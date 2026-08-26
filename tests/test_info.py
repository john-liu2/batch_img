"""Tests info.py
pytest -sv tests/test_info.py
Copyright © 2026 - Present, John Liu
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from batch_img.common import Common
from batch_img.interface import cli
from batch_img.info import Info


@pytest.fixture
def image_path() -> Path:
    """Return the path to a valid test image (JPEG with EXIF)."""
    return Path("tests/data/JPG/152.JPG")


@pytest.fixture
def image_dir() -> Path:
    """Return the path to a directory containing test images."""
    return Path("tests/data/JPG")


@pytest.fixture
def nonexistent_image_path() -> Path:
    """Return a path to a non-existent image file."""
    return Path("tests/data/JPG/nonexistent.JPG")


@pytest.fixture
def platform_error_messages() -> list[str]:
    """
    Return expected error substrings for a non-existent file.
    This accounts for OS‑specific messages (Windows vs. POSIX).
    """
    if sys.platform.startswith("win"):
        return ["cannot find the file", "No such file"]
    # macOS / Linux
    return ["No such file", "cannot identify"]


@pytest.fixture
def temp_output_file(tmp_path: Path) -> Path:
    """Return a temporary file path for quiet mode output."""
    return tmp_path / "img_meta_info.txt"


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestReadOneImageExif:
    """Tests for reading EXIF from a single image."""

    def test_read_1_image_exif(self, image_path):
        """Test reading EXIF from a single image file."""
        ok, result = Info.read_1_image_exif(image_path)
        assert ok
        path, data = result
        assert path == image_path
        assert "file_info" in data
        assert "exif" in data

        # Check file info
        assert data["file_info"]["format"] == "JPEG"
        assert "dimensions" in data["file_info"]
        assert "file_size" in data["file_info"]

        # Check EXIF data
        assert data["exif"]["Make"] == "Canon"

    def test_read_1_image_exif_nonexistent(
        self, nonexistent_image_path, platform_error_messages
    ):
        """Test reading EXIF from a non-existent file."""
        ok, result = Info.read_1_image_exif(nonexistent_image_path)
        assert not ok
        assert isinstance(result, str)
        assert any(err in result for err in platform_error_messages)

    def test_read_1_image_exif_invalid_file(self, image_path):
        """Test reading EXIF from an invalid file."""
        # Simulate an error during image reading
        with patch("PIL.Image.open") as mock_open:
            mock_open.side_effect = OSError("Invalid image file")
            ok, result = Info.read_1_image_exif(image_path)
            assert not ok
            assert isinstance(result, str)
            assert "Invalid image file" in result

    def test_read_1_image_exif_file_info(self, image_path):
        """Test that file info is properly populated."""
        ok, result = Info.read_1_image_exif(image_path)
        assert ok
        _, data = result

        file_info = data["file_info"]
        assert file_info["file_size"] > 0
        assert "dimensions" in file_info
        assert file_info["alpha_channel"] == "No"
        assert "colorspace" in file_info
        assert "last_modified" in file_info


class TestReadExif:
    """Tests for reading EXIF from files or directories."""

    def test_read_exif_single_file(self, image_path):
        """Test reading EXIF from a single image file."""
        assert Info.read_exif(image_path)

    def test_read_exif_directory(self, image_dir):
        """Test reading EXIF from a directory with images."""
        assert Info.read_exif(image_dir)

    def test_read_exif_no_files(self, tmp_path):
        """Test reading EXIF from a path with no image files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert not Info.read_exif(empty_dir)

    def test_read_exif_quiet_writes_formatted_text(
        self, image_path, temp_output_file, monkeypatch
    ):
        """Test quiet mode writes formatted text to a file."""
        monkeypatch.setattr(Info, "exif_output_path", lambda: temp_output_file)

        assert Info.read_exif(image_path, quiet=True)
        assert temp_output_file.exists()
        content = temp_output_file.read_text(encoding="utf-8")
        assert "152.JPG" in content
        assert "Canon" in content
        assert "File Size" in content
        assert "EXIF Metadata" in content

    def test_read_exif_quiet_output_format(
        self, image_path, temp_output_file, monkeypatch
    ):
        """Test the format of quiet mode output file."""
        monkeypatch.setattr(Info, "exif_output_path", lambda: temp_output_file)
        assert Info.read_exif(image_path, quiet=True)
        # splitlines() for cross platforms
        content = temp_output_file.read_text(encoding="utf-8").strip().splitlines()

        # First line is the separator
        assert content[0] == "─" * 60
        # Second line contains the file path
        assert "152.JPG" in content[1]
        # Check file info fields
        assert "File Size" in content[2]
        assert "Format" in content[4]
        # Blank line before EXIF section
        assert content[10] == ""
        # EXIF Metadata header
        assert "EXIF Metadata" in content[11]
        # Check that Make is present in EXIF section
        assert "Make" in content[12] or "Make" in content[13]

    def test_read_exif_quiet_no_write_error(self, image_path, tmp_path, monkeypatch):
        """Test error handling when writing quiet mode output fails."""
        output_file = tmp_path / "nonexistent_dir" / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        assert not Info.read_exif(image_path, quiet=True)

    def test_read_exif_multiple_files(self, image_dir):
        """Test reading EXIF from multiple files."""
        # Should return True if all files are processed
        assert Info.read_exif(image_dir)

    def test_read_exif_quiet_multiple_files(
        self, image_dir, temp_output_file, monkeypatch
    ):
        """Test quiet mode with multiple files."""
        monkeypatch.setattr(Info, "exif_output_path", lambda: temp_output_file)

        assert Info.read_exif(image_dir, quiet=True)
        assert temp_output_file.exists()
        content = temp_output_file.read_text(encoding="utf-8")
        assert "JPG" in content
        assert "EXIF Metadata" in content

    def test_read_exif_results_dictionary(self, image_dir):
        """Test that results are stored in a dictionary with file paths as keys."""
        files = list(Common.prepare_all_files(image_dir, ""))

        # Read all files and verify results structure
        results = {}
        for file in files:
            ok, result = Info.read_1_image_exif(file)
            if ok:
                # result is (Path, dict) tuple
                if isinstance(result, tuple) and len(result) == 2:
                    results[file] = result[1]

        assert len(results) > 0
        assert all(isinstance(path, Path) for path in results.keys())
        assert all("file_info" in data for data in results.values())


