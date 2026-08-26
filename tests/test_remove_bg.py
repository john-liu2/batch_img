"""Test remove_bg.py
pytest -sv tests/test_remove_bg.py
Copyright © 2025 - Present, John Liu
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.remove_bg import RemoveBg

# Use pathlib for directory resolution to avoid OS slash mismatches
_dir = Path(__file__).parent


@pytest.fixture(
    params=[
        (
            _dir / "data" / "JPG" / "IMG_0131.jpg",
            _dir / ".out",
            (True, _dir / ".out" / "IMG_0131_NoBg.png"),
        ),
        (
            _dir / "data" / "HEIC" / "IMG_0070.HEIC",
            _dir / ".out",
            (True, _dir / ".out" / "IMG_0070_NoBg.HEIC"),
        ),
        (
            _dir / "data" / "PNG" / "LagrangePoints.png",
            _dir / ".out",
            (True, _dir / ".out" / "LagrangePoints_NoBg.png"),
        ),
        (
            _dir / "data" / "HEIC" / "Cartoon.heic",
            _dir / ".out",
            (True, _dir / ".out" / "Cartoon_NoBg.heic"),
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
    # Native path joining to ensure cross-platform string equality during test failure
    actual = RemoveBg.remove_bg_image((Path("in") / "file", Path("out") / "file"))
    assert actual[0] is False


@pytest.fixture(
    params=[
        (
            _dir / "data" / "mixed",
            _dir / ".out",
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
