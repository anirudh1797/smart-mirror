import cv2
import numpy as np

from core.face.face_service import FaceResult


def draw_face_overlays(frame: np.ndarray, faces: list[FaceResult]) -> np.ndarray:
    """Draw bounding boxes and name labels on a frame."""
    annotated = frame.copy()

    for face in faces:
        top, right, bottom, left = face.bounding_box

        if face.customer_name:
            # Known face — green box
            color = (0, 200, 100)
            label = face.customer_name
        else:
            # Unknown face — blue box
            color = (200, 150, 50)
            label = "New Face"

        # Draw bounding box
        cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)

        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(
            annotated,
            (left, bottom),
            (left + label_size[0] + 10, bottom + label_size[1] + 16),
            color,
            cv2.FILLED,
        )

        # Draw label text
        cv2.putText(
            annotated,
            label,
            (left + 5, bottom + label_size[1] + 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

    return annotated
