import cv2
import numpy as np

from core.hardware.base import CameraBackend


class JetsonCamera(CameraBackend):
    """Camera backend for NVIDIA Jetson using GStreamer CSI pipeline."""

    def __init__(self):
        self._cap: cv2.VideoCapture | None = None
        self._width: int = 1280
        self._height: int = 720

    def _build_gstreamer_pipeline(self, source: int = 0) -> str:
        return (
            f"nvarguscamerasrc sensor-id={source} ! "
            f"video/x-raw(memory:NVMM), width={self._width}, height={self._height}, "
            f"framerate=30/1, format=NV12 ! "
            f"nvvidconv ! video/x-raw, format=BGRx ! "
            f"videoconvert ! video/x-raw, format=BGR ! "
            f"appsink drop=1"
        )

    def open(self, source: int | str = 0) -> None:
        sensor_id = int(source) if isinstance(source, str) else source
        pipeline = self._build_gstreamer_pipeline(sensor_id)
        self._cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"Failed to open Jetson CSI camera (sensor_id={sensor_id})"
            )

    def read_frame(self) -> tuple[bool, np.ndarray]:
        if self._cap is None:
            return False, np.array([])
        return self._cap.read()

    def get_resolution(self) -> tuple[int, int]:
        return (self._width, self._height)

    def set_resolution(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        # Resolution change requires re-opening with new GStreamer pipeline

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
