"""Tests for info.py
pytest -sv tests/test_info.py
Copyright © 2025 - Present, John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from batch_img.info import Info, INFO_TXT_FILE
from batch_img.const import EXIF, UNKNOWN

_dir = dirname(__file__)


@pytest.fixture
def mock_meta_data():
    """Returns a standard dictionary representing output from Common.get_image_data"""
    return {
        "file_size": 2048576,
        "file_ts": "2026-08-26 12:00",
        "format": "JPEG",
        "size": (1920, 1080),
        "mode": "RGB",
        "info": {"bit_depth": 8, "chroma": "4:2:0"},
        EXIF: {
            "Make": "Nikon",
            "Model": "D850",
            "ExposureTime": (1, 250),
            "FNumber": 2.8,
            "ISOSpeedRatings": 400,
            "FocalLength": 50.0,
            "GPSInfo": True,
        },
    }


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/HEIC/Cartoon_180cw.heic"),
            {
                "file_info": {
                    "file_size": "42 KB (43386 bytes)",
                    "last_modified": "2025-08-17 11:05",
                    "format": "HEIF",
                    "dimensions": "758 x 758 (0.6 MP)",
                    "bit_depth": "8 bits/channel",
                    "alpha_channel": "No",
                    "colorspace": "RGB",
                    "chroma_format": "4:2:0",
                },
                EXIF: {"ExifTag": 114, "Orientation": 1},
            },
        ),
        (
            Path(f"{_dir}/data/HEIC/IMG_2527.HEIC"),
            {
                "file_info": {
                    "file_size": "153 KB (157123 bytes)",
                    "last_modified": "2026-03-04 11:53",
                    "format": "HEIF",
                    "dimensions": "1920 x 1440 (2.8 MP)",
                    "bit_depth": "8 bits/channel",
                    "alpha_channel": "No",
                    "colorspace": "RGB",
                    "chroma_format": "4:2:0",
                },
                EXIF: {
                    "ColorSpace": 65535,
                    "DateTime": "2023-12-31 15:57",
                    "DateTimeDigitized": "2023:12:31 15:57:52",
                    "DateTimeOriginal": "2023:12:31 15:57:52",
                    "ExifTag": 242,
                    "ExifVersion": "0232",
                    "ExposureMode": 0,
                    "ExposureProgram": 2,
                    "ExposureTime": (
                        1,
                        28571,
                    ),
                    "FNumber": (
                        1244236,
                        699009,
                    ),
                    "Flash": 16,
                    "FocalLength": (
                        251773,
                        37217,
                    ),
                    "FocalLengthIn35mmFilm": 24,
                    "ISOSpeedRatings": 64,
                    "Make": "Apple",
                    "MeteringMode": 5,
                    "Model": "iPhone 15 Pro Max",
                    "Orientation": 1,
                    "SensingMethod": 2,
                    "WhiteBalance": 0,
                },
            },
        ),
    ]
)
def data_read_1_image(request):
    return request.param


class TestReadOneImageExif:
    """Tests for reading EXIF from a single image."""

    def test_read_1_image_exif(self, data_read_1_image):
        file, expected = data_read_1_image
        ok, actual = Info.read_1_image_exif(file)
        assert ok is True
        # Cloud CI runs get different ts
        expected["file_info"].pop("last_modified", None)
        result = actual[1]
        result["file_info"].pop("last_modified", None)  # safely ignore if not exist
        assert result == expected

    @patch("batch_img.info.Common.get_image_data")
    def test_read_1_image_exif_success(self, mock_get_data, mock_meta_data):
        """Test reading EXIF data successfully."""
        file = Path("dummy") / "test_image.jpg"
        # Mock Common.get_image_data to return a dummy image object and our meta dict
        mock_get_data.return_value = (MagicMock(), mock_meta_data)

        ok, result = Info.read_1_image_exif(file)

        assert ok is True
        path, data = result
        assert path == file

        # Verify file_info formatting
        file_info = data["file_info"]
        assert file_info["file_size"] == 2048576
        assert file_info["dimensions"] == "1920 x 1080 (2.1 MP)"
        assert file_info["alpha_channel"] == "No"
        assert file_info["format"] == "JPEG"

        # Verify EXIF
        assert data[EXIF]["Make"] == "Nikon"

    @patch("batch_img.info.Common.get_image_data")
    def test_read_1_image_exif_missing_data(self, mock_get_data):
        """Test reading EXIF data when metadata is sparse."""
        file = Path("dummy") / "test_image.jpg"
        mock_get_data.return_value = (
            MagicMock(),
            {"size": (0, 0), "info": {}, "mode": "L", EXIF: {}},
        )

        ok, result = Info.read_1_image_exif(file)

        assert ok is True
        _, data = result
        assert data["file_info"]["file_size"] == UNKNOWN
        assert data["file_info"]["colorspace"] == "L"
        assert data["file_info"]["alpha_channel"] == "No"

    @patch("batch_img.info.Common.get_image_data")
    def test_read_1_image_exif_os_error(self, mock_get_data):
        """Test error handling when reading an image fails."""
        file = Path("dummy") / "nonexistent.jpg"
        mock_get_data.side_effect = OSError("File not found")

        ok, result = Info.read_1_image_exif(file)

        assert ok is False
        assert isinstance(result, str)
        assert "File not found" in result


class TestReadExif:
    """Tests for the multithreaded EXIF reader and output."""

    @patch("batch_img.info.Common.prepare_all_files")
    @patch("batch_img.info.log.error")
    def test_read_exif_no_files(self, mock_log_error, mock_prepare):
        """Test behavior when no files are found in a directory."""
        mock_prepare.return_value = []
        input_dir = Path("empty_dir")

        result = Info.read_exif(input_dir)

        assert result is False
        # Patch loguru explicitly rather than using caplog
        mock_log_error.assert_called_once_with(f"No image files at {input_dir}")

    @patch("batch_img.info.Info.read_1_image_exif")
    def test_read_exif_single_file_stdout(self, mock_read, tmp_path):
        """Test reading a single file and printing to stdout."""
        # Create an actual physical file so in_path.is_file() evaluates to True
        file = tmp_path / "test.jpg"
        file.touch()

        mock_read.return_value = (
            True,
            (file, {"file_info": {}, EXIF: {"Make": "Sony"}}),
        )

        with patch("batch_img.info.log.info") as mock_log:
            result = Info.read_exif(file, quiet=False)

            assert result is True
            mock_read.assert_called_once_with(file)
            mock_log.assert_any_call("  [ EXIF Metadata ]")

    @patch("batch_img.info.Info.read_1_image_exif")
    def test_read_exif_quiet_mode_writes_file(self, mock_read, tmp_path, monkeypatch):
        """Test quiet mode writes correctly formatted text to a file."""
        # Create an actual physical file
        file = tmp_path / "test.jpg"
        file.touch()

        mock_read.return_value = (
            True,
            (
                file,
                {
                    "file_info": {"file_size": 1024, "format": "PNG"},
                    EXIF: {"Make": "Sony"},
                },
            ),
        )

        output_file = tmp_path / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        result = Info.read_exif(file, quiet=True)

        assert result is True
        assert output_file.exists()

        # Read with .splitlines() to avoid Windows \r\n vs Linux \n assertion failures
        content = output_file.read_text(encoding="utf-8").splitlines()

        assert content[0] == "─" * 60
        assert "test.jpg" in content[1]
        assert any("File Size" in line for line in content)
        assert any("Sony" in line for line in content)

    @patch("batch_img.info.Info.read_1_image_exif")
    def test_read_exif_quiet_mode_write_error(self, mock_read, tmp_path, monkeypatch):
        """Test error handling when the output file cannot be written."""
        # Create an actual physical file
        file = tmp_path / "test.jpg"
        file.touch()

        mock_read.return_value = (True, (file, {"file_info": {}, EXIF: {}}))

        # Point to a directory that doesn't exist to force an OSError
        output_file = tmp_path / "does_not_exist" / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        result = Info.read_exif(file, quiet=True)
        assert result is False


@pytest.fixture(
    params=[
        (
            Path(f"{_dir}/data/JPG/IMG_4412.jpeg"),
            {
                "exif": {
                    "ColorSpace": 1,
                    "ComponentsConfiguration": "\x01\x02\x03\x00",
                    "ExifTag": 102,
                    "ExifVersion": "0221",
                    "FlashpixVersion": "0100",
                    "Orientation": 1,
                    "SceneCaptureType": 0,
                    "YCbCrPositioning": 1,
                },
                "file_info": {
                    "file_size": "33 KB (34272 bytes)",
                    "last_modified": "2026-08-31 11:25",
                    "format": "JPEG",
                    "dimensions": "320 x 240 (0.1 MP)",
                    "bit_depth": UNKNOWN,
                    "alpha_channel": "No",
                    "colorspace": "RGB",
                    "chroma_format": UNKNOWN,
                },
            },
            Path(f"{_dir}/data/JPG/meta_no_gps.txt"),
        )
    ]
)
def data_out_meta_info(request):
    return request.param


def test_out_meta_info(data_out_meta_info, tmp_path, monkeypatch):
    img_file, data, truth_file = data_out_meta_info

    output_file = tmp_path / INFO_TXT_FILE
    monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

    with open(output_file, "w", encoding="utf-8") as output:
        Info.out_meta_info(img_file, data, 1, 1, output)

    assert output_file.exists()
    # Read with .splitlines() to avoid Windows \r\n vs Linux \n assertion failures
    content = output_file.read_text(encoding="utf-8").splitlines()
    expected = truth_file.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(content):
        if idx == 1:
            continue
        assert content[idx] == expected[idx]
