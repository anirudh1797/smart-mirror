import time

import numpy as np
import torch
from PIL import Image

from core.hardware.base import InferenceBackend


class HairStyleGenerator:
    """Wraps the Stable Diffusion inpainting pipeline for hairstyle generation."""

    def __init__(self, inference_backend: InferenceBackend, model_id: str, num_steps: int = 25):
        self._backend = inference_backend
        self._model_id = model_id
        self._num_steps = num_steps
        self._pipeline = None

    def load_model(self) -> None:
        """Load the SD inpainting pipeline (lazy, called once)."""
        from diffusers import StableDiffusionInpaintPipeline

        device = self._backend.get_device()
        dtype = self._backend.get_torch_dtype()

        print(f"Loading SD inpainting model on {device} ({dtype})...")
        self._pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            self._model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        )
        self._pipeline = self._pipeline.to(device)

        # Optimize for speed and lower memory
        self._pipeline.enable_attention_slicing()

        print("SD model loaded successfully")

    def generate(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        prompt: str,
        negative_prompt: str | None = None,
        strength: float = 0.75,
        guidance_scale: float = 7.5,
        progress_callback=None,
    ) -> tuple[np.ndarray, float]:
        """Generate a hairstyle using inpainting.

        Args:
            image: BGR frame (any size, will be resized for SD)
            mask: Binary mask (255=inpaint region)
            prompt: SD prompt describing the hairstyle
            negative_prompt: Negative prompt
            strength: Denoising strength (0-1)
            guidance_scale: CFG scale
            progress_callback: Optional callable(step, total_steps)

        Returns:
            (result_bgr, generation_time_ms)
        """
        if self._pipeline is None:
            self.load_model()

        import cv2

        orig_h, orig_w = image.shape[:2]

        # Use 256x256 for speed on non-CUDA devices, 512x512 on CUDA
        gen_size = 512 if self._backend.get_device() == "cuda" else 256

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((gen_size, gen_size), Image.LANCZOS)
        mask_pil = Image.fromarray(mask).resize((gen_size, gen_size), Image.NEAREST)

        # Step callback for progress reporting
        def step_callback(pipeline, step, timestep, callback_kwargs):
            if progress_callback:
                progress_callback(step + 1, self._num_steps)
            return callback_kwargs

        start = time.time()

        with torch.no_grad():
            result = self._pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt or "blurry, deformed, cartoon, anime, unrealistic",
                image=img_pil,
                mask_image=mask_pil,
                height=gen_size,
                width=gen_size,
                num_inference_steps=self._num_steps,
                strength=strength,
                guidance_scale=guidance_scale,
                callback_on_step_end=step_callback,
            ).images[0]

        gen_time = (time.time() - start) * 1000

        # Convert back to BGR and resize to original
        result_rgb = np.array(result)
        result_bgr = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
        result_bgr = cv2.resize(result_bgr, (orig_w, orig_h), interpolation=cv2.INTER_LANCZOS4)

        return result_bgr, gen_time

    def unload_model(self) -> None:
        """Free GPU memory."""
        self._pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None
