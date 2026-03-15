from datetime import date, time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.services.appointment_service import AppointmentService
from core.services.stylist_service import StylistService
from db.models import Hairstyle


class AppointmentScreen(QWidget):
    """Book an appointment form."""

    appointment_booked = pyqtSignal(int)  # emits appointment_id
    back_clicked = pyqtSignal()

    def __init__(
        self,
        appointment_service: AppointmentService,
        stylist_service: StylistService,
        parent=None,
    ):
        super().__init__(parent)
        self._appt_service = appointment_service
        self._stylist_service = stylist_service
        self._customer_id: int | None = None
        self._hairstyle: Hairstyle | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(back_btn)

        title = QLabel("Book Appointment")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        outer.addLayout(header)

        # Form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)

        panel = QFrame()
        panel.setObjectName("overlayPanel")
        panel.setMaximumWidth(500)
        form = QVBoxLayout(panel)
        form.setSpacing(12)
        form.setContentsMargins(30, 30, 30, 30)

        # Selected style display
        self._style_label = QLabel("No style selected")
        self._style_label.setStyleSheet("color: #B0B0B0; font-size: 14px;")
        form.addWidget(self._style_label)

        # Date
        form.addWidget(QLabel("Date"))
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(date.today())
        form.addWidget(self._date_edit)

        # Time
        form.addWidget(QLabel("Time"))
        self._time_edit = QTimeEdit()
        self._time_edit.setTime(time(10, 0))
        self._time_edit.setDisplayFormat("hh:mm AP")
        form.addWidget(self._time_edit)

        # Stylist
        form.addWidget(QLabel("Stylist"))
        self._stylist_combo = QComboBox()
        form.addWidget(self._stylist_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        book_btn = QPushButton("Confirm Booking")
        book_btn.setObjectName("primaryButton")
        book_btn.clicked.connect(self._on_book)
        btn_layout.addWidget(book_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.back_clicked.emit)
        btn_layout.addWidget(cancel_btn)
        form.addLayout(btn_layout)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
        self._error_label.setAlignment(Qt.AlignCenter)
        form.addWidget(self._error_label)

        self._success_label = QLabel("")
        self._success_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
        self._success_label.setAlignment(Qt.AlignCenter)
        form.addWidget(self._success_label)

        layout.addWidget(panel, alignment=Qt.AlignCenter)

    def _load_stylists(self) -> None:
        self._stylist_combo.clear()
        stylists = self._stylist_service.get_all_active()
        for s in stylists:
            self._stylist_combo.addItem(s.name, s.id)

    def _on_book(self) -> None:
        if self._customer_id is None:
            self._error_label.setText("No customer selected")
            return

        stylist_id = self._stylist_combo.currentData()
        appt_date = self._date_edit.date().toPyDate()
        appt_time = self._time_edit.time().toPyTime()

        try:
            appt = self._appt_service.create(
                customer_id=self._customer_id,
                appointment_date=appt_date,
                appointment_time=appt_time,
                stylist_id=stylist_id,
                hairstyle_id=self._hairstyle.id if self._hairstyle else None,
            )
            self._error_label.clear()
            self._success_label.setText(
                f"Appointment booked for {appt_date.strftime('%B %d')} "
                f"at {appt_time.strftime('%I:%M %p')}"
            )
            self.appointment_booked.emit(appt.id)
        except Exception as e:
            self._error_label.setText(str(e))

    def on_enter(self, context: dict) -> None:
        self._error_label.clear()
        self._success_label.clear()
        self._customer_id = context.get("customer_id")
        self._hairstyle = context.get("hairstyle")
        self._load_stylists()

        if self._hairstyle:
            self._style_label.setText(f"Style: {self._hairstyle.name}")
        else:
            self._style_label.setText("No style selected")
