from abc import ABC, abstractmethod

import numpy as np


class CameraBackend(ABC):
    """Abstract interface for camera hardware."""

    @abstractmethod
    def open(self, source: int | str = 0) -> None:
        """Open the camera device."""
        ...

    @abstractmethod
    def read_frame(self) -> tuple[bool, np.ndarray]:
        """Read a single frame. Returns (success, frame_bgr)."""
        ...

    @abstractmethod
    def get_resolution(self) -> tuple[int, int]:
        """Return (width, height) of the camera."""
        ...

    @abstractmethod
    def set_resolution(self, width: int, height: int) -> None:
        """Set the camera resolution."""
        ...

    @abstractmethod
    def release(self) -> None:
        """Release the camera device."""
        ...


class InferenceBackend(ABC):
    """Abstract interface for AI inference hardware."""

    @abstractmethod
    def get_device(self) -> str:
        """Return device string: 'cpu', 'cuda', or 'mps'."""
        ...

    @abstractmethod
    def is_gpu_available(self) -> bool:
        """Check if GPU acceleration is available."""
        ...

    @abstractmethod
    def get_torch_dtype(self):
        """Return the optimal torch dtype for this backend."""
        ...
