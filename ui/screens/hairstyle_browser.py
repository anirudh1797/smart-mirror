from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.hair.catalog import HairstyleCatalog
from db.models import Hairstyle
from ui.widgets.hairstyle_card import HairstyleCard


class HairstyleBrowserScreen(QWidget):
    """Browse hairstyle catalog with filters."""

    hairstyle_selected = pyqtSignal(object)  # emits Hairstyle
    back_clicked = pyqtSignal()

    def __init__(self, catalog: HairstyleCatalog, parent=None):
        super().__init__(parent)
        self._catalog = catalog
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

        title = QLabel("Choose a Hairstyle")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Filters
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "QFrame { background-color: rgba(255,255,255,0.05); "
            "border-radius: 8px; padding: 8px; }"
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(12)

        filter_layout.addWidget(QLabel("Gender:"))
        self._gender_filter = QComboBox()
        self._gender_filter.addItems(["All", "male", "female", "other"])
        self._gender_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self._gender_filter)

        filter_layout.addWidget(QLabel("Length:"))
        self._length_filter = QComboBox()
        self._length_filter.addItems(["All", "short", "medium", "long"])
        self._length_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self._length_filter)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Scrollable grid of hairstyle cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self._grid_container)
        layout.addWidget(scroll)

    def _apply_filters(self) -> None:
        gender = self._gender_filter.currentText()
        length = self._length_filter.currentText()

        hairstyles = self._catalog.get_hairstyles(
            gender=gender if gender != "All" else None,
            length=length if length != "All" else None,
        )
        self._populate_grid(hairstyles)

    def _populate_grid(self, hairstyles: list[Hairstyle]) -> None:
        # Clear existing cards
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not hairstyles:
            empty_label = QLabel("No hairstyles found")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
            self._grid_layout.addWidget(empty_label, 0, 0)
            return

        cols = 4
        for i, hairstyle in enumerate(hairstyles):
            card = HairstyleCard(hairstyle)
            card.clicked.connect(self.hairstyle_selected.emit)
            self._grid_layout.addWidget(card, i // cols, i % cols)

    def on_enter(self, context: dict) -> None:
        # Set gender filter if customer gender is known
        customer_gender = context.get("gender")
        if customer_gender and customer_gender in ["male", "female", "other"]:
            self._gender_filter.setCurrentText(customer_gender)
        else:
            self._gender_filter.setCurrentText("All")
        self._apply_filters()
