"""Test do_effect.py
pytest -sv tests/test_do_effect.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.do_effect import DoEffect


@pytest.fixture(
    params=[
        # (
        #     Path("~/Documents/IMG_0231.HEIC"),
        #     "",
        #     "blur",
        #     (True, Path("~/Documents/IMG_0231_blur.HEIC").expanduser()),
        # ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            "neon",
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_neon.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            "hdr",
            (True, Path(f"{dirname(__file__)}/.out/IMG_0070_hdr.HEIC")),
        ),
        (
            Path(f"{dirname(__file__)}/data/JPG/152.JPG"),
            Path(f"{dirname(__file__)}/.out/"),
            "blur",
            (True, Path(f"{dirname(__file__)}/.out/152_blur.JPG")),
        ),
    ]
)
def data_apply_1_image(request):
    return request.param


def test_apply_1_image(data_apply_1_image):
    in_path, out_path, effect_name, expected = data_apply_1_image
    actual = DoEffect.apply_1_image((in_path, out_path, effect_name))
    assert actual == expected


@patch("PIL.Image.open")
def test_error_apply_1_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = DoEffect.apply_1_image((Path("img/file"), Path("out/path"), "any"))
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/mixed"),
            Path(f"{dirname(__file__)}/.out/"),
            "neon",
            True,
        ),
    ]
)
def data_apply_all_in_dir(request):
    return request.param


def test_add_border_all_in_dir(data_apply_all_in_dir):
    in_path, out_path, effect_name, expected = data_apply_all_in_dir
    actual = DoEffect.apply_all_in_dir(in_path, out_path, effect_name)
    assert actual == expected
