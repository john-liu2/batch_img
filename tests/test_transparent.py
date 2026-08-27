"""Test transparent.py
pytest -sv tests/test_transparent.py
Copyright © 2025 - Present, John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from batch_img.const import REPLACE
from batch_img.transparent import Transparent

_dir = dirname(__file__)


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{_dir}/.out/"),
            255,
            True,
            (True, Path(f"{_dir}/.out/IMG_0070_a255w.HEIC")),
        ),
        (
            Path(f"{_dir}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{_dir}/.out/"),
            127,
            False,
            (True, Path(f"{_dir}/.out/IMG_0070_a127.HEIC")),
        ),
        (
            Path(f"{_dir}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{_dir}/.out/"),
            64,
            False,
            (True, Path(f"{_dir}/.out/IMG_0070_a64.HEIC")),
        ),
        (
            Path(f"{_dir}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{_dir}/.out/"),
            0,
            False,
            (True, Path(f"{_dir}/.out/IMG_0070_a0.HEIC")),
        ),
        (
            Path(f"{_dir}/data/JPG/IMG_2527.jpg"),
            Path(f"{_dir}/.out/"),
            127,
            False,
            (True, Path(f"{_dir}/.out/IMG_2527_a127.png")),
        ),
        (
            Path(f"{_dir}/data/JPG/IMG_2527.jpg"),
            Path(f"{_dir}/.out/"),
            127,
            True,
            (True, Path(f"{_dir}/.out/IMG_2527_a127w.png")),
        ),
        (
            Path(f"{_dir}/data/PNG/Checkmark.PNG"),
            Path(f"{_dir}/.out/"),
            0,
            False,
            (True, Path(f"{_dir}/.out/Checkmark_a0.PNG")),
        ),
        (
            Path(f"{_dir}/data/PNG/Checkmark.PNG"),
            Path(f"{_dir}/.out/"),
            64,
            True,
            (True, Path(f"{_dir}/.out/Checkmark_a64w.PNG")),
        ),
        (
            Path(f"{_dir}/data/PNG/Checkmark.PNG"),
            Path(f"{_dir}/.out/"),
            127,
            False,
            (True, Path(f"{_dir}/.out/Checkmark_a127.PNG")),
        ),
        (
            Path(f"{_dir}/data/PNG/Checkmark.PNG"),
            Path(f"{_dir}/.out/"),
            255,
            True,
            (True, Path(f"{_dir}/.out/Checkmark_a255w.PNG")),
        ),
    ]
)
def data_1_image_transparency(request):
    return request.param


def test_do_1_image_transparency(data_1_image_transparency):
    in_path, out_path, transparency, white, expected = data_1_image_transparency
    actual = Transparent.do_1_image_transparency(
        (
            in_path,
            out_path,
            transparency,
            white,
        )
    )
    assert actual == expected


@pytest.mark.slow(reason="This test modifies test data file.")
def test_do_1_image_transparency_replace():
    in_path = Path("~/Downloads/Cartoon_1024.heic").expanduser()
    actual = Transparent.do_1_image_transparency((in_path, REPLACE, 0, False))
    assert actual == (True, in_path)


@patch("PIL.Image.open")
def test_error_do_1_image_transparency(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Transparent.do_1_image_transparency(
        (
            Path("img/file"),
            Path("out/path"),
            33,
            True,
        )
    )
    # For Windows & macOS
    assert str(Path("img/file")) in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/PNG"),
            Path(f"{_dir}/.out/"),
            234,
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


def test_set_white_pixel_transparent():
    """Verify white pixels are set to full transparency using Pillow >= 12.1.0."""
    img = Image.new("RGBA", (2, 2))
    img.putdata(
        [(255, 255, 255, 255), (255, 0, 0, 255), (255, 255, 255, 128), (0, 255, 0, 255)]
    )

    Transparent.set_white_pixel_transparent(img)
    data = img.get_flattened_data()

    assert data[0] == (255, 255, 255, 0)
    assert data[1] == (255, 0, 0, 255)
    assert data[2] == (255, 255, 255, 0)
    assert data[3] == (0, 255, 0, 255)


def test_set_transparency():
    """Verify the global alpha channel overrides using Pillow >= 12.1.0."""
    img = Image.new("RGBA", (2, 2))
    img.putdata(
        [(255, 255, 255, 255), (255, 0, 0, 255), (0, 0, 0, 0), (100, 100, 100, 128)]
    )

    Transparent.set_transparency(img, 64)

    for p in img.get_flattened_data():
        assert p[3] == 64
