"""class Common: common utilities
Copyright © 2025 John Liu
"""

import json
import subprocess
import tomllib
from datetime import datetime
from importlib.metadata import version
from os.path import getmtime, getsize
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image, ImageChops

from batch_img.const import PKG_NAME, TS_FORMAT, VER

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


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

    @staticmethod
    def readable_file_size(in_bytes: int) -> str:
        """Convert bytes to human-readable KB, MB, or GB

        Args:
            in_bytes: input bytes integer

        Returns:
            str
        """
        for _unit in ["B", "KB", "MB", "GB"]:
            if in_bytes < 1024:
                break
            in_bytes /= 1024
        res = f"{in_bytes} B" if _unit == "B" else f"{in_bytes:.1f} {_unit}"
        return res

    @staticmethod
    def decode_exif(exif_data: str) -> dict:
        """Decode the EXIF data

        Args:
            exif_data: str

        Returns:
            dict
        """
        exif_dict = piexif.load(exif_data)
        _dict = {}
        for ifd_name, val in exif_dict.items():
            if not val:
                continue
            for tag_id, value in val.items():
                tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get("name", tag_id)
                _dict[tag_name] = value
        for key in (
            "FNumber",
            "FocalLength",
            "MakerNote",
            "SceneType",
            "SubjectArea",
            "Software",
            "HostComputer",
        ):
            if key in _dict:
                _dict.pop(key)
        keys = list(_dict.keys())
        for keyword in (
            "DateTime",
            "GPS",
            "OffsetTime",
            "SubSecTime",
            "Tile",
            "Pixel",
            "Lens",
            "Resolution",
            "Value",
        ):
            for key in keys:
                if key.startswith(keyword) or key.endswith(keyword):
                    _dict.pop(key)
        _res = {
            k: (v.decode() if isinstance(v, bytes) else v) for k, v in _dict.items()
        }
        logger.info(f"{_res=}")
        return _res

    @staticmethod
    def are_images_equal(path1: Path | str, path2: Path | str) -> bool:
        """Check if two image files are visually equal pixel-wise

        Args:
            path1: image1 file path
            path2: image2 file path

        Returns:
            bool: True - visually equal, False - not visually equal
        """
        size1 = getsize(path1)
        m_ts1 = datetime.fromtimestamp(getmtime(path1)).strftime(TS_FORMAT)
        with Image.open(path1) as img1:
            data1 = img1.convert("RGB")
            meta1 = {
                "file_size": Common.readable_file_size(size1),
                "file_ts": m_ts1,
                "format": img1.format,
                "size": img1.size,
                "mode": img1.mode,
                "info": img1.info,
            }
            if "exif" in img1.info:
                meta1["info"] = Common.decode_exif(img1.info["exif"])

        size2 = getsize(path2)
        m_ts2 = datetime.fromtimestamp(getmtime(path2)).strftime(TS_FORMAT)
        with Image.open(path2) as img2:
            data2 = img2.convert("RGB")
            meta2 = {
                "file_size": Common.readable_file_size(size2),
                "file_ts": m_ts2,
                "format": img2.format,
                "size": img2.size,
                "mode": img2.mode,
                "info": img2.info,
            }
            if "exif" in img2.info:
                meta2["info"] = Common.decode_exif(img2.info["exif"])

        logger.info(f"Meta of {path1}:\n{json.dumps(meta1, indent=2)}")
        logger.info(f"Meta of {path2}:\n{json.dumps(meta2, indent=2)}")
        return ImageChops.difference(data1, data2).getbbox() is None
