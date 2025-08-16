"""class Common: common utilities
Copyright © 2025 John Liu
"""

import subprocess
import tomllib
from importlib.metadata import version
from pathlib import Path

from loguru import logger

from batch_img.const import PKG_NAME, VER


class Common:
    @staticmethod
    def get_version() -> str:
        """
        Get this package version using several ways
        """
        try:
            return version(PKG_NAME)
        except (FileNotFoundError, ImportError, ValueError) as e:
            # Use lazy % formatting in logging for efficiency
            logger.warning(f"importlib.metadata.version Error: {e}")
            logger.debug("Try to get version from pyproject.toml file")
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject, "rb") as f:
                return tomllib.load(f)["project"][VER]

    @staticmethod
    def run_cmd(cmd: str) -> tuple:
        """Run a command on the host and get the output

        Args:
            cmd (str): a command line with options

        Returns:
            tuple: returnCode, StdOut, StdErr
        """
        logger.debug(f"{cmd=}")
        try:
            p = subprocess.run(
                cmd, capture_output=True, text=True, shell=True, check=True
            )
            r_code = p.returncode
            stdout = p.stdout
            stderr = p.stderr
            logger.debug(f"'{cmd}'\n {r_code=}\n {stdout=}\n {stderr=}")
            return r_code, stdout, stderr
        except subprocess.CalledProcessError as e:
            logger.exception(e)
            raise e
