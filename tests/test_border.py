"""Test border.py
pytest -sv tests/test_border.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.border import Border


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            9,
            "green",
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_bw9.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            18,
            "purple",
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_bw18.PNG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/JPG/152.JPG"),
            Path(f"{dirname(__file__)}/.out/"),
            4,
            "#AABBCC",
            (True, Path(f"{dirname(__file__)}/.out/152_bw4.JPG")),
        ),
    ]
)
def data_add_border_1_image(request):
    return request.param


def test_add_border_1_image(data_add_border_1_image):
    in_path, out_path, bd_width, bd_color, expected = data_add_border_1_image
    actual = Border.add_border_1_image(in_path, out_path, bd_width, bd_color)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_add_border_1_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Border.add_border_1_image(Path("img/file"), Path("out/path"), 9, "red")
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            9,
            "#CCBBAA",
            True,
        )
    ]
)
def data_add_border_all_in_dir(request):
    return request.param


def test_add_border_all_in_dir(data_add_border_all_in_dir):
    in_path, out_path, bd_width, bd_color, expected = data_add_border_all_in_dir
    actual = Border.add_border_all_in_dir(in_path, out_path, bd_width, bd_color)
    assert actual == expected
