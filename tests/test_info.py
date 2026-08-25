"""Tests info.py
pytest -sv tests/test_info.py
Copyright © 2026 - Present, John Liu
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from batch_img.common import Common
from batch_img.interface import cli
from batch_img.info import Info


class TestReadOneImageExif:
    """Tests for reading EXIF from a single image."""

    def test_read_1_image_exif(self):
        """Test reading EXIF from a single image file."""
        file = Path("tests/data/JPG/152.JPG")
        ok, result = Info.read_1_image_exif(file)
        assert ok
        path, data = result
        assert path == file
        assert "file_info" in data
        assert "exif" in data

        # Check file info
        assert data["file_info"]["format"] == "JPEG"
        assert "dimensions" in data["file_info"]
        assert "file_size" in data["file_info"]

        # Check EXIF data
        assert data["exif"]["Make"] == "Canon"

    def test_read_1_image_exif_nonexistent(self):
        """Test reading EXIF from a non-existent file."""
        file = Path("tests/data/JPG/nonexistent.JPG")
        ok, result = Info.read_1_image_exif(file)
        assert not ok
        assert isinstance(result, str)
        assert "No such file" in result or "cannot identify" in result

    def test_read_1_image_exif_invalid_file(self):
        """Test reading EXIF from an invalid file."""
        file = Path("tests/data/JPG/152.JPG")
        # Simulate an error during image reading
        with patch("PIL.Image.open") as mock_open:
            mock_open.side_effect = OSError("Invalid image file")
            ok, result = Info.read_1_image_exif(file)
            assert not ok
            assert isinstance(result, str)
            assert "Invalid image file" in result

    def test_read_1_image_exif_file_info(self):
        """Test that file info is properly populated."""
        file = Path("tests/data/JPG/152.JPG")
        ok, result = Info.read_1_image_exif(file)
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

    def test_read_exif_single_file(self):
        """Test reading EXIF from a single image file."""
        input_file = Path("tests/data/JPG/152.JPG")
        assert Info.read_exif(input_file)

    def test_read_exif_directory(self):
        """Test reading EXIF from a directory with images."""
        input_dir = Path("tests/data/JPG")
        assert Info.read_exif(input_dir)

    def test_read_exif_no_files(self, tmp_path):
        """Test reading EXIF from a path with no image files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert not Info.read_exif(empty_dir)

    def test_read_exif_quiet_writes_formatted_text(self, tmp_path, monkeypatch):
        """Test quiet mode writes formatted text to a file."""
        input_file = Path("tests/data/JPG/152.JPG")
        output_file = tmp_path / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        assert Info.read_exif(input_file, quiet=True)
        assert output_file.exists()
        content = output_file.read_text()
        assert "152.JPG" in content
        assert "Canon" in content
        assert "File Size" in content
        assert "EXIF Metadata" in content

    def test_read_exif_quiet_output_format(self, tmp_path, monkeypatch):
        """Test the format of quiet mode output file."""
        input_file = Path("tests/data/JPG/152.JPG")
        output_file = tmp_path / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        assert Info.read_exif(input_file, quiet=True)

        # Read and validate the output format
        content = output_file.read_text().strip().split("\n")
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

    def test_read_exif_quiet_no_write_error(self, tmp_path, monkeypatch):
        """Test error handling when writing quiet mode output fails."""
        input_file = Path("tests/data/JPG/152.JPG")
        output_file = tmp_path / "nonexistent_dir" / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        assert not Info.read_exif(input_file, quiet=True)

    def test_read_exif_multiple_files(self):
        """Test reading EXIF from multiple files."""
        input_dir = Path("tests/data/JPG")
        # Should return True if all files are processed
        assert Info.read_exif(input_dir)

    def test_read_exif_quiet_multiple_files(self, tmp_path, monkeypatch):
        """Test quiet mode with multiple files."""
        input_dir = Path("tests/data/JPG")
        output_file = tmp_path / "img_meta_info.txt"
        monkeypatch.setattr(Info, "exif_output_path", lambda: output_file)

        assert Info.read_exif(input_dir, quiet=True)
        assert output_file.exists()
        content = output_file.read_text()
        assert "JPG" in content
        assert "EXIF Metadata" in content

    def test_read_exif_results_dictionary(self):
        """Test that results are stored in a dictionary with file paths as keys."""
        input_dir = Path("tests/data/JPG")
        files = list(Common.prepare_all_files(input_dir, ""))

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
    def test_info_command(self, mock_info):
        """Test info command with input file."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["info", "-i", "tests/data/JPG/152.JPG"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with(
            {"src_path": "tests/data/JPG/152.JPG", "quiet": False}
        )

    @patch("batch_img.main.Main.info")
    def test_info_command_mocks_main(self, mock_info):
        """Test info command calls Main.info with correct arguments."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["info", "-i", "images"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": "images", "quiet": False})

    @patch("batch_img.main.Main.info")
    def test_info_command_quiet(self, mock_info):
        """Test info command with --quiet flag."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["--quiet", "info", "-i", "images"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": "images", "quiet": True})

    @patch("batch_img.main.Main.info")
    def test_info_command_missing_input(self, mock_info):
        """Test info command with missing input."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["info"])
        assert result.exception
        assert "Missing option '-i' / '--input'" in result.output

    @patch("batch_img.main.Main.info")
    def test_info_command_with_parent_input(self, mock_info):
        """Test info command with parent input."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["-i", "images", "info"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": "images", "quiet": False})

    @patch("batch_img.main.Main.info")
    def test_info_command_with_parent_quiet(self, mock_info):
        """Test info command with parent quiet flag."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["--quiet", "-i", "images", "info"])
        assert not result.exception
        assert result.output == ""
        mock_info.assert_called_once_with({"src_path": "images", "quiet": True})

    @patch("batch_img.main.Main.info")
    def test_info_command_quiet_after_command(self, mock_info):
        """Test that --quiet after info command raises an error."""
        mock_info.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, args=["info", "--quiet", "-i", "images"])
        assert result.exception
        assert result.exit_code == 2

    def test_info_command_help(self):
        """Test info command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, args=["info", "--help"])
        assert not result.exception
        assert "--input" in result.output
        assert "Print EXIF information" in result.output
