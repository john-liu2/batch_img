"""Test no_gps.py
pytest -sv tests/test_no_gps.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.no_gps import NoGps

_dir = dirname(__file__)


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/JPG/P1040566.jpeg"),
            Path(f"{_dir}/.out/"),
            (
                True,
                f"Skip as no EXIF in {str(Path(f'{_dir}/data/JPG/P1040566.jpeg'))}",
            ),
        ),
        (
            Path(f"{_dir}/data/HEIC/IMG_0131.HEIC"),
            Path(f"{_dir}/.out/"),
            (
                True,
                f"No 'GPS' in EXIF of {str(Path(f'{_dir}/data/HEIC/IMG_0131.HEIC'))}",
            ),
        ),
    ]
)
def data_remove_1_image_gps(request):
    return request.param


def test_remove_1_image_gps(data_remove_1_image_gps):
    in_path, out_path, expected = data_remove_1_image_gps
    actual = NoGps.remove_1_image_gps((in_path, out_path))
    assert actual == expected


@patch("PIL.Image.open")
def test_error_remove_1_image_gps(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = NoGps.remove_1_image_gps((Path("in/file"), Path("out/file")))
    assert actual[0] is False


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/mixed"),
            Path(f"{_dir}/.out/"),
            True,
        ),
    ]
)
def data_remove_all_images_gps(request):
    return request.param


def test_remove_all_images_gps(data_remove_all_images_gps):
    in_path, out_path, expected = data_remove_all_images_gps
    actual = NoGps.remove_all_images_gps(in_path, out_path)
    assert actual == expected
