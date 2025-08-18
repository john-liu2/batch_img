"""Test rotate.py
pytest -sv tests/test_rotate.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.rotate import Rotate


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/HEIC/chef_orientation_3.heic"), 3, True),
        (Path(f"{dirname(__file__)}/data/HEIC/chef_orientation_8.heic"), 8, True),
    ]
)
def data_set_exif_orientation(request):
    return request.param


# JL 2025-08-18: not run as the whole pytest as it modifies the test data files
# def test_set_exif_orientation(data_set_exif_orientation):
#     file, o_val, expected = data_set_exif_orientation
#     actual = Rotate.set_exif_orientation(file, o_val)
#     assert actual == expected


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            90,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_90cw.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            180,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_180cw.PNG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/JPG/152.JPG"),
            Path(f"{dirname(__file__)}/.out/"),
            270,
            (True, Path(f"{dirname(__file__)}/.out/152_270cw.JPG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/chef_show2.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            180,
            (True, Path(f"{dirname(__file__)}/.out/chef_show2_180cw.heic")),
        ),
    ]
)
def data_rotate_1_image_file(request):
    return request.param


def test_rotate_1_image_file(data_rotate_1_image_file):
    in_path, out_path, angle, expected = data_rotate_1_image_file
    actual = Rotate.rotate_1_image_file(in_path, out_path, angle)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_rotate_1_image_file(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Rotate.rotate_1_image_file(Path("img/file"), Path("out/path"), 90)
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            90,
            True,
        ),
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            180,
            True,
        ),
    ]
)
def data_rotate_all_in_dir(request):
    return request.param


def test_rotate_all_in_dir(data_rotate_all_in_dir):
    in_path, out_path, angle_cw, expected = data_rotate_all_in_dir
    actual = Rotate.rotate_all_in_dir(in_path, out_path, angle_cw)
    assert actual == expected
