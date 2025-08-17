"""class Main: the entry point of the tool
Copyright © 2025 John Liu
"""

import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from batch_img.const import PKG_NAME, TS_FORMAT
from batch_img.resize import Resize


class Main:
    @staticmethod
    def init_log_file() -> str:
        """Set up the unique name log file for each run

        Returns:
            str: log file path
        """
        log_file = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        logger.add(
            f"{os.getcwd()}/{log_file}", backtrace=True, diagnose=True, enqueue=True
        )
        return log_file

    @staticmethod
    def resize(options: dict) -> bool:
        """Resize the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        # Resize one file
        in_path = Path(options["src_path"])
        length = options.get("length")
        if not length:
            logger.warning(f"No resize due to bad {length=}")
            return False
        ok, _ = Resize.resize_an_image(in_path, Path(os.getcwd()), length)
        return ok

    @staticmethod
    def add_border(options: dict) -> bool:
        """Add border to the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        # To-do
        return True

    @staticmethod
    def rotate(options: dict) -> bool:
        """Rotate the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        # To-do
        return True

    @staticmethod
    def default_run(options: dict) -> bool:
        """Do the default action on the image file(s):
        1) Resize to 1280 pixels as the max length
        2) Add a border: 5 pixel width, gray color
        3) Not rotate
        """
        logger.info(f"{json.dumps(options, indent=2)}")
        Main.init_log_file()
        # To-do
        return True
