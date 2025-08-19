"""Test resize.py
pytest -sv tests/test_resize.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest
from batch_img.const import REPLACE
from batch_img.resize import Resize


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            1024,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_1024.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            1024,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_1024.PNG")),
        ),
    ]
)
def data_resize_an_image(request):
    return request.param


def test_resize_an_image(data_resize_an_image):
    in_file, out_path, max_side, expected = data_resize_an_image
    actual = Resize.resize_an_image(in_file, out_path, max_side)
    assert actual == expected


@pytest.mark.slow(reason="This test modifies test data file.")
def test_resize_an_image_replace():
    in_path = Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG")
    actual = Resize.resize_an_image(in_path, REPLACE, 800)
    assert actual == (True, in_path)


@patch("PIL.Image.open")
def test_error_resize_an_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Resize.resize_an_image(Path("in/file"), Path("out/file"), 800)
    assert actual[0] is False


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            1024,
            True,
        )
    ]
)
def data_resize_all_progress_bar(request):
    return request.param


def test_resize_all_progress_bar(data_resize_all_progress_bar):
    in_path, out_path, length, expected = data_resize_all_progress_bar
    actual = Resize.resize_all_progress_bar(in_path, out_path, length)
    assert actual == expected
