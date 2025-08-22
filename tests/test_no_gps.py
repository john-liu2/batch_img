"""Test no_gps.py
pytest -sv tests/test_no_gps.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.no_gps import NoGps, REPLACE


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/JPG/P1040566.jpeg"),
            Path(f"{dirname(__file__)}/.out/"),
            (
                True,
                f"Skip as no EXIF in {dirname(__file__)}/data/JPG/P1040566.jpeg",
            ),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0131.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            (
                True,
                f"No 'GPS' in EXIF of {dirname(__file__)}/data/HEIC/IMG_0131.HEIC",
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
