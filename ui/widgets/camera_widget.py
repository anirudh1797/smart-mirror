import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy


class CameraWidget(QLabel):
    """Widget that displays live camera frames, scaled to fill the widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #000000;")
        self.setText("Camera loading...")

    def update_frame(self, frame: np.ndarray) -> None:
        """Convert a BGR numpy frame to QPixmap and display it."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qt_image)

        # Scale to fill widget while keeping aspect ratio
        scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)
