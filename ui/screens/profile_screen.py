import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.face.face_service import FaceResult
from core.services.customer_service import CustomerService


class ProfileScreen(QWidget):
    """Create or edit customer profile form."""

    profile_saved = pyqtSignal(int)  # emits customer_id
    cancel_clicked = pyqtSignal()

    def __init__(self, customer_service: CustomerService, parent=None):
        super().__init__(parent)
        self._customer_service = customer_service
        self._face_encoding: np.ndarray | None = None
        self._editing_id: int | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        # Form panel
        panel = QFrame()
        panel.setObjectName("overlayPanel")
        panel.setMaximumWidth(500)
        form_layout = QVBoxLayout(panel)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Customer Profile")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Name
        form_layout.addWidget(QLabel("Name *"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Enter full name")
        form_layout.addWidget(self._name_input)

        # Phone
        form_layout.addWidget(QLabel("Phone"))
        self._phone_input = QLineEdit()
        self._phone_input.setPlaceholderText("Enter phone number")
        form_layout.addWidget(self._phone_input)

        # Email
        form_layout.addWidget(QLabel("Email"))
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Enter email address")
        form_layout.addWidget(self._email_input)

        # Gender
        form_layout.addWidget(QLabel("Gender *"))
        self._gender_combo = QComboBox()
        self._gender_combo.addItems(["male", "female", "other"])
        form_layout.addWidget(self._gender_combo)

        # Age Group
        form_layout.addWidget(QLabel("Age Group *"))
        self._age_combo = QComboBox()
        self._age_combo.addItems(["child", "teen", "adult", "senior"])
        self._age_combo.setCurrentText("adult")
        form_layout.addWidget(self._age_combo)

        # Notes
        form_layout.addWidget(QLabel("Notes"))
        self._notes_input = QLineEdit()
        self._notes_input.setPlaceholderText("Stylist notes or preferences")
        form_layout.addWidget(self._notes_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        save_btn = QPushButton("Save Profile")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(cancel_btn)

        form_layout.addLayout(btn_layout)

        # Error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
        self._error_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self._error_label)

        layout.addWidget(panel, alignment=Qt.AlignCenter)

    def _clear_form(self) -> None:
        self._name_input.clear()
        self._phone_input.clear()
        self._email_input.clear()
        self._gender_combo.setCurrentIndex(0)
        self._age_combo.setCurrentText("adult")
        self._notes_input.clear()
        self._error_label.clear()
        self._face_encoding = None
        self._editing_id = None

    def _on_save(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            self._error_label.setText("Name is required")
            return

        try:
            if self._editing_id is not None:
                customer = self._customer_service.update(
                    self._editing_id,
                    name=name,
                    phone=self._phone_input.text().strip() or None,
                    email=self._email_input.text().strip() or None,
                    gender=self._gender_combo.currentText(),
                    age_group=self._age_combo.currentText(),
                    notes=self._notes_input.text().strip() or None,
                )
                if customer:
                    self.profile_saved.emit(customer.id)
            else:
                customer = self._customer_service.create(
                    name=name,
                    phone=self._phone_input.text().strip() or None,
                    email=self._email_input.text().strip() or None,
                    gender=self._gender_combo.currentText(),
                    age_group=self._age_combo.currentText(),
                    notes=self._notes_input.text().strip() or None,
                    face_encoding=self._face_encoding,
                )
                self.profile_saved.emit(customer.id)
        except Exception as e:
            self._error_label.setText(str(e))

    def _on_cancel(self) -> None:
        self._clear_form()
        self.cancel_clicked.emit()

    def on_enter(self, context: dict) -> None:
        self._clear_form()
        face = context.get("face")
        if face and isinstance(face, FaceResult):
            self._face_encoding = face.encoding

        customer_id = context.get("customer_id")
        if customer_id:
            self._editing_id = customer_id
            customer = self._customer_service.get_by_id(customer_id)
            if customer:
                self._name_input.setText(customer.name)
                self._phone_input.setText(customer.phone or "")
                self._email_input.setText(customer.email or "")
                self._gender_combo.setCurrentText(customer.gender)
                self._age_combo.setCurrentText(customer.age_group)
                self._notes_input.setText(customer.notes or "")
