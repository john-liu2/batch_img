"""class Rotate: detect if the image file(s) is upside down or sideways
Copyright © 2025 John Liu
"""

from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from loguru import logger
from PIL import Image

from batch_img.common import Common
from batch_img.const import UNKNOWN

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files

ORIENTATION_MAP = {
    1: "normal",
    2: "mirrored_horizontal",
    3: "upside_down",
    4: "mirrored_vertical",
    5: "rotated_left_mirrored",
    6: "rotated_left",
    7: "rotated_right_mirrored",
    8: "rotated_right",
}
DETECTED_ORIENTATION = {
    0: "normal",
    90: "rotated_left",
    180: "upside_down",
    270: "rotated_right",
}


class Rotate:
    @staticmethod
    def get_image_orientation(file: Path) -> str:
        """Get image orientation by EXIF data

        Args:
            file: image file path

        Returns:
            str
        """
        try:
            with Image.open(file) as img:
                if "exif" not in img.info:
                    logger.warning(f"No EXIF data in {file}")
                    return UNKNOWN
                exif_info = Common.decode_exif(img.info["exif"])
                if "Orientation" in exif_info:
                    return ORIENTATION_MAP.get(exif_info["Orientation"])
            logger.warning(f"No 'Orientation' tag in {exif_info=}")
            return UNKNOWN
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return f"{file}:\n{e}"

    @staticmethod
    def rotate_image(img, angle: int):
        """Rotate image by the angle degree clock wise

        Args:
            img: image data
            angle: angle degree int: 0, 90, 180, 270

        Returns:
            image data
        """
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    @staticmethod
    def detect_by_face(file: Path) -> int:
        """Detect orientation by face in mage by Haar Cascades:
        * Fastest but least accurate
        * Works best with frontal faces
        * May produce false positives

        Args:
            file: image file path

        Returns:
            int: 0, 90, 180, 270
        """
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        with Image.open(file) as safe_img:
            opencv_img = np.array(safe_img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")
            for angle in (0, 90, 180, 270):
                img = Rotate.rotate_image(opencv_img, angle)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.2, minNeighbors=6
                )
                logger.info(f"{len(faces)=}")
                if len(faces) > 0:
                    return angle
        logger.warning(f"Found no face in {file}")
        return -1

    @staticmethod
    def detect_orientation(file: Path) -> str:
        """Detect orientation by image content: text, face, etc.

        Args:
            file: image file path

        Returns:
            str
        """
