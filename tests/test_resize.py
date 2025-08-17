"""Test resize.py
pytest -sv tests/test_resize.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.common import Common
from batch_img.resize import Resize


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            1024,
            Path(f"{dirname(__file__)}/.out/IMG_0070_1024.HEIC"),
        )
    ]
)
def data_resize_an_image(request):
    return request.param


def test_resize_an_image(data_resize_an_image):
    in_file, out_path, max_side, expected = data_resize_an_image
    actual = Resize.resize_an_image(in_file, out_path, max_side)
    assert actual == expected
    # assert Common.are_images_equal(in_file, actual) is False


@patch("PIL.Image.open")
def test_resize_an_image_error(mock_open):
    mock_open.side_effect = ValueError("VE")
    with pytest.raises(ValueError):
        Resize.resize_an_image(Path("in/file"), Path("out/file"), 800)
