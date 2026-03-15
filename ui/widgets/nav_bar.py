from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton


class NavBar(QFrame):
    """Bottom navigation bar with main actions."""

    navigate = pyqtSignal(str)  # emits screen name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navBar")
        self.setFixedHeight(70)

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 8, 20, 8)

        buttons = [
            ("Mirror", "mirror"),
            ("Hairstyles", "browser"),
            ("Book", "appointment"),
            ("History", "history"),
        ]

        for label, screen in buttons:
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, s=screen: self.navigate.emit(s))
            layout.addWidget(btn)
