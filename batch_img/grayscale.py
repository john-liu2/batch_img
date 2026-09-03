"""Convert to grayscale image(s)
Copyright © 2026 - Present, John Liu
"""

from pathlib import Path

import pillow_heif

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

    @staticmethod
    def do_all_images(in_path: Path, out_path: Path | str, quiet: bool = False) -> bool:
        """Convert all image files in the dir to grayscale ones

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            quiet: suppress progress and error output

        Returns:
            bool: True - Success. False - Error
        """
