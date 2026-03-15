import torch

from core.hardware.base import InferenceBackend


class CUDAInferenceBackend(InferenceBackend):
    """Inference backend for NVIDIA CUDA GPUs (Jetson Orin Nano)."""

    def get_device(self) -> str:
        return "cuda"

    def is_gpu_available(self) -> bool:
        return torch.cuda.is_available()

    def get_torch_dtype(self):
        return torch.float16
