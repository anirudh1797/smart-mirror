import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from core.hardware.base import CameraBackend


class CameraThread(QThread):
    """Worker thread that reads camera frames and emits them as signals."""

    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera: CameraBackend, parent=None):
        super().__init__(parent)
        self._camera = camera
        self._running = False

    def run(self) -> None:
        self._running = True
        while self._running:
            success, frame = self._camera.read_frame()
            if success:
                self.frame_ready.emit(frame)
            else:
                self.msleep(100)  # Wait before retrying on failure
            self.msleep(33)  # ~30 FPS

    def stop(self) -> None:
        self._running = False
        self.wait()
