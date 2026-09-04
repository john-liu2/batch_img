"""Convert to grayscale image(s)
Copyright © 2026 - Present, John Liu
"""

import os
from pathlib import Path

import pillow_heif
from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF, REPLACE, SOFTWARE

pillow_heif.register_heif_opener()


class Grayscale:
    @staticmethod
    def do_one_image(args: tuple) -> tuple:
        """Convert an image file to grayscale one

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE

        Returns:
            tuple: bool, output file path
        """
        in_path, out_path = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                exif = img.getexif()
                # 1. Set 'Software' tag to show conversion
                # 2. Set ColorSpace to 'Uncalibrated' (65535) as it's no longer sRGB (1)
                software_tag = 0x0131  # EXIF tag for 'Software'
                color_space_tag = 0xA001  # EXIF tag for 'ColorSpace'
                exif[software_tag] = SOFTWARE
                exif[color_space_tag] = 65535

                # TIFF uses EXIF (IFD0) for structural image data.
                # Must remove the original RGB structural tags so Pillow can
                # automatically generate the Grayscale ones for the new file.
                tiff_structural_tags = [
                    256,  # ImageWidth
                    257,  # ImageLength
                    258,  # BitsPerSample
                    259,  # Compression
                    262,  # PhotometricInterpretation (1=BlackIsZero, 2=RGB)
                    273,  # StripOffsets
                    277,  # SamplesPerPixel (1=Grayscale, 3=RGB)
                    278,  # RowsPerStrip
                    279,  # StripByteCounts
                    284,  # PlanarConfiguration
                ]
                for tag in tiff_structural_tags:
                    exif.pop(tag, None)  # safely ignor non-exist key

                save_kwargs = {EXIF: exif}
                file = Common.set_out_file(in_path, out_path, "GrayScale")
                # Convert to grayscale
                gray_img = img.convert("L")
                gray_img.save(file, img.format, optimize=True, **save_kwargs)

            log.debug(f"Saved the grayscale image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def do_all_images(in_path: Path, out_path: Path | str, quiet: bool = False) -> bool:
        """Convert all image files in the folder to grayscale ones

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            quiet: suppress progress and error output

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Convert {files_cnt} image(s) to grayscale in multiprocess ...")
        success_cnt = Common.executor_progress(
            Grayscale.do_one_image,
            "Convert image(s) to grayscale",
            tasks,
            quiet=quiet,
        )
        log.info(f"\nSuccessfully converted {success_cnt}/{files_cnt} image(s)")
        return True
