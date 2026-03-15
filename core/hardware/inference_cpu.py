import torch

from core.hardware.base import InferenceBackend


class CPUInferenceBackend(InferenceBackend):
    """Inference backend for CPU and Apple Silicon MPS."""

    def get_device(self) -> str:
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def is_gpu_available(self) -> bool:
        return torch.backends.mps.is_available()

    def get_torch_dtype(self):
        return torch.float32
