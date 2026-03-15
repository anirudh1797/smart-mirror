from dataclasses import dataclass

import cv2
import numpy as np

from core.hair.generator import HairStyleGenerator
from core.hair.segmenter import HairSegmenter
from core.hardware.base import InferenceBackend
from db.models import Hairstyle


@dataclass
class HairPreviewResult:
    output_image: np.ndarray
    generation_time_ms: float
    success: bool
    error_message: str | None = None


class HairPreviewService:
    """Orchestrates hair segmentation, SD generation, and compositing."""

    def __init__(
        self,
        inference_backend: InferenceBackend,
        model_id: str,
        num_steps: int = 25,
    ):
        self._segmenter = HairSegmenter()
        self._generator = HairStyleGenerator(inference_backend, model_id, num_steps)

    def load_models(self) -> None:
        self._generator.load_model()

    def generate_preview(
        self,
        frame: np.ndarray,
        face_box: tuple[int, int, int, int],
        hairstyle: Hairstyle,
        strength: float = 0.75,
        progress_callback=None,
    ) -> HairPreviewResult:
        """Generate a hairstyle preview.

        1. Segment hair region to create mask
        2. Run SD inpainting
        3. Blend result with original frame
        """
        try:
            # Step 1: Generate hair mask
            mask = self._segmenter.segment(frame, face_box)

            # Step 2: Run SD inpainting
            result, gen_time = self._generator.generate(
                image=frame,
                mask=mask,
                prompt=hairstyle.sd_prompt,
                negative_prompt=hairstyle.sd_negative_prompt,
                strength=strength,
                progress_callback=progress_callback,
            )

            # Step 3: Blend — use the mask for smooth compositing
            mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
            frame_f = frame.astype(np.float32)
            result_f = result.astype(np.float32)
            blended = (result_f * mask_3ch + frame_f * (1 - mask_3ch)).astype(np.uint8)

            return HairPreviewResult(
                output_image=blended,
                generation_time_ms=gen_time,
                success=True,
            )

        except Exception as e:
            return HairPreviewResult(
                output_image=frame,
                generation_time_ms=0,
                success=False,
                error_message=str(e),
            )

    def unload_models(self) -> None:
        self._generator.unload_model()

    @property
    def is_loaded(self) -> bool:
        return self._generator.is_loaded
