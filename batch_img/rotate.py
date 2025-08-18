"""class Rotate: rotate image file(s) to clockwise angle
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Rotate:
    @staticmethod
    def rotate_1_image_file(in_path: Path, out_path: Path, angle_cw: int) -> tuple:
        """Rotate an image file and save to the output dir

        Args:
            in_path: input file path
            out_path: output dir path
            angle_cw: rotation angle clockwise: 90, 180, or 270

        Returns:
            tuple: bool, str
        """
        if angle_cw not in {90, 180, 270}:
            return False, f"Bad {angle_cw=}. Only allow 90, 180, 270"
        try:
            with Image.open(in_path) as img:
                exif_dict = {"0th": {}, "Exif": {}}
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                # logger.info(f"{exif_dict=}")
                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = f"{in_path.stem}_{angle_cw}cw{in_path.suffix}"
                    out_file = Path(f"{out_path}/{filename}")
                if angle_cw == 90:
                    rotated_img = img.rotate(-90, expand=True)
                elif angle_cw == 180:
                    rotated_img = img.rotate(180, expand=True)
                elif angle_cw == 270:
                    rotated_img = img.rotate(90, expand=True)
                else:
                    rotated_img = img

                rotated_img.save(out_file, img.format, exif=exif_bytes)
            logger.info(f"Saved rotated ({angle_cw}°) to {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"
