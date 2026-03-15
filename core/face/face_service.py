from dataclasses import dataclass

import numpy as np

from core.face.detector import FaceDetector
from core.face.recognizer import FaceRecognizer
from db.models import Customer


@dataclass
class FaceResult:
    bounding_box: tuple[int, int, int, int]  # (top, right, bottom, left)
    encoding: np.ndarray | None
    customer_id: int | None  # matched customer ID or None
    customer_name: str | None
    confidence: float  # distance (lower = better match)


class FaceService:
    """Orchestrates face detection, encoding, and recognition."""

    def __init__(self, model: str = "hog", tolerance: float = 0.6):
        self._detector = FaceDetector(model=model)
        self._recognizer = FaceRecognizer(tolerance=tolerance)
        self._known_encodings: list[np.ndarray] = []
        self._known_customer_ids: list[int] = []
        self._known_customer_names: list[str] = []

    def load_known_faces(self, customers: list[Customer]) -> None:
        """Load face encodings from customer records into memory."""
        self._known_encodings.clear()
        self._known_customer_ids.clear()
        self._known_customer_names.clear()

        for customer in customers:
            if customer.face_encoding is not None:
                encoding = np.frombuffer(customer.face_encoding, dtype=np.float64)
                self._known_encodings.append(encoding)
                self._known_customer_ids.append(customer.id)
                self._known_customer_names.append(customer.name)

    def register_face(self, encoding: np.ndarray, customer_id: int, name: str) -> None:
        """Add a new face encoding to the in-memory index."""
        self._known_encodings.append(encoding)
        self._known_customer_ids.append(customer_id)
        self._known_customer_names.append(name)

    def process_frame(self, frame: np.ndarray) -> list[FaceResult]:
        """Detect and recognize all faces in a frame."""
        locations = self._detector.detect(frame)
        if not locations:
            return []

        encodings = self._recognizer.encode_all(frame, locations)
        results = []

        for location, encoding in zip(locations, encodings):
            match = self._recognizer.match(encoding, self._known_encodings)

            if match is not None:
                idx, distance = match
                results.append(FaceResult(
                    bounding_box=location,
                    encoding=encoding,
                    customer_id=self._known_customer_ids[idx],
                    customer_name=self._known_customer_names[idx],
                    confidence=distance,
                ))
            else:
                results.append(FaceResult(
                    bounding_box=location,
                    encoding=encoding,
                    customer_id=None,
                    customer_name=None,
                    confidence=1.0,
                ))

        return results

    @property
    def known_face_count(self) -> int:
        return len(self._known_encodings)
