"""Test exif.py
pytest -sv tests/test_exif.py
Copyright © 2026 - Present, John Liu
"""

import struct
import pytest
from PIL import Image
from batch_img.exif import Exif


@pytest.fixture
def temp_images(tmp_path):
    paths = {}

    # PNG (100x50, RGBA)
    png_path = tmp_path / "test.png"
    Image.new("RGBA", (100, 50), color="red").save(png_path, format="PNG")
    paths["PNG"] = png_path

    # JPEG (80x40, RGB, 4:2:0)
    jpg_path = tmp_path / "test.jpg"
    Image.new("RGB", (80, 40), color="blue").save(
        jpg_path, format="JPEG", subsampling="4:2:0"
    )
    paths["JPEG"] = jpg_path

    # TIFF (60x30, RGB)
    tiff_path = tmp_path / "test.tiff"
    Image.new("RGB", (60, 30), color="green").save(tiff_path, format="TIFF")
    paths["TIFF"] = tiff_path

    # WEBP (120x60, RGB)
    webp_path = tmp_path / "test.webp"
    Image.new("RGB", (120, 60), color="yellow").save(webp_path, format="WEBP")
    paths["WEBP"] = webp_path

    # Synthetic HEIC (200x100)
    heic_path = tmp_path / "test.heic"
    heic_bytes = (
        b"\x00\x00\x00\x14ftypheic\x00\x00\x00\x00heicmif1"
        b"\x00\x00\x00\x10ispe\x00\x00\x00\x00" + struct.pack(">II", 200, 100)
    )
    heic_path.write_bytes(heic_bytes)
    paths["HEIC"] = heic_path

    return paths


def test_parse_raw_header_public_api(temp_images):
    for fmt, path in temp_images.items():
        data = path.read_bytes()
        meta = Exif.parse_raw_header(data)
        assert meta["format"] == fmt


def test_parse_raw_header_invalid_inputs():
    assert Exif.parse_raw_header(b"") == {}
    assert Exif.parse_raw_header(b"UNSUPPORTED_HEADER_BYTES") == {}


def test_parse_png(temp_images):
    data = temp_images["PNG"].read_bytes()
    meta = Exif._parse_png(data)
    assert meta == {
        "format": "PNG",
        "size": (100, 50),
        "bit_depth": 8,
        "mode": "RGBA",
    }
    assert Exif._parse_png(b"invalid_png") == {}


def test_parse_jpeg(temp_images):
    data = temp_images["JPEG"].read_bytes()
    meta = Exif._parse_jpeg(data)
    assert meta["format"] == "JPEG"
    assert meta["size"] == (80, 40)
    assert meta["bit_depth"] == 8
    assert meta["mode"] == "RGB"
    assert meta.get("chroma") == "4:2:0"
    assert Exif._parse_jpeg(b"invalid_jpeg") == {}


def test_parse_tiff(temp_images):
    data = temp_images["TIFF"].read_bytes()
    meta = Exif._parse_tiff(data)
    assert meta["format"] == "TIFF"
    assert meta["size"] == (60, 30)
    assert meta["bit_depth"] == 8
    assert Exif._parse_tiff(b"invalid_tiff") == {}


def test_parse_webp(temp_images):
    data = temp_images["WEBP"].read_bytes()
    meta = Exif._parse_webp(data)
    assert meta["format"] == "WEBP"
    assert meta["size"] == (120, 60)
    assert meta["bit_depth"] == 8
    assert Exif._parse_webp(b"invalid_webp") == {}


def test_parse_heic(temp_images):
    data = temp_images["HEIC"].read_bytes()
    meta = Exif._parse_heic(data)
    assert meta == {
        "format": "HEIC",
        "size": (200, 100),
        "bit_depth": 8,
        "mode": "RGB",
    }
    assert Exif._parse_heic(b"invalid_heic") == {}
