"""class Auto - do auto actions to the image file(s):
    * Resize to 1280 pixels as the max length
    * Add the border of 5 pixel width in black color
    * Remove GPS location info
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import pillow_heif
from PIL import Image

from batch_img.common import Common
from batch_img.const import BD_COLOR, BD_WIDTH, EXIF, MAX_LENGTH, REPLACE
from batch_img.log import logger
from batch_img.orientation import Orientation
from batch_img.rotate import Rotate

pillow_heif.register_heif_opener()


class Auto:
    @staticmethod
    def process_an_image(in_path: Path, out_path: Path | str) -> tuple:
        """Process an image file:
        * Resize to 1280 pixels as the max length
        * Add the border of 9 pixel width in gray color
        * Remove GPS location info

        Args:
            in_path: input file path
            out_path: output dir path or REPLACE

        Returns:
            tuple: bool, str
        """
        try:
            with Image.open(in_path) as img:
                width, height = img.size
                logger.debug(f"{width=}, {height=}")
                new_size = Common.calculate_new_size(width, height, MAX_LENGTH)
                new_img = img.resize(new_size, Image.Resampling.LANCZOS, reducing_gap=3)

                # Add border
                width, height = new_img.size
                logger.debug(f"new_img: {width=}, {height=}")
                box = Common.get_crop_box(width, height, BD_WIDTH)
                cropped_img = new_img.crop(box)
                bd_img = Image.new(new_img.mode, (width, height), BD_COLOR)
                bd_img.paste(cropped_img, (BD_WIDTH, BD_WIDTH))

                file = Common.set_out_file(in_path, out_path, f"bw{BD_WIDTH}")

                if EXIF not in img.info:
                    logger.debug(f"No EXIF in {in_path}")
                    bd_img.save(file, img.format, optimize=True)
                else:
                    _, exif_bytes = Common.remove_exif_gps(img.info[EXIF])
                    logger.debug(f"Purge GPS in EXIF in {in_path}")
                    bd_img.save(file, img.format, optimize=True, exif=exif_bytes)
            logger.debug(f"Saved the processed image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                logger.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def rotate_if_needed(in_path: Path, out_path: Path | str) -> tuple:
        """Rotate if the image is upside down or sideways

        Args:
            in_path: image file path
            out_path: output dir path

        Returns:
            tuple: bool, file path
        """
        cw_angle = Orientation().get_cw_angle_by_face(in_path)
        logger.debug(f"By face: {cw_angle=}")
        if cw_angle in {-1, 0}:
            logger.warning(f"Found no face in {in_path.name=}. Try check by floor...")
            cw_angle, _ = Orientation().detect_floor_by_edge(in_path)
            if cw_angle == -1:
                logger.warning(f"Found no floor in {in_path.name=}. Skip.")
                return False, in_path
        ok, out_file = Rotate.rotate_1_image((in_path, out_path, cw_angle))
        return ok, out_file

    @staticmethod
    def auto_do_1_image(args: tuple) -> tuple:
        """Auto process an image file:
        * Resize to 1280 pixels as the max length
        * Add the border of 9 pixel width in gray color
        * Remove GPS location info

        Args:
            args: tuple of the below params:
            in_path: image file path
            out_path: output dir path or REPLACE
            auto_rotate: auto rotate image flag

        Returns:
            tuple: bool, str
        """
        in_path, out_path, auto_rotate = args
        Common.set_log_by_process()
        ok, file = Auto.process_an_image(in_path, out_path)
        if auto_rotate:
            _, file = Auto.rotate_if_needed(file, out_path)
        return ok, file

    @staticmethod
    def auto_on_all(in_path: Path, out_path: Path | str, auto_rotate: bool) -> bool:
        """Auto process all images in a folder

        Args:
            in_path: input file path
            out_path: output dir path
            auto_rotate: auto rotate image flag

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, auto_rotate) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            logger.error(f"No image files at {in_path}")
            return False

        logger.debug(f"Auto process {files_cnt} files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Auto.auto_do_1_image, "Auto process image files", files_cnt, tasks
        )
        logger.info(f"\nAuto processed {success_cnt}/{files_cnt} files")
        return True
