"""Get image file(s) meta and EXIF info.
Copyright © 2026 - Present, John Liu
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF, TS_2_MINUTE

INFO_TXT_FILE = "img_meta_info.txt"


class Info:
    """Read and display EXIF metadata without modifying image files."""

    @staticmethod
    def read_1_image_exif(file: Path) -> tuple[bool, tuple[Path, dict] | str]:
        """Read decoded EXIF metadata from one image.

        Args:
            file: image file path

        Returns:
            tuple: success flag and the image path with EXIF data, or an error message
        """
        try:
            with Image.open(file) as image:
                # Get file info
                m_ts = datetime.fromtimestamp(file.stat().st_mtime).strftime(
                    TS_2_MINUTE
                )
                file_info = {
                    "file_size": file.stat().st_size,
                    "last_modified": m_ts,
                    "format": image.format or "Unknown",
                    "dimensions": f"{image.width}x{image.height}",
                    "bit_depth": image.info.get("bits", "Unknown"),
                    "alpha_channel": "Yes" if image.mode in {"RGBA", "LA"} else "No",
                    "colorspace": image.mode,
                    "chroma_format": image.info.get("chroma", "Unknown"),
                }

                # Get EXIF data
                exif_data = image.info.get(EXIF)
                exif = Common.decode_exif(exif_data) if exif_data else {}

                # Combine file info and EXIF data
                result = {
                    "file_info": file_info,
                    "exif": exif,
                }
            return True, (file, result)
        except (OSError, ValueError) as exc:
            return False, f"{file}: {exc}"

    @staticmethod
    def exif_output_path() -> Path:
        """Return the quiet-mode EXIF report path in the working directory."""
        return Path.cwd() / INFO_TXT_FILE

    @staticmethod
    def read_exif(in_path: Path, quiet: bool = False) -> bool:
        """Read EXIF metadata for an image or all supported images in a directory.

        Image reads run in threads. Results are stored in a dictionary with
        file paths as unique keys. Results are printed in input order after
        all threads complete.

        Args:
            in_path: Path to an image file or directory containing images
            quiet: If True, write formatted results to a file instead of stdout

        Returns:
            bool: True if all images were processed successfully, False otherwise
        """
        files = (
            [in_path]
            if in_path.is_file()
            else list(Common.prepare_all_files(in_path, ""))
        )
        if not files:
            log.error(f"No image files at {in_path}")
            return False

        # Use threading to read EXIF from multiple files
        results = {}
        with ThreadPoolExecutor(max_workers=min(10, len(files))) as executor:
            future_to_file = {
                executor.submit(Info.read_1_image_exif, file): file for file in files
            }

            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    ok, result = future.result()
                    if ok:
                        # result is a tuple (Path, dict) - extract the dict
                        if isinstance(result, tuple) and len(result) == 2:
                            results[file] = result[1]
                        else:
                            results[file] = result
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    log.error(f"Error reading {file}: {exc}")

        success_count = len(results)

        if quiet:
            output_file = Info.exif_output_path()
            try:
                with open(output_file, "w", encoding="utf-8") as output:
                    Info._write_formatted_info(output, files, results)
                log.info(f"EXIF information written to {output_file}")
                return success_count == len(files)
            except OSError as exc:
                log.error(f"Failed to write EXIF information to {output_file}: {exc}")
                return False

        # Print results in input order
        for idx, file in enumerate(files, 1):
            if file in results:
                Info._print_exif_info(file, results[file], idx, len(files))

        log.info(f"Read EXIF from {success_count}/{len(files)} files")
        return success_count == len(files)

    @staticmethod
    def _write_formatted_info(output: TextIO, files: list, results: dict) -> None:
        """Write formatted EXIF information to a file.

        Args:
            output: File object to write to
            files: List of image files
            results: Dictionary of file paths to results
        """
        for idx, file in enumerate(files, 1):
            if file in results:
                Info._write_exif_info(output, file, results[file], idx, len(files))

    @staticmethod
    def _write_exif_info(
        output: TextIO, file: Path, data: dict, index: int, total: int
    ) -> None:
        """Write EXIF information for one file to output.

        Args:
            output: File object to write to
            file: Image file path
            data: Dictionary containing file_info and exif data
            index: Current file index (1-based)
            total: Total number of files
        """
        file_info = data.get("file_info", {})
        exif = data.get("exif", {})

        # Write separator and file header
        output.write("─" * 60 + "\n")
        output.write(f"{file} [{index}/{total}]\n")

        # Write file info
        output.write(
            f"  File Size       : {Info._easy_file_sz(file_info.get('file_size', 0))}\n"
        )
        output.write(
            f"  Last Modified   : {file_info.get('last_modified', 'Unknown')}\n"
        )
        output.write(f"  Format          : {file_info.get('format', 'Unknown')}\n")
        output.write(f"  Dimensions      : {file_info.get('dimensions', 'Unknown')}\n")
        output.write(f"  Bit Depth       : {file_info.get('bit_depth', 'Unknown')}\n")
        output.write(
            f"  Alpha Channel   : {file_info.get('alpha_channel', 'Unknown')}\n"
        )
        output.write(f"  Colorspace      : {file_info.get('colorspace', 'Unknown')}\n")
        output.write(
            f"  Chroma Format   : {file_info.get('chroma_format', 'Unknown')}\n"
        )

        # Write EXIF metadata
        output.write("\n")
        output.write("  [ EXIF Metadata ]\n")

        if exif:
            # Map EXIF tags to friendly names
            exif_map = {
                "Make": "Make",
                "Model": "Model",
                "DateTime": "Date/Time",
                "ISOSpeedRatings": "ISO Speed",
                "ExposureTime": "Exposure",
                "FNumber": "Aperture",
                "FocalLength": "Focal Length",
                "GPSInfo": "GPS Data",
            }

            for key, label in exif_map.items():
                if key in exif:
                    value = exif[key]
                    if key == "GPSInfo":
                        value = "Available" if value else "None"
                    elif key == "ExposureTime" and isinstance(value, tuple):
                        value = f"{value[0]}/{value[1]} s"
                    elif key == "ExposureTime" and isinstance(value, float):
                        if value < 1:
                            value = f"1/{int(1 / value)} s"
                        else:
                            value = f"{value} s"
                    elif key == "FNumber" and isinstance(value, (float, int)):
                        value = f"f/{value:.2f}"
                    elif key == "FocalLength" and isinstance(value, (float, int)):
                        value = f"{value:.2f} mm"
                    elif key == "ISOSpeedRatings" and isinstance(value, (int, str)):
                        value = f"ISO {value}"

                    output.write(f"    {label:<15}: {value}\n")
        else:
            output.write("    None\n")

    @staticmethod
    def json_serial(obj: Any) -> str:
        """JSON serializer for objects not serializable by default json code."""
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        raise TypeError(f"Type {type(obj)} not serializable")

    @staticmethod
    def _print_exif_info(file: Path, data: dict, index: int, total: int) -> None:
        """Print EXIF information in a formatted way.

        Args:
            file: Image file path
            data: Dictionary containing file_info and exif data
            index: Current file index (1-based)
            total: Total number of files
        """
        file_info = data.get("file_info", {})
        exif = data.get("exif", {})

        # Print separator and file header
        log.info("─" * 60)
        log.info(f"{file} [{index}/{total}]")

        # Print file info
        log.info(
            f"  File Size     : {Info._easy_file_sz(file_info.get('file_size', 0))}"
        )
        log.info(f"  Last Modified   : {file_info.get('last_modified', 'Unknown')}")
        log.info(f"  Format          : {file_info.get('format', 'Unknown')}")
        log.info(f"  Dimensions      : {file_info.get('dimensions', 'Unknown')}")
        log.info(f"  Bit Depth       : {file_info.get('bit_depth', 'Unknown')}")
        log.info(f"  Alpha Channel   : {file_info.get('alpha_channel', 'Unknown')}")
        log.info(f"  Colorspace      : {file_info.get('colorspace', 'Unknown')}")
        log.info(f"  Chroma Format   : {file_info.get('chroma_format', 'Unknown')}")

        # Print EXIF metadata
        log.info("")
        log.info("  [ EXIF Metadata ]")

        if exif:
            # Map EXIF tags to friendly names
            exif_map = {
                "Make": "Make",
                "Model": "Model",
                "DateTime": "Date/Time",
                "ISOSpeedRatings": "ISO Speed",
                "ExposureTime": "Exposure",
                "FNumber": "Aperture",
                "FocalLength": "Focal Length",
                "GPSInfo": "GPS Data",
            }

            for key, label in exif_map.items():
                if key in exif:
                    value = exif[key]
                    if key == "GPSInfo":
                        value = "Available" if value else "None"
                    elif key == "ExposureTime" and isinstance(value, tuple):
                        value = f"{value[0]}/{value[1]} s"
                    elif key == "ExposureTime" and isinstance(value, float):
                        if value < 1:
                            value = f"1/{int(1 / value)} s"
                        else:
                            value = f"{value} s"
                    elif key == "FNumber" and isinstance(value, (float, int)):
                        value = f"f/{value:.2f}"
                    elif key == "FocalLength" and isinstance(value, (float, int)):
                        value = f"{value:.2f} mm"
                    elif key == "ISOSpeedRatings" and isinstance(value, (int, str)):
                        value = f"ISO {value}"

                    log.info(f"    {label:<15}: {value}")
        else:
            log.info("    None")

    @staticmethod
    def _easy_file_sz(size: int) -> str:
        """Format file size in human-readable format.

        Args:
            size: File size in bytes

        Returns:
            Formatted file size string
        """
        if size < 1024:
            return f"{size} B ({size} bytes)"
        if size < 1024 * 1024:
            kb = size / 1024
            return f"{kb:.1f} KB ({size} bytes)"
        if size < 1024 * 1024 * 1024:
            mb = size / (1024 * 1024)
            return f"{mb:.1f} MB ({size} bytes)"
        gb = size / (1024 * 1024 * 1024)
        return f"{gb:.1f} GB ({size} bytes)"
