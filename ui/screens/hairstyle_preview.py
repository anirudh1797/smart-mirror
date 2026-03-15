import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.hair.preview_service import HairPreviewResult
from db.models import Hairstyle


class HairstylePreviewScreen(QWidget):
    """AR preview screen — shows the generated hairstyle on the user's photo."""

    back_clicked = pyqtSignal()
    book_clicked = pyqtSignal(object)  # emits Hairstyle
    try_another_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_hairstyle: Hairstyle | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(back_btn)

        self._title_label = QLabel("Hairstyle Preview")
        self._title_label.setObjectName("titleLabel")
        header.addWidget(self._title_label)
        header.addStretch()
        layout.addLayout(header)

        # Preview area
        preview_layout = QHBoxLayout()

        # Left: Original photo
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Original"))
        self._original_label = QLabel()
        self._original_label.setFixedSize(400, 400)
        self._original_label.setAlignment(Qt.AlignCenter)
        self._original_label.setStyleSheet(
            "background-color: rgba(255,255,255,0.05); border-radius: 8px;"
        )
        left_panel.addWidget(self._original_label)
        preview_layout.addLayout(left_panel)

        # Right: Generated preview
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Preview"))
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(400, 400)
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setStyleSheet(
            "background-color: rgba(255,255,255,0.05); border-radius: 8px;"
        )
        right_panel.addWidget(self._preview_label)
        preview_layout.addLayout(right_panel)

        layout.addLayout(preview_layout)

        # Status label
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet("color: #B0B0B0; font-size: 14px;")
        layout.addWidget(self._status_label)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        try_btn = QPushButton("Try Another Style")
        try_btn.clicked.connect(self.try_another_clicked.emit)
        btn_layout.addWidget(try_btn)

        book_btn = QPushButton("Book This Style")
        book_btn.setObjectName("primaryButton")
        book_btn.clicked.connect(self._on_book)
        btn_layout.addWidget(book_btn)

        layout.addLayout(btn_layout)

    @staticmethod
    def _frame_to_pixmap(frame_bgr: np.ndarray, size: int = 400) -> QPixmap:
        """Convert a BGR numpy frame to a QPixmap, safely copying data."""
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()  # .copy() owns the data
        return QPixmap.fromImage(img).scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def set_original_frame(self, frame: np.ndarray) -> None:
        """Display the original captured frame."""
        pixmap = self._frame_to_pixmap(frame)
        self._original_label.setPixmap(pixmap)

    def set_preview_result(self, result: HairPreviewResult) -> None:
        """Display the generated hairstyle preview."""
        if result.success:
            pixmap = self._frame_to_pixmap(result.output_image)
            self._preview_label.setPixmap(pixmap)
            self._status_label.setText(
                f"Generated in {result.generation_time_ms:.0f}ms"
            )
        else:
            self._preview_label.setText("Generation failed")
            self._status_label.setText(result.error_message or "Unknown error")

    def set_loading(self, message: str = "Generating preview...") -> None:
        """Show loading state."""
        self._preview_label.setText(message)
        self._preview_label.setStyleSheet(
            "background-color: rgba(255,255,255,0.05); border-radius: 8px; "
            "color: #B0B0B0; font-size: 16px;"
        )
        self._status_label.setText(message)

    def set_hairstyle(self, hairstyle: Hairstyle) -> None:
        self._current_hairstyle = hairstyle
        self._title_label.setText(f"Preview: {hairstyle.name}")

    def _on_book(self) -> None:
        if self._current_hairstyle:
            self.book_clicked.emit(self._current_hairstyle)

    def on_enter(self, context: dict) -> None:
        hairstyle = context.get("hairstyle")
        if hairstyle:
            self.set_hairstyle(hairstyle)
        self._preview_label.clear()
        self._status_label.clear()
