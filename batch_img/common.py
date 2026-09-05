"""class Common: common utilities
Copyright © 2025 John Liu
"""

import hashlib
import importlib.metadata
import itertools
import json
import os
import subprocess
import sys
import tomllib
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from multiprocessing import current_process
from os.path import getmtime, getsize
from pathlib import Path
from time import time

import httpx
import piexif
import pillow_heif
from loguru import logger as log
from packaging import version  # compare versions safely
from PIL import Image, ImageChops
from PIL.TiffImagePlugin import IFDRational
from tqdm import tqdm

from batch_img.const import (
    EXIF,
    EXPIRE_HOUR,
    PATTERNS,
    PKG_NAME,
    REPLACE,
    TS_2_MINUTE,
    TS_FORMAT2,
    UNKNOWN,
    VER,
)
from batch_img.exif import Exif
from batch_img.log import Log

pillow_heif.register_heif_opener()
VER_CACHE = Path(f"~/.{PKG_NAME}_version_cache.json").expanduser()


class Common:
    @staticmethod
    def get_version(pkg_name: str) -> str:
        """Get this package version by various ways

        Args:
            pkg_name: package name str

        Returns:
            str:
        """
        try:
            return importlib.metadata.version(pkg_name)
        except (FileNotFoundError, ImportError, ValueError) as e:
            log.warning(f"importlib.metadata.version() Error: {e}")
            log.debug("Get version from pyproject.toml file")
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject, "rb") as f:
                return tomllib.load(f)["project"][VER]

    @staticmethod
    def get_latest_pypi_ver(pkg_name: str, expire_hr: int = EXPIRE_HOUR):
        """Get the package latest version on PyPI with local cache

        Args:
            pkg_name: package name str
            expire_hr: cache expiration hour int

        Returns:
            str: latest version on PyPI
        """
        jsn_url = f"https://pypi.org/pypi/{pkg_name}/json"
        latest_ver = ""
        try:
            if pkg_name in str(VER_CACHE) and VER_CACHE.exists():
                with open(VER_CACHE, encoding="utf-8") as f:
                    cache = json.load(f)
                    if time() - cache["timestamp"] < expire_hr * 3600:
                        latest_ver = cache["version"]
            if not latest_ver:
                response = httpx.get(jsn_url, timeout=5)
                if response.status_code != 200:
                    msg = f"⚠️ Error get data from PyPI: {jsn_url}"
                    log.error(msg)
                    return UNKNOWN
                latest_ver = response.json()["info"]["version"]
                d_cache = {"timestamp": int(time()), "version": latest_ver}
                with open(VER_CACHE, "w", encoding="utf-8") as f:
                    json.dump(d_cache, f)
            return latest_ver
        except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
            raise e

    @staticmethod
    def check_latest_version(pkg_name: str) -> str:
        """Check if the installed version is the latest one

        Args:
            pkg_name: package name str

        Returns:
            str
        """
        msg = ""
        try:
            latest_ver = Common.get_latest_pypi_ver(pkg_name)
            cur_ver = Common.get_version(pkg_name)
            if version.parse(cur_ver) < version.parse(latest_ver):
                msg = (
                    f"🔔 Update available: {cur_ver}  →  {latest_ver}\n"
                    f"Run '{pkg_name} --update'"
                )
                log.info(msg)
        except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
            msg = f"Error get PyPI data: {e}"
            log.error(msg)
        return msg

    @staticmethod
    def update_package(pkg_name: str) -> str:
        """Update the package to the latest version

        Args:
            pkg_name: package name str

        Returns:
            str
        """
        Log.init_log_file()
        msg = Common.check_latest_version(pkg_name)
        if "Update available" not in msg:
            return msg
        log.info(f"🔄 Updating {pkg_name} ...")
        cmd = f"uv pip install --upgrade {pkg_name}"
        if sys.prefix != sys.base_prefix:
            # inside a venv or virtualenv
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", pkg_name]
        try:
            Common.run_cmd(cmd)
            msg = "✅ Update completed."
            log.info(msg)
        except subprocess.CalledProcessError as e:
            msg = f"❌ Update {pkg_name}: {e}"
            log.error(msg)
        return msg

    @staticmethod
    def run_cmd(cmd: list | str) -> tuple:
        """Run a command on the host and get the output

        Args:
            cmd: a command line with options

        Returns:
            tuple: returnCode, StdOut, StdErr
        """
        log.debug(f"{cmd=}")
        cmd_lst = cmd if isinstance(cmd, list) else cmd.split()
        try:
            p = subprocess.run(cmd_lst, capture_output=True, text=True, check=True)
            r_code = p.returncode
            stdout = p.stdout
            stderr = p.stderr
            log.debug(f"'{cmd=}'\n {r_code=}\n {stdout=}\n {stderr=}")
            return r_code, stdout, stderr
        except subprocess.CalledProcessError as e:
            log.exception(e)
            raise e

    @staticmethod
    def human_readable_time(seconds: float) -> str:
        """
        Convert duration in seconds to human-readable duration string
        :param seconds: seconds float
        :return: duration string
        """
        if seconds > 60.0:
            return str(timedelta(seconds=round(seconds)))
        return f"{str(round(seconds, 2))} s"

    @staticmethod
    def file_to_base64(file: Path) -> str:
        """Encode a file to base64 str

        Args:
            file: input file path

        Returns:
            str:
        """
        with open(file, "rb") as f:
            data = f.read().replace(b"\r\n", b"\n")
            sha256 = hashlib.sha256(data).hexdigest()
            log.debug(f"{file} - {sha256=}")
            return b64encode(data).decode("utf-8")

    @staticmethod
    def easy_file_sz(sz: int) -> str:
        """Convert bytes to human-readable KB, MB, or GB

        Args:
            sz: bytes integer

        Returns:
            str
        """
        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        while sz > 1024.0 and unit_index < len(units) - 1:
            # Stop if under 1024, OR if reached the last available unit ("GB")
            sz /= 1024.0
            unit_index += 1

        unit = units[unit_index]
        s = f"{round(sz)} {unit}" if unit in {"B", "KB"} else f"{sz:.1f} {unit}"
        return s

    @staticmethod
    def remove_exif_gps(exif_data: bytes) -> tuple:
        """Remove GPS info from the EXIF data

        Args:
            exif_data: bytes

        Returns:
            tuple: bool, bytes
        """
        exif_dict = piexif.load(exif_data)
        if "GPS" in exif_dict and exif_dict["GPS"]:
            exif_dict.pop("GPS")
            exif_bytes = piexif.dump(exif_dict)
            log.debug("Removed GPS info in EXIF")
            return True, exif_bytes
        log.debug("No GPS in EXIF")
        return False, exif_data

    @staticmethod
    def decode_exif(exif_data: bytes) -> dict:
        """Decode the EXIF data

        Args:
            exif_data: bytes

        Returns:
            dict
        """
        exif_dict = piexif.load(exif_data)
        _dict = {}
        for ifd_name, val in exif_dict.items():
            # Canon EOS 5D Mark II 'thumbnail': b'\xff\xd8\xff\xdb...
            # 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
            if not val or ifd_name == "thumbnail":
                continue
            for tag_id, value in val.items():
                tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get("name", tag_id)
                _dict[tag_name] = value
        # log.info(f"{_dict=}")
        for key in (
            "HostComputer",
            "InterColorProfile",
            "MakerNote",
            "SceneType",
            "Software",
            "SubjectArea",
            "UserComment",
            "XMLPacket",
        ):
            _dict.pop(key, None)  # safely ignor non-exist key
        keys = list(_dict.keys())
        for keyword in (
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
            # Use errors="replace" to prevent UnicodeDecodeError on raw binary bytes
            _res = {
                k: (v.decode("utf-8", errors="replace") if isinstance(v, bytes) else v)
                for k, v in _dict.items()
            }
        log.debug(f"{_res=}")
        return _res

    @staticmethod
    def sort_nested_dict(data):
        """Sort nested dict for deterministic output"""
        # If it's a dictionary, sort its keys and recursively sort its values
        if isinstance(data, dict):
            return {k: Common.sort_nested_dict(v) for k, v in sorted(data.items())}

        # If it's a list, check if there are dictionaries inside the list
        if isinstance(data, list):
            return [Common.sort_nested_dict(item) for item in data]

        # Base case: return the value as-is if it's not a dict or list
        return data

    @staticmethod
    def _extract_tiff_metadata(img, d_info: dict) -> None:
        """Extract missing bit_depth and chroma natively for TIFF format"""
        if img.format != "TIFF" or not hasattr(img, "tag_v2"):
            return
        if "bit_depth" not in d_info["info"]:
            bps = img.tag_v2.get(258)
            if bps:
                d_info["info"]["bit_depth"] = bps[0] if isinstance(bps, tuple) else bps
        if "chroma" not in d_info["info"]:
            subs = img.tag_v2.get(530)
            if subs and isinstance(subs, tuple):
                chroma_map = {
                    (1, 1): "4:4:4",
                    (2, 1): "4:2:2",
                    (2, 2): "4:2:0",
                    (1, 2): "4:4:0",
                    (4, 1): "4:1:1",
                }
                if subs in chroma_map:
                    d_info["info"]["chroma"] = chroma_map[subs]
            elif img.mode in {"RGB", "RGBA"}:
                d_info["info"]["chroma"] = "4:4:4:4" if img.mode == "RGBA" else "4:4:4"

    @staticmethod
    def _process_exif_data(img, d_info: dict) -> None:
        """Extract and decode EXIF data with fallback support"""
        exif_data = img.info.pop(EXIF, None)
        if not exif_data and hasattr(img, "getexif"):
            try:
                exif_obj = img.getexif()
                if exif_obj:
                    exif_data = exif_obj.tobytes()
            except (AttributeError, NotImplementedError, ValueError) as e:
                log.debug(f"Failed to get exif via getexif(): {e}")

        if not exif_data:
            return
        try:
            d_info[EXIF] = Common.decode_exif(exif_data)
        except (
            ValueError,
            KeyError,
            IndexError,
            UnicodeDecodeError,
        ) as e:
            log.debug(f"Failed to decode exif data: {e}")
            return

        dt_str = d_info[EXIF].get("DateTime")
        if dt_str:
            tmp = datetime.strptime(dt_str, TS_FORMAT2).strftime(TS_2_MINUTE)
            d_info[EXIF]["DateTime"] = tmp

        val = d_info[EXIF].get("ColorSpace")
        if val == 1 and d_info["c_profile"] == UNKNOWN:
            if d_info.get("mode") == "L":
                d_info["c_profile"] = "Generic Gray Gamma 2.2 Profile"
            else:
                d_info["c_profile"] = "sRGB IEC61966-2.1"

    @staticmethod
    def get_image_data(file: Path) -> tuple:
        """Get image file data combining raw byte header parsing and Pillow

        Args:
            file: image file path

        Returns:
            tuple: data, info
        """
        size = getsize(file)
        m_ts = datetime.fromtimestamp(getmtime(file)).strftime(TS_2_MINUTE)
        with open(file, "rb") as f:
            raw_bytes = f.read(65536)
        raw_meta = Exif.parse_raw_header(raw_bytes)

        with Image.open(file) as img:
            data = img.convert("RGB")
            d_info = {
                "file_size": f"{Common.easy_file_sz(size)} ({size} bytes)",
                "file_ts": m_ts,
                "format": img.format,
                "mode": raw_meta.get("mode") or img.mode,
                "c_profile": UNKNOWN,
                "size": img.size,
                "info": img.info,
            }
            if "bit_depth" in raw_meta:
                d_info["info"]["bit_depth"] = raw_meta["bit_depth"]
            if "chroma" in raw_meta:
                d_info["info"]["chroma"] = raw_meta["chroma"]

            Common._extract_tiff_metadata(img, d_info)
            # Extract and parse ICC Profile Name
            raw_icc = img.info.get("icc_profile")
            if raw_icc:
                d_info["c_profile"] = Exif.get_icc_profile(raw_icc)

            for key in ("xmp", "XML:com.adobe.xmp", "icc_profile"):  # clean up
                img.info.pop(key, None)  # safely ignor non-exist key

            val = img.info.get("chroma", None)
            if val and isinstance(val, int):  # Convert 420 to "4:2:0"
                img.info["chroma"] = ":".join(str(val))

            Common._process_exif_data(img, d_info)

        if d_info["c_profile"] == UNKNOWN:
            d_info["c_profile"] = (
                "Generic Gray Gamma 2.2 Profile" if d_info["mode"] == "L" else "sRGB"
            )
        return data, Common.sort_nested_dict(d_info)

    @staticmethod
    def jsn_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, IFDRational):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        raise TypeError(f"Type {type(obj)} not serializable")

    @staticmethod
    def are_images_equal(path1: Path, path2: Path) -> bool:
        """Check if two image files are visually equal pixel-wise

        Args:
            path1: image1 file path
            path2: image2 file path

        Returns:
            bool: True - visually equal, False - not visually equal
        """
        data1, meta1 = Common.get_image_data(path1)
        data2, meta2 = Common.get_image_data(path2)

        s1 = f"{path1}:\n{json.dumps(meta1, indent=2, default=Common.jsn_serial)}"
        log.debug(s1)
        s2 = f"{path2}:\n{json.dumps(meta2, indent=2, default=Common.jsn_serial)}"
        log.debug(s2)
        is_equal = ImageChops.difference(data1, data2).getbbox() is None
        log.debug(f"{is_equal=}")
        return is_equal

    @staticmethod
    def get_crop_box(width, height, border_width) -> tuple[float, float, float, float]:
        """Get the crop box tuple

        Args:
            width: image width int
            height: image height int
            border_width: border width int

        Returns:
            tuple[float, float, float, float]
        """
        crop_left = border_width
        crop_top = border_width
        crop_right = width - border_width
        crop_bottom = height - border_width
        return crop_left, crop_top, crop_right, crop_bottom

    @staticmethod
    def calculate_new_size(width: int, height: int, max_len: int) -> tuple[int, int]:
        """Calculate the new size with the same aspect ratio

        Args:
            width: image width int
            height: image height int
            max_len: max length int

        Returns:
            tuple: new_width, new_height
        """
        # Calculate to keep aspect ratio
        if width > height:
            ratio = max_len / width
        else:
            ratio = max_len / height
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return new_width, new_height

    @staticmethod
    def prepare_all_files(in_path: Path, out_path: Path | str):
        """

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE

        Returns:
            iterable: files list generator
        """
        if out_path and out_path != REPLACE:
            out_path.mkdir(parents=True, exist_ok=True)
        # Fix Path.glob() got 2x count on Windows 10
        tmp = [in_path.glob(p, case_sensitive=True) for p in PATTERNS]
        _files = itertools.chain.from_iterable(set(tmp))
        return _files

    @staticmethod
    def executor_progress(
        func, desc: str, tasks: list, quiet: bool = False, results: list | None = None
    ) -> int:
        """ProcessPoolExecutor / ThreadPoolExecutor + progress bar

        Args:
            func: function to be run in multiprocess
            desc: description str
            tasks: tasks list for multiprocess pool
            quiet: suppress progress and error output
            results: optional list to receive successful task results

        Returns:
            int: success_cnt
        """
        success_cnt = 0
        all_cnt = len(tasks)
        workers = min((os.process_cpu_count() or 1) + 4, all_cnt)
        log.info(f"workers: {workers}")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(func, task) for task in tasks]
            with tqdm(total=len(futures), desc=desc, disable=quiet) as pbar:
                # as_completed to iterate over futures as they finish
                for future in as_completed(futures):
                    ok, res = future.result()
                    if ok:
                        success_cnt += 1
                        if results is not None:
                            results.append(res)
                    elif not quiet:
                        tqdm.write(f"error: {res}")
                    pbar.update(1)
        return success_cnt

    @staticmethod
    def set_out_file(in_path: Path, out_path: Path | str, extra: str = "") -> Path:
        """Set the output file path

        Args:
            in_path: input file path
            out_path: output dir path
            extra: extra str in output file name

        Returns:
            Path:
        """
        if not out_path:
            return Path(f"{in_path.parent}/{in_path.stem}_{extra}{in_path.suffix}")
        if out_path == REPLACE:
            return Path(f"{in_path.parent}/{in_path.stem}_tmp{in_path.suffix}")
        out_path.expanduser().mkdir(parents=True, exist_ok=True)
        filename = f"{in_path.stem}_{extra}{in_path.suffix}"
        return Path(f"{out_path}/{filename}")

    @staticmethod
    def set_log_by_process() -> None:
        """Do log setting in a worker process.
        loguru config doesn’t propagate across processes.

        Returns:
            None
        """
        if current_process().name != "MainProcess":
            Log.set_worker_log()
