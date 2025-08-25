"""Test transparent.py
pytest -sv tests/test_transparent.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.const import REPLACE
from batch_img.transparent import Transparent


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            255,
            # Non PNG got err on white pixels: not enough values to unpack (expected 4, got 3)
            True,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_a255.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            127,
            False,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_a127.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            64,
            False,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_a64.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            0,
            False,
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_a0.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/JPG/IMG_2527.jpg"),
            Path(f"{dirname(__file__)}/.out/"),
            127,
            False,
            (True, Path(f"{dirname(__file__)}/.out/IMG_2527_a127.png")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            0,
            False,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_a0.PNG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            64,
            True,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_a64w.PNG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            127,
            False,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_a127.PNG")),
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            255,
            True,
            (True, Path(f"{dirname(__file__)}/.out/Checkmark_a255w.PNG")),
        ),
    ]
)
def data_1_image_transparency(request):
    return request.param


def test_do_1_image_transparency(data_1_image_transparency):
    in_path, out_path, transparency, white, expected = data_1_image_transparency
    actual = Transparent.do_1_image_transparency(
        (in_path, out_path, transparency, white)
    )
    assert actual == expected


@pytest.mark.slow(reason="This test modifies test data file.")
def test_do_1_image_transparency_replace():
    in_path = Path(f"~/Downloads/Cartoon_1024.heic").expanduser()
    actual = Transparent.do_1_image_transparency((in_path, REPLACE, 0, False))
    assert actual == (True, in_path)


@patch("PIL.Image.open")
def test_error_do_1_image_transparency(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Transparent.do_1_image_transparency(
        (Path("img/file"), Path("out/path"), 33, True)
    )
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            128,
            True,
            True,
        )
    ]
)
def data_all_transparency(request):
    return request.param


def test_all_images_transparency(data_all_transparency):
    in_path, out_path, transparency, white, expected = data_all_transparency
    actual = Transparent.all_images_transparency(in_path, out_path, transparency, white)
    assert actual == expected
