"""Test orientation.py
pytest -sv tests/test_orientation.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.orientation import Orientation, ORIENTATION_MAP, UNKNOWN


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"), ORIENTATION_MAP[1]),
        (Path(f"{dirname(__file__)}/data/JPG/P1040566.jpeg"), UNKNOWN),
        (Path(f"{dirname(__file__)}/data/PNG/LagrangePoints.png"), UNKNOWN),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"), ORIENTATION_MAP[1]),
    ]
)
def data_get_image_orientation(request):
    return request.param


def test_get_exif_orientation(data_get_image_orientation):
    file, expected = data_get_image_orientation
    actual = Orientation.get_exif_orientation(file)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_get_exif_orientation(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Orientation.get_exif_orientation(Path("img/file"))
    assert "img/file" in actual


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"), 0),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_180cw.heic"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_270cw.heic"), 90),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_90cw.heic"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"), -1),
        (Path(f"{dirname(__file__)}/data/PNG/LagrangePoints.png"), -1),
        (Path(f"{dirname(__file__)}/data/JPG/152.JPG"), -1),
    ]
)
def data_detect_by_face(request):
    return request.param


def test_detect_by_face(data_detect_by_face):
    file, expected = data_detect_by_face
    actual = Orientation().detect_by_face(file)
    assert actual == expected
