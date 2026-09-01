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
            w = meta["size"][0]
            h = meta["size"][1]
            mp = round(w * h / 1_000_000.0, 1)
            bit_depth = meta["info"].get("bit_depth", UNKNOWN)
            if bit_depth != UNKNOWN:
                bit_depth = f"{bit_depth} bits/channel"
            result = {
                "file_info": {
                    "file_size": meta.get("file_size", UNKNOWN),
                    "last_modified": meta.get("file_ts", UNKNOWN),
                    "format": meta.get("format", UNKNOWN),
                    "dimensions": f"{w} x {h} ({mp} MP)",
                    "bit_depth": bit_depth,
                    "alpha_channel": "Yes" if meta["mode"] in {"RGBA", "LA"} else "No",
                    "colorspace": meta.get("mode", UNKNOWN),
                    "chroma_format": meta["info"].get("chroma", UNKNOWN),
                },
                EXIF: meta.get(EXIF, {}),
            }
            return True, (file, result)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return False, f"{file}: {exc}"

    @staticmethod
    def exif_output_path() -> Path:
        """Return the quiet-mode EXIF report path in the working directory."""
        return Path.cwd() / INFO_TXT_FILE

    @staticmethod
    def do_output(success_cnt: int, total: int, results: dict, quiet: bool) -> bool:
        """
        Output EXIF metadata

        Args:
            success_cnt: success readings count
            total: total input files count
            results: Dictionary of file paths to results
            quiet: If True, write formatted results to a file instead of stdout

        Returns:
            bool: True if all images were processed successfully, False otherwise
        """
        if quiet:  # dump to a file if --quiet
            output_file = Info.exif_output_path()
            try:
                with open(output_file, "w", encoding="utf-8") as output:
                    Info.write_formatted_info(output, total, results)
                log.info(f"EXIF information written to {output_file}")
                return success_cnt == total
            except OSError as exc:
                log.error(f"Failed to write EXIF information to {output_file}: {exc}")
                return False

        # Print to stdout
        Info.write_formatted_info(None, total, results)
        log.info(f"Read meta info from {success_cnt}/{total} files")
        return success_cnt == total

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
        total = len(files)
        results = dict(sorted(results.items()))  # sort results for deterministic output
        return Info.do_output(success_count, total, results, quiet)

    @staticmethod
    def write_formatted_info(obj: TextIO | None, total: int, results: dict) -> None:
        """Write formatted EXIF information to a file.

        Args:
            obj: File object to write to. If None, prints to logger.
            total: total input files count
            results: Dictionary of file paths to results
        """
        idx = 1
        for file, data in results.items():
            Info.out_meta_info(file, data, idx, total, obj)
            idx += 1

    @staticmethod
    def _out(text: str, obj: TextIO | None = None) -> None:
        """Helper to route string output dynamically.

        Args:
            text: Text to write
            obj: File object to write to. If None, prints to logger.
        """
        if obj:
            obj.write(text + "\n")
        else:
            log.info(text)

    @staticmethod
    def out_meta_info(
        file: Path, data: dict, index: int, total: int, obj: TextIO | None
    ) -> None:
        """Format and output meta information to a file or stdout.

        Args:
            file: Image file path
            data: Dictionary containing file_info and exif data
            index: Current file index (1-based)
            total: Total number of files
            obj: File object to write to. If None, prints to logger.
        """
        file_info = data.get("file_info", {})
        exif = data.get(EXIF, {})

        # Output separator and file header
        Info._out("─" * 60, obj)
        Info._out(f"{file} [{index}/{total}]", obj)

        # Output file info
        Info._out(f"  File Size       : {file_info.get('file_size', UNKNOWN)}", obj)
        Info._out(f"  Last Modified   : {file_info.get('last_modified', UNKNOWN)}", obj)
        Info._out(f"  Format          : {file_info.get('format', UNKNOWN)}", obj)
        Info._out(f"  Dimensions      : {file_info.get('dimensions', UNKNOWN)}", obj)
        Info._out(f"  Bit Depth       : {file_info.get('bit_depth', UNKNOWN)}", obj)
        Info._out(f"  Alpha Channel   : {file_info.get('alpha_channel', UNKNOWN)}", obj)
        Info._out(f"  Colorspace      : {file_info.get('colorspace', UNKNOWN)}", obj)
        Info._out(f"  Chroma Format   : {file_info.get('chroma_format', UNKNOWN)}", obj)

        # Output EXIF metadata
        Info._out("", obj)
        Info._out("  [ EXIF Metadata ]", obj)

        if not exif:
            Info._out("    None (or unreadable EXIF header)", obj)
            Info._out("", obj)
            return
        Info.print_exif(exif, obj)

    @staticmethod
    def out_pairs(exif: dict, label_map: dict, obj: TextIO | None) -> bool:
        """Output metadata key value pairs

        Args:
            exif: exif data in dict
            label_map: key to output label mapping
            obj: File object to write to. If None, prints to logger.
        """
        found_any = False
        for key, label in label_map.items():
            value = exif.get(key, None)
            if key == "GPSLatitude":
                value = "Present" if value else "Absent"
            elif key == "ExposureTime" and isinstance(value, tuple):
                value = f"{value[0]}/{value[1]} s"
                found_any = True
            elif key == "ExposureTime" and isinstance(value, float):
                found_any = True
                value = f"1/{int(1 / value)} s" if value < 1 else f"{value} s"
            elif key == "FNumber" and isinstance(value, tuple):
                value = f"f/{value[0] / value[1]:.2f}".rstrip("0").rstrip(".")
                found_any = True
            elif key == "FNumber" and isinstance(value, (float, int)):
                value = f"f/{value:.2f}".rstrip("0").rstrip(".")
                found_any = True
            elif key == "FocalLength" and isinstance(value, tuple):
                value = f"{value[0] / value[1]:.2f} mm"
                found_any = True
            elif key == "FocalLength" and isinstance(value, (float, int)):
                value = f"{value:.2f} mm"
                found_any = True
            elif key == "ISOSpeedRatings" and isinstance(value, (int, str)):
                value = f"ISO {value}"
                found_any = True

            if value:
                Info._out(f"    {label:<15}: {value}", obj)
        return found_any

    @staticmethod
    def print_exif(exif: dict, obj: TextIO | None) -> None:
        """Print EXIF data

        Args:
            exif: exif data in dict
            obj: File object to write to. If None, prints to logger.
        """
        label_map = {
            "Make": "Make",
            "Model": "Model",
            "DateTime": "Date/Time",
            "ISOSpeedRatings": "ISO Speed",
            "ExposureTime": "Exposure",
            "FNumber": "Aperture",
            "FocalLength": "Focal Length",
            "GPSLatitude": "GPS Data",
        }
        found_any = Info.out_pairs(exif, label_map, obj)
        if not found_any:
            Info._out("    No standard camera tags found in EXIF", obj)
        Info._out("", obj)
