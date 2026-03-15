import face_recognition
import numpy as np


class FaceDetector:
    """Detects face locations in a frame."""

    def __init__(self, model: str = "hog"):
        self._model = model  # "hog" (CPU) or "cnn" (GPU)

    def detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Detect face locations in a BGR frame.

        Returns list of (top, right, bottom, left) bounding boxes.
        """
        rgb = frame[:, :, ::-1]  # BGR -> RGB
        locations = face_recognition.face_locations(rgb, model=self._model)
        return locations
