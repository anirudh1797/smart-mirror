import sys
import time
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from config import load_config
from core.face.face_service import FaceResult, FaceService
from core.hair.catalog import HairstyleCatalog
from core.hair.preview_service import HairPreviewService
from core.hardware.camera_factory import create_camera
from core.hardware.inference_factory import create_inference_backend
from core.services.appointment_service import AppointmentService
from core.services.customer_service import CustomerService
from core.services.stylist_service import StylistService
from db.engine import init_db
from db.seed import seed_hairstyles
from ui.app import SmartMirrorApp
from ui.screens.appointment_screen import AppointmentScreen
from ui.screens.hairstyle_browser import HairstyleBrowserScreen
from ui.screens.hairstyle_preview import HairstylePreviewScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.main_menu_screen import MainMenuScreen
from ui.screens.mirror_screen import MirrorScreen
from ui.screens.profile_screen import ProfileScreen
from ui.screens.recognition_screen import RecognitionScreen
from ui.threads.camera_thread import CameraThread
from ui.threads.face_detection_thread import FaceDetectionThread
from ui.threads.hair_generation_thread import HairGenerationThread
from ui.widgets.face_overlay_widget import draw_face_overlays


class SmartMirrorController:
    """Wires all components together and handles navigation logic."""

    def __init__(self):
        self.config = load_config()

        # Initialize database and seed data
        init_db(self.config.db_path)
        seed_hairstyles()

        # Services
        self.customer_service = CustomerService()
        self.appointment_service = AppointmentService()
        self.stylist_service = StylistService()
        self.stylist_service.seed_default()
        self.catalog = HairstyleCatalog()

        # Face service
        self.face_service = FaceService(
            model=self.config.face_detection_model,
            tolerance=self.config.face_tolerance,
        )
        self._load_known_faces()

        # Inference backend for AI hair preview
        self.inference_backend = create_inference_backend(self.config.platform)
        self.preview_service = HairPreviewService(
            inference_backend=self.inference_backend,
            model_id=self.config.sd_model_id,
            num_steps=self.config.sd_num_inference_steps,
        )

        # Current state
        self._current_customer_id: int | None = None
        self._current_customer_name: str | None = None
        self._current_customer_gender: str | None = None
        self._latest_frame: np.ndarray | None = None
        self._latest_faces: list[FaceResult] = []
        self._frame_count = 0
        self._last_nav_time: float = 0  # cooldown to prevent rapid navigation
        self._nav_cooldown_seconds: float = 3.0  # wait 3s between auto-navigations

    def _load_known_faces(self) -> None:
        customers = self.customer_service.get_all_with_faces()
        self.face_service.load_known_faces(customers)
        print(f"Loaded {self.face_service.known_face_count} known faces")

    def setup(self) -> int:
        """Create all UI components and start the app."""
        # App
        self.app = SmartMirrorApp(fullscreen=self.config.fullscreen)

        # Screens
        self.mirror_screen = MirrorScreen()
        self.recognition_screen = RecognitionScreen()
        self.profile_screen = ProfileScreen(self.customer_service)
        self.main_menu_screen = MainMenuScreen()
        self.browser_screen = HairstyleBrowserScreen(self.catalog)
        self.preview_screen = HairstylePreviewScreen()
        self.appointment_screen = AppointmentScreen(
            self.appointment_service, self.stylist_service
        )
        self.history_screen = HistoryScreen(self.appointment_service)

        # Register screens
        for name, screen in [
            ("mirror", self.mirror_screen),
            ("recognition", self.recognition_screen),
            ("profile", self.profile_screen),
            ("menu", self.main_menu_screen),
            ("browser", self.browser_screen),
            ("preview", self.preview_screen),
            ("appointment", self.appointment_screen),
            ("history", self.history_screen),
        ]:
            self.app.register_screen(name, screen)

        # Connect signals
        self._connect_signals()

        # Camera
        self.camera = create_camera(self.config.platform)
        self.camera_thread = None
        self.face_thread = None
        self.hair_thread = None

        try:
            self.camera.open(self.config.camera_source)
            self.camera.set_resolution(*self.config.camera_resolution)

            self.camera_thread = CameraThread(self.camera)
            self.camera_thread.frame_ready.connect(self._on_frame)
            self.camera_thread.start()

            self.face_thread = FaceDetectionThread(self.face_service)
            self.face_thread.faces_detected.connect(self._on_faces_detected)
            self.face_thread.start()

            self.hair_thread = HairGenerationThread(self.preview_service)
            self.hair_thread.preview_ready.connect(self._on_preview_ready)
            self.hair_thread.status_update.connect(self._on_hair_status)
            self.hair_thread.start()

        except RuntimeError as e:
            print(f"Camera unavailable: {e}")
            self.mirror_screen.show_camera_error(
                "Camera unavailable.\n\n"
                "Grant permission in:\n"
                "System Settings > Privacy & Security > Camera"
            )

        self.app.navigate_to("mirror")
        exit_code = self.app.run()

        # Cleanup
        if self.camera_thread:
            self.camera_thread.stop()
        if self.face_thread:
            self.face_thread.stop()
        if self.hair_thread:
            self.hair_thread.stop()
        self.camera.release()

        return exit_code

    def _connect_signals(self) -> None:
        # Recognition screen
        self.recognition_screen.continue_clicked.connect(self._on_continue_as_customer)
        self.recognition_screen.create_profile_clicked.connect(self._on_create_profile)
        self.recognition_screen.skip_clicked.connect(self._go_to_mirror)

        # Profile screen
        self.profile_screen.profile_saved.connect(self._on_profile_saved)
        self.profile_screen.cancel_clicked.connect(self._go_to_mirror)

        # Main menu
        self.main_menu_screen.try_hairstyles_clicked.connect(self._go_to_browser)
        self.main_menu_screen.book_appointment_clicked.connect(self._go_to_appointment)
        self.main_menu_screen.view_history_clicked.connect(self._go_to_history)
        self.main_menu_screen.edit_profile_clicked.connect(self._go_to_edit_profile)

        # Browser
        self.browser_screen.hairstyle_selected.connect(self._on_hairstyle_selected)
        self.browser_screen.back_clicked.connect(self._go_to_menu)

        # Preview
        self.preview_screen.back_clicked.connect(self._go_to_browser)
        self.preview_screen.book_clicked.connect(self._on_book_hairstyle)
        self.preview_screen.try_another_clicked.connect(self._go_to_browser)

        # Appointment
        self.appointment_screen.back_clicked.connect(self._go_to_menu)
        self.appointment_screen.appointment_booked.connect(self._on_appointment_booked)

        # History
        self.history_screen.back_clicked.connect(self._go_to_menu)

    # ── Frame handling ──────────────────────────────────────────────

    def _on_frame(self, frame: np.ndarray) -> None:
        self._latest_frame = frame
        self._frame_count += 1

        current = self.app.current_screen_name()

        # Feed frame to face detection thread every N frames
        if self.face_thread and self._frame_count % self.config.face_detection_interval == 0:
            self.face_thread.submit_frame(frame)

        # Draw face overlays on mirror screen
        if current == "mirror":
            if self._latest_faces:
                annotated = draw_face_overlays(frame, self._latest_faces)
                self.mirror_screen.update_frame(annotated)
            else:
                self.mirror_screen.update_frame(frame)
        elif current == "recognition":
            self.recognition_screen.update_frame(frame)
        elif current == "menu":
            self.main_menu_screen.update_frame(frame)

    def _on_faces_detected(self, faces: list[FaceResult]) -> None:
        self._latest_faces = faces
        current = self.app.current_screen_name()

        if current == "mirror" and faces:
            # Cooldown to prevent rapid re-navigation
            now = time.time()
            if now - self._last_nav_time < self._nav_cooldown_seconds:
                return

            self._last_nav_time = now
            face = faces[0]
            self.app.navigate_to("recognition", {"face": face})

    # ── Navigation handlers ─────────────────────────────────────────

    def _go_to_mirror(self) -> None:
        self._last_nav_time = time.time()  # reset cooldown
        self.app.navigate_to("mirror")

    def _on_continue_as_customer(self, customer_id: int) -> None:
        customer = self.customer_service.get_by_id(customer_id)
        if customer:
            self._current_customer_id = customer.id
            self._current_customer_name = customer.name
            self._current_customer_gender = customer.gender
            self.app.navigate_to("menu", {"customer_name": customer.name})

    def _on_create_profile(self, face: FaceResult) -> None:
        self.app.navigate_to("profile", {"face": face})

    def _on_profile_saved(self, customer_id: int) -> None:
        customer = self.customer_service.get_by_id(customer_id)
        if customer:
            self._current_customer_id = customer.id
            self._current_customer_name = customer.name
            self._current_customer_gender = customer.gender

            # Register face for future recognition
            if customer.face_encoding is not None:
                encoding = np.frombuffer(customer.face_encoding, dtype=np.float64)
                self.face_service.register_face(encoding, customer.id, customer.name)

            self.app.navigate_to("menu", {"customer_name": customer.name})

    def _go_to_menu(self) -> None:
        self.app.navigate_to("menu", {
            "customer_name": self._current_customer_name or ""
        })

    def _go_to_browser(self) -> None:
        self.app.navigate_to("browser", {
            "gender": self._current_customer_gender
        })

    def _go_to_appointment(self) -> None:
        self.app.navigate_to("appointment", {
            "customer_id": self._current_customer_id
        })

    def _go_to_history(self) -> None:
        self.app.navigate_to("history", {
            "customer_id": self._current_customer_id
        })

    def _go_to_edit_profile(self) -> None:
        self.app.navigate_to("profile", {
            "customer_id": self._current_customer_id
        })

    # ── Hairstyle preview ───────────────────────────────────────────

    def _on_hairstyle_selected(self, hairstyle) -> None:
        self.app.navigate_to("preview", {"hairstyle": hairstyle})
        self.preview_screen.set_loading("Generating preview...")

        if self._latest_frame is not None:
            self.preview_screen.set_original_frame(self._latest_frame)

            # Find face box from latest detection
            face_box = None
            if self._latest_faces:
                face_box = self._latest_faces[0].bounding_box
            else:
                # Use center of frame as fallback
                h, w = self._latest_frame.shape[:2]
                face_box = (h // 4, w * 3 // 4, h * 3 // 4, w // 4)

            if self.hair_thread:
                self.hair_thread.request_preview(
                    self._latest_frame, face_box, hairstyle
                )

    def _on_preview_ready(self, result) -> None:
        self.preview_screen.set_preview_result(result)

    def _on_hair_status(self, message: str) -> None:
        current = self.app.current_screen_name()
        if current == "preview":
            self.preview_screen.set_loading(message)

    def _on_book_hairstyle(self, hairstyle) -> None:
        self.app.navigate_to("appointment", {
            "customer_id": self._current_customer_id,
            "hairstyle": hairstyle,
        })

    def _on_appointment_booked(self, appointment_id: int) -> None:
        pass  # Stay on appointment screen showing success message


def main() -> int:
    controller = SmartMirrorController()
    return controller.setup()


if __name__ == "__main__":
    sys.exit(main())
