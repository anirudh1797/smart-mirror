import cv2
import numpy as np

from core.hardware.base import CameraBackend


class DesktopCamera(CameraBackend):
    """Camera backend for desktop webcams using OpenCV VideoCapture."""

    def __init__(self):
        self._cap: cv2.VideoCapture | None = None

    def open(self, source: int | str = 0) -> None:
        self._cap = cv2.VideoCapture(source)
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open camera source: {source}")

    def read_frame(self) -> tuple[bool, np.ndarray]:
        if self._cap is None:
            return False, np.array([])
        return self._cap.read()

    def get_resolution(self) -> tuple[int, int]:
        if self._cap is None:
            return (0, 0)
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (w, h)

    def set_resolution(self, width: int, height: int) -> None:
        if self._cap is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
