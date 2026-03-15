import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from core.hair.preview_service import HairPreviewResult, HairPreviewService
from db.models import Hairstyle


class HairGenerationThread(QThread):
    """Worker thread that runs SD inpainting off the UI thread."""

    preview_ready = pyqtSignal(object)  # emits HairPreviewResult
    model_loaded = pyqtSignal()
    status_update = pyqtSignal(str)

    def __init__(self, preview_service: HairPreviewService, parent=None):
        super().__init__(parent)
        self._service = preview_service
        self._frame: np.ndarray | None = None
        self._face_box: tuple[int, int, int, int] | None = None
        self._hairstyle: Hairstyle | None = None
        self._should_generate = False
        self._should_load = False
        self._running = False

    def request_load_model(self) -> None:
        """Request model loading (called from UI thread)."""
        self._should_load = True

    def request_preview(
        self,
        frame: np.ndarray,
        face_box: tuple[int, int, int, int],
        hairstyle: Hairstyle,
    ) -> None:
        """Request a hairstyle preview generation (called from UI thread)."""
        self._frame = frame.copy()
        self._face_box = face_box
        self._hairstyle = hairstyle
        self._should_generate = True

    def run(self) -> None:
        self._running = True

        while self._running:
            if self._should_load:
                self._should_load = False
                self.status_update.emit("Loading AI model...")
                try:
                    self._service.load_models()
                    self.model_loaded.emit()
                    self.status_update.emit("AI model ready")
                except Exception as e:
                    self.status_update.emit(f"Model load failed: {e}")

            if self._should_generate and self._frame is not None:
                self._should_generate = False
                self.status_update.emit("Generating hairstyle preview...")

                def on_progress(step, total):
                    self.status_update.emit(f"Generating... step {step}/{total}")

                result = self._service.generate_preview(
                    frame=self._frame,
                    face_box=self._face_box,
                    hairstyle=self._hairstyle,
                    progress_callback=on_progress,
                )
                self.preview_ready.emit(result)

                if result.success:
                    self.status_update.emit(
                        f"Preview generated in {result.generation_time_ms:.0f}ms"
                    )
                else:
                    self.status_update.emit(f"Generation failed: {result.error_message}")

            self.msleep(100)

    def stop(self) -> None:
        self._running = False
        self.wait()
