"""Test remove_bg.py
pytest -sv tests/test_remove_bg.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.remove_bg import RemoveBg


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/JPG/IMG_0131.jpg"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/IMG_0131_NoBg.png")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_NoBg.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/LagrangePoints.png"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/LagrangePoints_NoBg.png")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/Cartoon_NoBg.heic")),
        ),
    ]
)
def data_remove_bg_image(request):
    return request.param


def test_remove_bg_image(data_remove_bg_image):
    in_file, out_path, expected = data_remove_bg_image
    actual = RemoveBg.remove_bg_image((in_file, out_path))
    assert actual == expected


@patch("PIL.Image.open")
def test_error_remove_bg_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = RemoveBg.remove_bg_image((Path("in/file"), Path("out/file")))
    assert actual[0] is False


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            True,
        ),
    ]
)
def data_remove_all_images_bg(request):
    return request.param


def test_remove_all_images_bg(data_remove_all_images_bg):
    in_path, out_path, expected = data_remove_all_images_bg
    actual = RemoveBg.remove_all_images_bg(in_path, out_path)
    assert actual == expected
