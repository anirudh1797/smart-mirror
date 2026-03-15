from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.services.appointment_service import AppointmentService


class HistoryScreen(QWidget):
    """View appointment history for a customer."""

    back_clicked = pyqtSignal()

    def __init__(self, appointment_service: AppointmentService, parent=None):
        super().__init__(parent)
        self._appt_service = appointment_service
        self._customer_id: int | None = None
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

        title = QLabel("Appointment History")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setAlignment(Qt.AlignTop)
        self._list_layout.setSpacing(8)
        scroll.setWidget(self._list_container)
        layout.addWidget(scroll)

    def _load_history(self) -> None:
        # Clear existing items
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self._customer_id is None:
            return

        appointments = self._appt_service.get_by_customer(self._customer_id)

        if not appointments:
            empty = QLabel("No appointments yet")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
            self._list_layout.addWidget(empty)
            return

        for appt in appointments:
            card = QFrame()
            card.setObjectName("overlayPanel")
            card.setMaximumHeight(100)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)

            # Date & time
            date_str = appt.appointment_date.strftime("%b %d, %Y")
            time_str = appt.appointment_time.strftime("%I:%M %p")
            date_label = QLabel(f"{date_str}\n{time_str}")
            date_label.setStyleSheet("font-size: 14px; color: #E0E0E0;")
            date_label.setFixedWidth(120)
            card_layout.addWidget(date_label)

            # Status badge
            status_colors = {
                "booked": "#4285F4",
                "confirmed": "#34A853",
                "in_progress": "#FBBC04",
                "completed": "#0F9D58",
                "cancelled": "#EA4335",
            }
            color = status_colors.get(appt.status, "#888")
            status_label = QLabel(appt.status.upper())
            status_label.setFixedWidth(100)
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: bold; "
                f"border: 1px solid {color}; border-radius: 4px; padding: 4px;"
            )
            card_layout.addWidget(status_label)

            card_layout.addStretch()
            self._list_layout.addWidget(card)

    def on_enter(self, context: dict) -> None:
        self._customer_id = context.get("customer_id")
        self._load_history()
