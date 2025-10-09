"""Test border.py
pytest -sv tests/test_border.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.border import Border
from batch_img.const import REPLACE

_dir = dirname(__file__)


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{_dir}/.out/"),
            9,
            "green",
            (True, Path(f"{_dir}/.out/IMG_0070_bw9.HEIC")),
        ),
        (
            Path(f"{_dir}/data/PNG/Checkmark.PNG"),
            Path(f"{_dir}/.out/"),
            18,
            "purple",
            (True, Path(f"{_dir}/.out/Checkmark_bw18.PNG")),
        ),
        (
            Path(f"{_dir}/data/JPG/152.JPG"),
            Path(f"{_dir}/.out/"),
            4,
            "#AABBCC",
            (True, Path(f"{_dir}/.out/152_bw4.JPG")),
        ),
    ]
)
def data_border_1_image(request):
    return request.param


def test_border_1_image(data_border_1_image):
    in_path, out_path, bd_width, bd_color, expected = data_border_1_image
    actual = Border.border_1_image((in_path, out_path, bd_width, bd_color))
    assert actual == expected


@pytest.mark.slow(reason="This test modifies test data file.")
def test_border_1_image_replace():
    in_path = Path(f"{_dir}/data/PNG/Checkmark.PNG")
    actual = Border.border_1_image((in_path, REPLACE, 9, "red"))
    assert actual == (True, in_path)


@patch("PIL.Image.open")
def test_error_add_border_1_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Border.border_1_image((Path("img/file"), Path("out/path"), 9, "red"))
    # For Windows & macOS
    assert str(Path("img/file")) in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/mixed"),
            Path(f"{_dir}/.out/"),
            9,
            "#CCBBAA",
            True,
        ),
        (
            Path(f"{_dir}/data/JPG"),
            Path(f"{_dir}/.out/"),
            5,
            "green",
            True,
        ),
    ]
)
def data_add_border_all_in_dir(request):
    return request.param


def test_add_border_all_in_dir(data_add_border_all_in_dir):
    in_path, out_path, bd_width, bd_color, expected = data_add_border_all_in_dir
    actual = Border.border_all_in_dir(in_path, out_path, bd_width, bd_color)
    assert actual == expected
