from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

from db.models import Hairstyle

# Style type icons and colors
_STYLE_ICONS = {
    "fade": ("FADE", "#4285F4"),
    "crop": ("CROP", "#34A853"),
    "pompadour": ("POMP", "#FBBC04"),
    "buzz": ("BUZZ", "#EA4335"),
    "quiff": ("QUIFF", "#9C27B0"),
    "side_part": ("SIDE", "#00BCD4"),
    "undercut": ("UNDR", "#FF5722"),
    "pixie": ("PIXIE", "#E91E63"),
    "bob": ("BOB", "#9C27B0"),
    "lob": ("LOB", "#673AB7"),
    "waves": ("WAVE", "#2196F3"),
    "straight": ("STR8", "#4CAF50"),
    "curly": ("CURL", "#FF9800"),
    "braids": ("BRAID", "#795548"),
    "bangs": ("BANG", "#607D8B"),
    "crew": ("CREW", "#3F51B5"),
    "mohawk": ("HAWK", "#F44336"),
    "pigtails": ("PGTL", "#FF4081"),
}


def _create_placeholder_pixmap(hairstyle: Hairstyle, width: int, height: int) -> QPixmap:
    """Create a styled placeholder thumbnail for a hairstyle."""
    pixmap = QPixmap(width, height)

    icon_text, color = _STYLE_ICONS.get(
        hairstyle.style_type, (hairstyle.style_type[:4].upper(), "#666")
    )

    bg_color = QColor(color)
    bg_color.setAlpha(40)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Background
    painter.fillRect(0, 0, width, height, QColor(30, 30, 30))

    # Colored accent bar at top
    accent = QColor(color)
    painter.fillRect(0, 0, width, 4, accent)

    # Style type label
    accent.setAlpha(180)
    painter.setPen(accent)
    font = QFont("Helvetica Neue", 20, QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 10, width, 50, Qt.AlignCenter, icon_text)

    # Gender indicator
    gender_map = {"male": "Men", "female": "Women", "other": "Kids"}
    gender_text = gender_map.get(hairstyle.gender, "")
    painter.setPen(QColor(150, 150, 150))
    font.setPointSize(10)
    font.setWeight(QFont.Normal)
    painter.setFont(font)
    painter.drawText(0, 55, width, 25, Qt.AlignCenter, gender_text)

    # Length bar
    lengths = {"short": 0.3, "medium": 0.6, "long": 0.9}
    bar_fill = lengths.get(hairstyle.length, 0.5)
    bar_y = 90
    bar_w = width - 20
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(50, 50, 50))
    painter.drawRoundedRect(10, bar_y, bar_w, 8, 4, 4)
    painter.setBrush(QColor(color))
    painter.drawRoundedRect(10, bar_y, int(bar_w * bar_fill), 8, 4, 4)

    # Length label
    painter.setPen(QColor(120, 120, 120))
    font.setPointSize(9)
    painter.setFont(font)
    painter.drawText(0, bar_y + 10, width, 20, Qt.AlignCenter, hairstyle.length)

    painter.end()
    return pixmap


class HairstyleCard(QFrame):
    """Clickable card widget displaying a hairstyle."""

    clicked = pyqtSignal(object)  # emits Hairstyle

    def __init__(self, hairstyle: Hairstyle, parent=None):
        super().__init__(parent)
        self._hairstyle = hairstyle
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(160, 200)
        self.setStyleSheet(
            "QFrame { background-color: rgba(255,255,255,0.08); "
            "border-radius: 10px; border: 1px solid rgba(255,255,255,0.15); }"
            "QFrame:hover { background-color: rgba(255,255,255,0.15); "
            "border: 1px solid rgba(66,133,244,0.6); }"
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(140, 120)
        thumb.setAlignment(Qt.AlignCenter)

        img_path = Path(self._hairstyle.reference_image_path)
        if img_path.exists():
            pixmap = QPixmap(str(img_path)).scaled(
                140, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            pixmap = _create_placeholder_pixmap(self._hairstyle, 140, 120)

        thumb.setPixmap(pixmap)
        layout.addWidget(thumb)

        # Name
        name = QLabel(self._hairstyle.name)
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("font-size: 13px; color: #E0E0E0; font-weight: bold;")
        layout.addWidget(name)

        # Style info
        info = QLabel(f"{self._hairstyle.length} | {self._hairstyle.style_type}")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._hairstyle)
