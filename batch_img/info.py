"""Get image file(s) meta and EXIF info.
Copyright © 2026 - Present, John Liu
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TextIO

from loguru import logger as log

from batch_img.common import Common
from batch_img.const import EXIF, UNKNOWN

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
            _, meta = Common.get_image_data(file)
            result = {
                "file_info": {
                    "file_size": meta.get("file_size", UNKNOWN),
                    "last_modified": meta.get("file_ts", UNKNOWN),
                    "format": meta.get("format", UNKNOWN),
                    "dimensions": f"{meta['size'][0]} x {meta['size'][1]}",
                    "bit_depth": meta["info"].get("bit_depth", UNKNOWN),
                    "alpha_channel": "Yes" if meta["mode"] in {"RGBA", "LA"} else "No",
                    "colorspace": meta.get("mode", UNKNOWN),
                    "chroma_format": meta["info"].get("chroma", UNKNOWN),
                },
                EXIF: meta[EXIF],
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
                Info._output_exif_info(file, results[file], idx, len(files))

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
                Info._output_exif_info(file, results[file], idx, len(files), output)

    @staticmethod
    def _output_exif_info(
        file: Path, data: dict, index: int, total: int, output: TextIO | None = None
    ) -> None:
        """Format and output EXIF information to either a file or stdout.

        Args:
            file: Image file path
            data: Dictionary containing file_info and exif data
            index: Current file index (1-based)
            total: Total number of files
            output: File object to write to. If None, prints to logger.
        """

        def _out(text: str) -> None:
            """Helper to route string output dynamically."""
            if output:
                output.write(text + "\n")
            else:
                log.info(text)

        file_info = data.get("file_info", {})
        exif = data.get(EXIF, {})

        # Output separator and file header
        _out("─" * 60)
        _out(f"{file} [{index}/{total}]")

        # Output file info
        _out(
            f"  File Size       : {Common.easy_file_sz(file_info.get('file_size', 0))}"
        )
        _out(f"  Last Modified   : {file_info.get('last_modified', 'Unknown')}")
        _out(f"  Format          : {file_info.get('format', 'Unknown')}")
        _out(f"  Dimensions      : {file_info.get('dimensions', 'Unknown')}")
        _out(f"  Bit Depth       : {file_info.get('bit_depth', 'Unknown')}")
        _out(f"  Alpha Channel   : {file_info.get('alpha_channel', 'Unknown')}")
        _out(f"  Colorspace      : {file_info.get('colorspace', 'Unknown')}")
        _out(f"  Chroma Format   : {file_info.get('chroma_format', 'Unknown')}")

        # Output EXIF metadata
        _out("")
        _out("  [ EXIF Metadata ]")

        if not exif:
            _out("    None")

        # Map EXIF tags to friendly names
        exif_map = {
            "Make": "Make",
            "Model": "Model",
            "DateTime": "Date/Time",
            "ISOSpeedRatings": "ISO Speed",
            "ExposureTime": "Exposure",
            "FNumber": "Aperture",
            "FocalLength": "Focal Length",
            "FocalLengthIn35mmFilm": "Focal Length",
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
                elif key == "FocalLengthIn35mmFilm" and isinstance(value, (float, int)):
                    value = f"{value / 3.55:.3f} mm"
                elif key == "ISOSpeedRatings" and isinstance(value, (int, str)):
                    value = f"ISO {value}"

                _out(f"    {label:<15}: {value}")
