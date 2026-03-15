import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.camera_widget import CameraWidget


class MainMenuScreen(QWidget):
    """Main menu with action buttons, shown after face recognition."""

    try_hairstyles_clicked = pyqtSignal()
    book_appointment_clicked = pyqtSignal()
    view_history_clicked = pyqtSignal()
    edit_profile_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._customer_name: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Camera background
        self.camera_widget = CameraWidget(self)
        layout.addWidget(self.camera_widget)

        # Overlay panel (centered)
        self._panel = QFrame(self)
        self._panel.setObjectName("overlayPanel")
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setSpacing(14)
        panel_layout.setContentsMargins(40, 30, 40, 30)

        self._welcome_label = QLabel("Welcome!")
        self._welcome_label.setObjectName("titleLabel")
        self._welcome_label.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self._welcome_label)

        # Menu buttons
        btn_data = [
            ("Try Hairstyles", self.try_hairstyles_clicked, "primaryButton"),
            ("Book Appointment", self.book_appointment_clicked, None),
            ("My History", self.view_history_clicked, None),
            ("Edit Profile", self.edit_profile_clicked, None),
        ]

        for text, signal, obj_name in btn_data:
            btn = QPushButton(text)
            if obj_name:
                btn.setObjectName(obj_name)
            btn.setMinimumHeight(50)
            btn.clicked.connect(signal.emit)
            panel_layout.addWidget(btn)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        pw, ph = 350, 340
        x = (self.width() - pw) // 2
        y = (self.height() - ph) // 2
        self._panel.setGeometry(x, y, pw, ph)

    def update_frame(self, frame: np.ndarray) -> None:
        self.camera_widget.update_frame(frame)

    def on_enter(self, context: dict) -> None:
        name = context.get("customer_name", "")
        if name:
            self._welcome_label.setText(f"Welcome, {name}!")
        else:
            self._welcome_label.setText("Welcome!")