class TestFormatFileSize:
    """Tests for file size formatting."""

    def test_format_small_size(self):
        """Test formatting small file size."""
        result = Info._easy_file_sz(500)
        assert "500 B" in result
        assert "(500 bytes)" in result

    def test_format_kb_size(self):
        """Test formatting KB size."""
        result = Info._easy_file_sz(1024 * 5)
        assert "KB" in result
        assert "(5120 bytes)" in result

    def test_format_mb_size(self):
        """Test formatting MB size."""
        result = Info._easy_file_sz(1024 * 1024 * 2)
        assert "MB" in result
        assert "(2097152 bytes)" in result


class TestInfoCommand:
    """Tests for the info sub-command in the CLI."""

    @patch("batch_img.main.Main.info")
    def test_info_command(self, mock_info, image_path):
        """Test info command with input file."""
        mock_info.return_value = True
        runner = CliRunner()
        img_path = str(image_path)
        result = runner.invoke(cli, args=["info", "-i", img_path])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": img_path, "quiet": False})

    @patch("batch_img.main.Main.info")
    def test_info_command_mocks_main(self, mock_info, image_dir):
        """Test info command calls Main.info with correct arguments."""
        mock_info.return_value = True
        runner = CliRunner()
        img_dir = str(image_dir)
        result = runner.invoke(cli, args=["info", "-i", img_dir])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": img_dir, "quiet": False})

    @patch("batch_img.main.Main.info")
    def test_info_command_quiet(self, mock_info, image_dir):
        """Test info command with --quiet flag."""
        mock_info.return_value = True
        runner = CliRunner()
        img_dir = str(image_dir)
        result = runner.invoke(cli, args=["--quiet", "info", "-i", img_dir])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": img_dir, "quiet": True})

    @patch("batch_img.main.Main.info")
    def test_info_command_missing_input(self, mock_info):
        """Test info command with missing input."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["info"])
        assert result.exception
        assert "Missing option '-i' / '--input'" in result.output

    @patch("batch_img.main.Main.info")
    def test_info_command_with_parent_input(self, mock_info, image_dir):
        """Test info command with parent input."""
        mock_info.return_value = True
        runner = CliRunner()
        img_dir = str(image_dir)
        result = runner.invoke(cli, args=["-i", img_dir, "info"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": img_dir, "quiet": False})

    @patch("batch_img.main.Main.info")
    def test_info_command_with_parent_quiet(self, mock_info, image_dir):
        """Test info command with parent quiet flag."""
        mock_info.return_value = True
        runner = CliRunner()
        img_dir = str(image_dir)
        result = runner.invoke(cli, args=["--quiet", "-i", img_dir, "info"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": img_dir, "quiet": True})

    @patch("batch_img.main.Main.info")
    def test_info_command_quiet_after_command(self, mock_info, image_dir):
        """Test that --quiet after info command raises an error."""
        mock_info.return_value = True
        runner = CliRunner()
        img_dir = str(image_dir)
        result = runner.invoke(cli, args=["info", "--quiet", "-i", img_dir])
        assert result.exception
        assert result.exit_code == 2

    def test_info_command_help(self):
        """Test info command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, args=["info", "--help"])
        assert not result.exception
        assert "--input" in result.output
        assert "Print EXIF information" in result.output
