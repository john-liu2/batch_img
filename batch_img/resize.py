"""class Resize: resize the image file(s)
Copyright © 2025 John Liu
"""

from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Resize:
    @staticmethod
    def resize_an_image(in_path: Path | str, out_path: Path | str, length: int) -> Path:
        """Resize one image file

        Args:
            in_path: input file path
            out_path: output dir path
            length: max length (width or height) in pixels

        Returns:
            Path: output file path
        """
        try:
            with Image.open(in_path) as img:
                width, height = img.size
                aspect_ratio = width / height

            exif_dict = None
            if "exif" in img.info:
                exif_dict = piexif.load(img.info["exif"])

            # Calculate max_size by max_side and aspect_ratio
            if aspect_ratio > 1:
                max_size = (length, int(length / aspect_ratio))
            else:
                max_size = (int(length * aspect_ratio), length)

            # Keep the aspect ratio. Use LANCZOS for high-quality downsampling
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save back to HEIC format with EXIF
            out_path.mkdir(exist_ok=True)
            out_file = out_path
            if out_path.is_dir():
                filename = f"{in_path.stem}_{length}{in_path.suffix}"
                out_file = Path(f"{out_path}/{filename}")
            if exif_dict:
                exif_bytes = piexif.dump(exif_dict)
                img.save(out_file, format="HEIF", exif=exif_bytes)
            else:
                img.save(out_file, format="HEIF")
            logger.info(f"Saved {out_file}")
            return out_file
        except Exception as e:
            logger.exception(e)
            raise e
