"""class Main: the entry point of the tool
Copyright © 2025 John Liu
"""

import json
import os
from datetime import datetime

from loguru import logger

from batch_img.common import Common
from batch_img.const import PKG_NAME

TS_FORMAT = "%Y-%m-%d_%H-%M-%S"


class Main:
    @staticmethod
    def run(options: dict) -> str:
        """
        Check options and run
        """
        cur_ver = Common.get_version()
        if options.get("version"):
            return cur_ver

        logger.info(f"{json.dumps(options, indent=2)}")
        log_file = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        logger.add(
            f"{os.getcwd()}/{log_file}", backtrace=True, diagnose=True, enqueue=True
        )
        if options.get("resize"):
            max_width = int(options.get("resize"))
            # To-do
            return f"Resized image file(s) to {max_width}"

        if options.get("rotate"):
            degree = int(options.get("rotate"))
            # To-do
            return f"Rotated image file(s) to {degree}-degree clock-wise"

        return log_file
