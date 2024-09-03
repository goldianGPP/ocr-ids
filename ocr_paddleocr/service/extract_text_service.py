from injector import inject
import gc
import threading
import base64
import numpy as np
from io import BytesIO
from paddleocr import PaddleOCR
import logging
import cv2
from PIL import Image

logger = logging.getLogger("ocr-ids-be")


class ExtractTextService:

    @inject
    def __init__(self):
        self.ocr_model = PaddleOCR(
            use_angle_cls=False,
            lang="en",
            rec_model_dir="ch_PP-OCRv4_rec_infer",
            det_model_dir="ch_PP-OCRv4_det_infer",
            cls_model_dir="ch_ppocr_mobile_v2.0_cls_infer",
        )
        self.ocr_model.det_lang = "ml"
        self.lock = threading.Lock()
        logger.info("MrzService instance created")

    def _get_horizontal_lines(
        self, results, height_threshold=0.5, distance_threshold=50
    ):
        # Extract text boxes and their coordinates
        boxes = [line[0] for line in results[0]]
        texts = [line[1][0] for line in results[0]]

        # Calculate the vertical center and the horizontal position of each box
        centers = [(box[0][1] + box[2][1]) / 2 for box in boxes]
        heights = [(box[2][1] - box[0][1]) for box in boxes]
        x_positions = [box[0][0] for box in boxes]

        lines = []
        current_line = []
        prev_center = centers[0]
        prev_x = x_positions[0]

        for i in range(len(texts)):
            if (
                abs(centers[i] - prev_center) <= height_threshold * heights[i]
                and abs(x_positions[i] - prev_x) <= distance_threshold
            ):
                # Same line and within distance threshold
                current_line.append(texts[i])
            else:
                # New line
                lines.append(" ".join(current_line))
                current_line = [texts[i]]
            prev_center = centers[i]
            prev_x = (
                x_positions[i] + boxes[i][2][0] - boxes[i][0][0]
            )  # Update to the end x-position

        # Append the last line
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _lightweight_preprocess(self, image, w_threshold=True):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        finally:
            del gray
            del binary
            del _
            del clahe

    def extract_from_base64(
        self, imageBase64, w_threshold=True, height_threshold=0.5, distance_threshold=50
    ):
        with self.lock:
            image_data = base64.b64decode(imageBase64)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)
            preprocessed_image = self._lightweight_preprocess(
                image_np, w_threshold=w_threshold
            )

            try:
                return self._get_horizontal_lines(
                    results=self.ocr_model.ocr(image_np, cls=True),
                    height_threshold=height_threshold,
                    distance_threshold=distance_threshold,
                )
            except Exception as e:
                logging.error(f"Error processing OCR: {e}")
                return None
            finally:
                del image_np
                del preprocessed_image
                gc.collect()
