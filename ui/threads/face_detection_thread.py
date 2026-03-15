import numpy as np
from PyQt5.QtCore import QMutex, QThread, pyqtSignal

from core.face.face_service import FaceResult, FaceService


class FaceDetectionThread(QThread):
    """Worker thread that runs face detection on frames at ~5 FPS."""

    faces_detected = pyqtSignal(list)  # list[FaceResult]

    def __init__(self, face_service: FaceService, parent=None):
        super().__init__(parent)
        self._face_service = face_service
        self._running = False
        self._latest_frame: np.ndarray | None = None
        self._mutex = QMutex()

    def submit_frame(self, frame: np.ndarray) -> None:
        """Submit a frame for processing (non-blocking, drops old frames)."""
        self._mutex.lock()
        self._latest_frame = frame.copy()
        self._mutex.unlock()

    def run(self) -> None:
        self._running = True
        frame_count = 0

        while self._running:
            self._mutex.lock()
            frame = self._latest_frame
            self._latest_frame = None
            self._mutex.unlock()

            if frame is not None:
                results = self._face_service.process_frame(frame)
                self.faces_detected.emit(results)

            self.msleep(200)  # ~5 FPS

    def stop(self) -> None:
        self._running = False
        self.wait()
