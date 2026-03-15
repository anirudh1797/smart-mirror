import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.face.face_service import FaceResult
from ui.widgets.camera_widget import CameraWidget


class RecognitionScreen(QWidget):
    """Shows welcome-back or new-face-detected overlay."""

    create_profile_clicked = pyqtSignal(object)  # emits FaceResult
    continue_clicked = pyqtSignal(int)  # emits customer_id
    skip_clicked = pyqtSignal()  # go back to mirror

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_face: FaceResult | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Camera feed background
        self.camera_widget = CameraWidget(self)
        layout.addWidget(self.camera_widget)

        # Overlay panel (centered)
        self._panel = QFrame(self)
        self._panel.setObjectName("overlayPanel")
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setSpacing(16)
        panel_layout.setContentsMargins(40, 30, 40, 30)

        self._title_label = QLabel("", self._panel)
        self._title_label.setObjectName("titleLabel")
        self._title_label.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self._title_label)

        self._subtitle_label = QLabel("", self._panel)
        self._subtitle_label.setObjectName("subtitleLabel")
        self._subtitle_label.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self._subtitle_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._primary_btn = QPushButton("Continue")
        self._primary_btn.setObjectName("primaryButton")
        self._primary_btn.clicked.connect(self._on_primary_click)
        btn_layout.addWidget(self._primary_btn)

        self._secondary_btn = QPushButton("Not Me")
        self._secondary_btn.clicked.connect(self._on_secondary_click)
        btn_layout.addWidget(self._secondary_btn)

        panel_layout.addLayout(btn_layout)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        pw, ph = 400, 220
        x = (self.width() - pw) // 2
        y = (self.height() - ph) // 2
        self._panel.setGeometry(x, y, pw, ph)

    def update_frame(self, frame: np.ndarray) -> None:
        self.camera_widget.update_frame(frame)

    def show_known_face(self, face: FaceResult) -> None:
        """Configure for a recognized customer."""
        self._current_face = face
        self._title_label.setText(f"Welcome back, {face.customer_name}!")
        self._subtitle_label.setText("Ready to try new styles?")
        self._primary_btn.setText("Continue")
        self._secondary_btn.setText("Not Me")
        self._secondary_btn.show()

    def show_unknown_face(self, face: FaceResult) -> None:
        """Configure for an unrecognized face."""
        self._current_face = face
        self._title_label.setText("New Face Detected!")
        self._subtitle_label.setText("Create a profile to get started")
        self._primary_btn.setText("Create Profile")
        self._secondary_btn.setText("Skip")
        self._secondary_btn.show()

    def _on_primary_click(self) -> None:
        if self._current_face is None:
            return
        if self._current_face.customer_id is not None:
            self.continue_clicked.emit(self._current_face.customer_id)
        else:
            self.create_profile_clicked.emit(self._current_face)

    def _on_secondary_click(self) -> None:
        self.skip_clicked.emit()

    def on_enter(self, context: dict) -> None:
        face = context.get("face")
        if face and isinstance(face, FaceResult):
            if face.customer_id is not None:
                self.show_known_face(face)
            else:
                self.show_unknown_face(face)
