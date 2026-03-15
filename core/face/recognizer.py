import dlib
import numpy as np

# Load dlib models directly (same models face_recognition uses)
import face_recognition.api as _fr_api

_face_encoder = _fr_api.face_encoder
_pose_predictor = _fr_api.pose_predictor_68_point


def _compute_encodings(
    rgb_image: np.ndarray,
    face_locations: list[tuple[int, int, int, int]],
) -> list[np.ndarray]:
    """Compute face encodings using dlib directly.

    Bypasses face_recognition.face_encodings() to avoid the dlib 19.24.6
    compatibility issue with compute_face_descriptor().
    """
    # Ensure contiguous array (BGR->RGB via [::-1] creates non-contiguous)
    rgb_image = np.ascontiguousarray(rgb_image)

    results = []
    for top, right, bottom, left in face_locations:
        rect = dlib.rectangle(left, top, right, bottom)
        landmark = _pose_predictor(rgb_image, rect)

        # Use single-face API (signature 1)
        descriptor = _face_encoder.compute_face_descriptor(rgb_image, landmark)
        results.append(np.array(descriptor))

    return results


class FaceRecognizer:
    """Encodes faces and compares against known encodings."""

    def __init__(self, tolerance: float = 0.6):
        self._tolerance = tolerance

    def encode(self, frame: np.ndarray, face_location: tuple[int, int, int, int]) -> np.ndarray | None:
        """Compute 128-d face encoding for a detected face."""
        rgb = np.ascontiguousarray(frame[:, :, ::-1])
        encodings = _compute_encodings(rgb, [face_location])
        if encodings:
            return encodings[0]
        return None

    def encode_all(self, frame: np.ndarray, face_locations: list[tuple[int, int, int, int]]) -> list[np.ndarray]:
        """Compute encodings for all detected faces."""
        rgb = np.ascontiguousarray(frame[:, :, ::-1])
        return _compute_encodings(rgb, face_locations)

    def match(
        self,
        encoding: np.ndarray,
        known_encodings: list[np.ndarray],
    ) -> tuple[int, float] | None:
        """Match an encoding against known encodings.

        Returns (index, distance) of the best match, or None if no match.
        """
        if not known_encodings:
            return None

        import face_recognition
        distances = face_recognition.face_distance(known_encodings, encoding)
        best_idx = int(np.argmin(distances))
        best_distance = float(distances[best_idx])

        if best_distance <= self._tolerance:
            return best_idx, best_distance

        return None
