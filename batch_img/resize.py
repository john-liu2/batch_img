"""class Resize: resize the image file(s)
Copyright © 2025 John Liu
"""

import itertools
from multiprocessing import Pool, cpu_count
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger
from PIL import Image
from tqdm import tqdm

pillow_heif.register_heif_opener()  # allow Pillow to open HEIC files


class Resize:
    @staticmethod
    def resize_an_image(in_path: Path, out_path: Path, length: int) -> tuple:
        """Resize an image file and save to the output dir

        Args:
            in_path: input file path
            out_path: output dir path
            length: max length (width or height) in pixels

        Returns:
            tuple: bool, output file path
        """
        try:
            with Image.open(in_path) as img:
                max_size = (length, length)
                # The thumbnail() keeps the original aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                out_path.mkdir(parents=True, exist_ok=True)
                out_file = out_path
                if out_path.is_dir():
                    filename = f"{in_path.stem}_{length}{in_path.suffix}"
                    out_file = Path(f"{out_path}/{filename}")

                exif_dict = None
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                # Save to the same format: HEIF, JPEG, PNG, etc.
                if exif_dict:
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(out_file, img.format, optimize=True, exif=exif_bytes)
                else:
                    img.save(out_file, img.format, optimize=True)
            logger.info(f"Saved {out_file}")
            return True, out_file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def resize_all_progress_bar(in_path: Path, out_path: Path, length: int) -> bool:
        """Resize all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path
            length: max length (width or height) in pixels

        Returns:
            bool: True - Success. False - Error
        """
        out_path.mkdir(parents=True, exist_ok=True)
        patterns = (
            "*.HEIC",
            "*.heic",
            "*.JPG",
            "*.jpg",
            "*.JPEG",
            "*.jpeg",
            "*.PNG",
            "*.png",
        )
        image_files = itertools.chain.from_iterable(in_path.glob(p) for p in patterns)
        if not image_files:
            logger.error(f"No image files at {in_path}")
            return False
        tasks = [
            (
                in_path / f,
                out_path,
                length,
            )
            for f in image_files
        ]
        success_cnt = 0
        files_cnt = len(tasks)
        # Limit to 4 workers if cpu cores cnt > 4
        workers = min(cpu_count(), 4)

        logger.info(f"Resize {files_cnt} image files with {workers} workers...")
        with Pool(workers) as pool:
            with tqdm(total=files_cnt, desc="Resize image files") as pbar:
                for ok, res in pool.starmap(Resize.resize_an_image, tasks):
                    if ok:
                        success_cnt += 1
                    else:
                        tqdm.write(f"Error: {res}")
                    pbar.update()
        logger.info(f"\nSuccessfully resized {success_cnt}/{files_cnt} files")
        return True
