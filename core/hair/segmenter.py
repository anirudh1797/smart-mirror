import cv2
import numpy as np


class HairSegmenter:
    """Generates a hair mask from a face region using classical CV techniques.

    This is a lightweight fallback. For production, replace with a
    BiSeNet face-parsing model for more accurate segmentation.
    """

    def segment(
        self, frame: np.ndarray, face_box: tuple[int, int, int, int]
    ) -> np.ndarray:
        """Generate a binary mask covering the hair region.

        Args:
            frame: BGR image
            face_box: (top, right, bottom, left) face bounding box

        Returns:
            Binary mask (same size as frame), 255=hair region, 0=elsewhere
        """
        top, right, bottom, left = face_box
        h, w = frame.shape[:2]
        face_h = bottom - top
        face_w = right - left

        mask = np.zeros((h, w), dtype=np.uint8)

        # Estimate hair region: above the face + sides
        hair_top = max(0, top - int(face_h * 0.8))
        hair_left = max(0, left - int(face_w * 0.2))
        hair_right = min(w, right + int(face_w * 0.2))
        hair_bottom = top + int(face_h * 0.3)  # Overlap slightly into forehead

        # Create elliptical mask for natural hair shape
        center_x = (hair_left + hair_right) // 2
        center_y = (hair_top + hair_bottom) // 2
        axis_x = (hair_right - hair_left) // 2
        axis_y = (hair_bottom - hair_top) // 2

        cv2.ellipse(
            mask,
            (center_x, center_y),
            (axis_x, axis_y),
            0, 0, 360,
            255,
            cv2.FILLED,
        )

        # Also add side regions for longer hairstyles
        side_bottom = bottom + int(face_h * 0.2)
        # Left side
        cv2.ellipse(
            mask,
            (left - int(face_w * 0.05), (top + side_bottom) // 2),
            (int(face_w * 0.2), (side_bottom - top) // 2),
            0, 0, 360,
            255,
            cv2.FILLED,
        )
        # Right side
        cv2.ellipse(
            mask,
            (right + int(face_w * 0.05), (top + side_bottom) // 2),
            (int(face_w * 0.2), (side_bottom - top) // 2),
            0, 0, 360,
            255,
            cv2.FILLED,
        )

        # Remove the face area from the mask (keep face intact)
        face_center_x = (left + right) // 2
        face_center_y = (top + bottom) // 2
        face_axis_x = int(face_w * 0.38)
        face_axis_y = int(face_h * 0.42)
        cv2.ellipse(
            mask,
            (face_center_x, face_center_y),
            (face_axis_x, face_axis_y),
            0, 0, 360,
            0,
            cv2.FILLED,
        )

        # Smooth the mask edges
        mask = cv2.GaussianBlur(mask, (21, 21), 10)

        return mask
