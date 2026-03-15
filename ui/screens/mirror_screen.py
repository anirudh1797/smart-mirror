from datetime import datetime

import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.widgets.camera_widget import CameraWidget


class MirrorScreen(QWidget):
    """Main idle screen: live camera feed with clock overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._start_clock()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Camera feed (background)
        self.camera_widget = CameraWidget(self)
        layout.addWidget(self.camera_widget)

        # Clock overlay (top-right)
        self._clock_label = QLabel(self)
        self._clock_label.setObjectName("clockLabel")
        self._clock_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self._clock_label.setStyleSheet(
            "font-size: 48px; font-weight: 300; color: #FFFFFF; "
            "background-color: transparent; padding: 20px;"
        )

        # Date overlay (below clock)
        self._date_label = QLabel(self)
        self._date_label.setObjectName("dateLabel")
        self._date_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self._date_label.setStyleSheet(
            "font-size: 20px; color: #B0B0B0; "
            "background-color: transparent; padding: 0px 20px;"
        )

        # Status label (bottom center)
        self._status_label = QLabel("Stand in front of the mirror to begin", self)
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(
            "font-size: 18px; color: rgba(255, 255, 255, 0.6); "
            "background-color: transparent; padding: 20px;"
        )

    def resizeEvent(self, event) -> None:
        """Reposition overlay labels on resize."""
        super().resizeEvent(event)
        w = self.width()

        # Clock in top-right
        self._clock_label.setGeometry(w - 300, 20, 280, 60)
        self._date_label.setGeometry(w - 300, 75, 280, 30)

        # Status at bottom center
        self._status_label.setGeometry(0, self.height() - 60, w, 40)

    def _start_clock(self) -> None:
        self._update_clock()
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

    def _update_clock(self) -> None:
        now = datetime.now()
        self._clock_label.setText(now.strftime("%H:%M"))
        self._date_label.setText(now.strftime("%A, %B %d"))

    def update_frame(self, frame: np.ndarray) -> None:
        """Forward camera frame to the camera widget."""
        self.camera_widget.update_frame(frame)

    def show_camera_error(self, message: str) -> None:
        """Show an error message when camera is unavailable."""
        self.camera_widget.setText(message)
        self.camera_widget.setAlignment(Qt.AlignCenter)
        self.camera_widget.setStyleSheet(
            "font-size: 20px; color: #FF6B6B; background-color: #000000; padding: 40px;"
        )

    def on_enter(self, context: dict) -> None:
        """Called when navigating to this screen."""
        pass
