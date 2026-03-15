import sys
from pathlib import Path
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget


class SmartMirrorApp:
    """Main application class. Manages screens via QStackedWidget."""

    def __init__(self, fullscreen: bool = False):
        self.app = QApplication(sys.argv)
        self._load_stylesheet()

        self.window = QMainWindow()
        self.window.setWindowTitle("Smart Mirror")
        self.window.setMinimumSize(800, 600)

        self.stack = QStackedWidget()
        self.window.setCentralWidget(self.stack)

        self._screens: dict[str, QWidget] = {}
        self._fullscreen = fullscreen

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).resolve().parent.parent / "assets" / "styles" / "mirror_dark.qss"
        if qss_path.exists():
            self.app.setStyleSheet(qss_path.read_text())

    def register_screen(self, name: str, screen: QWidget) -> None:
        """Register a screen widget by name."""
        self._screens[name] = screen
        self.stack.addWidget(screen)

    def navigate_to(self, name: str, context: dict[str, Any] | None = None) -> None:
        """Switch to a named screen, optionally passing context data."""
        screen = self._screens.get(name)
        if screen is None:
            raise ValueError(f"Unknown screen: {name}")

        if hasattr(screen, "on_enter") and callable(screen.on_enter):
            screen.on_enter(context or {})

        self.stack.setCurrentWidget(screen)

    def current_screen_name(self) -> str | None:
        """Return the name of the currently visible screen."""
        current = self.stack.currentWidget()
        for name, screen in self._screens.items():
            if screen is current:
                return name
        return None

    def run(self) -> int:
        """Start the application event loop."""
        if self._fullscreen:
            self.window.showFullScreen()
        else:
            self.window.show()
        return self.app.exec_()
