"""Test grayscale.py
pytest -sv tests/test_grayscale.py
Copyright © 2026 - Present, John Liu
"""

from os.path import dirname
from pathlib import Path
import pytest
from PIL import Image
from pillow_heif import register_heif_opener
from unittest.mock import patch

from batch_img.grayscale import Grayscale, REPLACE, SOFTWARE

# Register HEIF/HEIC support for Pillow
register_heif_opener()

_dir = dirname(__file__)


@pytest.mark.parametrize(
    "filename, img_format, overwrite",
    [
        ("test.jpg", "JPEG", False),
        ("test.png", "PNG", False),
        ("test.tiff", "TIFF", False),
        ("test.heic", "HEIF", False),
        ("test.jpg", "JPEG", True),
        ("test.png", "PNG", True),
        ("test.tiff", "TIFF", True),
        ("test.heic", "HEIF", True),
    ],
)
def test_do_one_image(tmp_path, filename, img_format, overwrite):
    # tmp_path is a built-in pytest fixture that provides a temporary directory
    in_path = tmp_path / filename
    out_path = tmp_path / f"gray_{filename}"
    if overwrite:
        out_path = REPLACE

    # Create a base dummy image with mock EXIF data
    img = Image.new("RGB", (100, 100), color="red")
    exif = img.getexif()
    exif[0x0112] = 1  # Orientation tag
    img.save(in_path, format=img_format, exif=exif)

    # Call the method
    args = (Path(in_path), Path(out_path))
    ok, out_file = Grayscale.do_one_image(args)

    assert out_file.exists(), f"Output file for {img_format} was not created."
    with Image.open(out_file) as out_img:
        # Verify Grayscale Mode
        assert out_img.mode == "L", f"{img_format} was not converted to grayscale."

        # Verify EXIF was preserved and updated
        out_exif = out_img.getexif()
        assert out_exif is not None, f"EXIF data stripped from {img_format}."

        # Check original tag preservation (Orientation)
        assert out_exif.get(0x0112) == 1, "Original EXIF tag (Orientation) was lost."

        # Check updated tags (Software and ColorSpace)
        assert out_exif.get(0x0131) == SOFTWARE, "Software EXIF tag was not set."
        assert out_exif.get(0xA001) == 65535, "ColorSpace EXIF tag was not updated."


@patch("PIL.Image.open")
def test_error_do_one_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Grayscale.do_one_image((Path("in/file"), Path("out/file")))
    assert actual[0] is False


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/mixed"),
            Path(f"{_dir}/.out/"),
            True,
        ),
    ]
)
def data_do_all_images(request):
    return request.param


def test_do_all_images(data_do_all_images):
    in_path, out_path, expected = data_do_all_images
    actual = Grayscale.do_all_images(in_path, out_path)
    assert actual == expected
