"""Test interface.py
pytest -sv tests/test_interface.py
Copyright © 2025 John Liu
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from batch_img.const import MSG_BAD, MSG_OK
from batch_img.interface import (
    auto,
    border,
    cli,
    do_effect,
    info,
    remove_bg,
    remove_gps,
    resize,
    rotate,
    transparent,
)


@patch("batch_img.main.Main.info")
def test_info(mock_info):
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["info", "-i", "images"])
    assert not result.exception
    assert not result.output
    mock_info.assert_called_once_with({"src_path": "images", "quiet": False})


@patch("batch_img.main.Main.info")
def test_info_quiet(mock_info):
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "info", "-i", "images"])
    assert not result.exception
    assert not result.output
    mock_info.assert_called_once_with({"src_path": "images", "quiet": True})


@patch("batch_img.main.Main.info")
def test_info_quiet_after_command(mock_info):
    """Test that --quiet after sub-command raises an error (global option)."""
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["info", "--quiet", "-i", "images"])
    assert result.exception
    assert result.exit_code == 2


@patch("batch_img.main.Main.info")
def test_info_missing_input(mock_info):
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["info"])
    assert result.exception
    assert "Missing option '-i' / '--input'" in result.output


@patch("batch_img.main.Main.info")
def test_info_with_parent_input(mock_info):
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["-i", "images", "info"])
    assert not result.exception
    assert not result.output
    mock_info.assert_called_once_with({"src_path": "images", "quiet": False})


@patch("batch_img.main.Main.info")
def test_info_with_parent_quiet(mock_info):
    mock_info.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "-i", "images", "info"])
    assert not result.exception
    assert not result.output
    mock_info.assert_called_once_with({"src_path": "images", "quiet": True})


@patch("batch_img.main.Main.auto")
def test_auto_input_option(mock_auto):
    mock_auto.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_auto.assert_called_once_with(
        {"src_path": "images", "output": "", "auto_rotate": False}
    )


@patch("batch_img.main.Main.auto")
def test_auto_with_output(mock_auto):
    mock_auto.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto", "-i", "images", "-o", "output/dir"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_auto.assert_called_once_with(
        {"src_path": "images", "output": "output/dir", "auto_rotate": False}
    )


@patch("batch_img.main.Main.auto")
def test_auto_global_quiet(mock_auto):
    mock_auto.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "auto", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_auto.assert_called_once_with(
        {"src_path": "images", "output": "", "auto_rotate": False, "quiet": True}
    )


@patch("batch_img.main.Main.auto")
def test_auto_quiet_after_command(mock_auto):
    """Test that --quiet after sub-command raises an error (global option)."""
    mock_auto.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto", "--quiet", "-i", "images"])
    assert result.exception
    assert result.exit_code == 2


@patch("batch_img.main.Main.auto")
def test_auto_missing_input(mock_auto):
    mock_auto.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto"])
    assert result.exception
    assert "Missing option '-i' / '--input'" in result.output


@patch("batch_img.main.Main.border")
def test_border_default_options(mock_border):
    mock_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["border", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_border.assert_called_once_with(
        {
            "src_path": "images",
            "output": "",
            "border_width": 5,
            "border_color": "gray",
        }
    )


@patch("batch_img.main.Main.border")
def test_border_with_options(mock_border):
    mock_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=["border", "-i", "images", "-bw", "10", "-bc", "#AABBCC", "-o", "output/file"],
    )
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_border.assert_called_once_with(
        {
            "src_path": "images",
            "output": "output/file",
            "border_width": 10,
            "border_color": "#AABBCC",
        }
    )


@patch("batch_img.main.Main.border")
def test_border_global_quiet(mock_border):
    mock_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "border", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_border.assert_called_once_with(
        {
            "src_path": "images",
            "output": "",
            "border_width": 5,
            "border_color": "gray",
            "quiet": True,
        }
    )


@patch("batch_img.main.Main.border")
def test_error_border(mock_border):
    mock_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["border", "-i", "images", "-bw", "-9"])
    assert result.exception


@patch("batch_img.main.Main.do_effect")
def test_do_effect_default(mock_do_effect):
    mock_do_effect.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["do-effect", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_do_effect.assert_called_once_with(
        {"src_path": "images", "output": "", "effect": "neon"}
    )


@patch("batch_img.main.Main.do_effect")
def test_do_effect_with_options(mock_do_effect):
    mock_do_effect.return_value = True
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=["do-effect", "-i", "images", "-e", "blur", "-o", "output/dir"],
    )
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_do_effect.assert_called_once_with(
        {"src_path": "images", "output": "output/dir", "effect": "blur"}
    )


@patch("batch_img.main.Main.do_effect")
def test_do_effect_global_quiet(mock_do_effect):
    mock_do_effect.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "do-effect", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_do_effect.assert_called_once_with(
        {"src_path": "images", "output": "", "effect": "neon", "quiet": True}
    )


@patch("batch_img.main.Main.do_effect")
def test_do_effect_missing_effect(mock_do_effect):
    mock_do_effect.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["do-effect", "-i", "images", "-e", "invalid"])
    assert result.exception


@patch("batch_img.main.Main.remove_bg")
def test_remove_bg(mock_remove_bg):
    mock_remove_bg.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["remove-bg", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_bg.assert_called_once_with(
        {"src_path": "images", "output": ""}
    )


@patch("batch_img.main.Main.remove_bg")
def test_remove_bg_with_output(mock_remove_bg):
    mock_remove_bg.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["remove-bg", "-i", "images", "-o", "output/dir"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_bg.assert_called_once_with(
        {"src_path": "images", "output": "output/dir"}
    )


@patch("batch_img.main.Main.remove_bg")
def test_remove_bg_global_quiet(mock_remove_bg):
    mock_remove_bg.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "remove-bg", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_bg.assert_called_once_with(
        {"src_path": "images", "output": "", "quiet": True}
    )


@patch("batch_img.main.Main.remove_gps")
def test_remove_gps(mock_remove_gps):
    mock_remove_gps.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["remove-gps", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_gps.assert_called_once_with(
        {"src_path": "images", "output": ""}
    )


@patch("batch_img.main.Main.remove_gps")
def test_remove_gps_with_output(mock_remove_gps):
    mock_remove_gps.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["remove-gps", "-i", "images", "-o", "output/file"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_gps.assert_called_once_with(
        {"src_path": "images", "output": "output/file"}
    )


@patch("batch_img.main.Main.remove_gps")
def test_remove_gps_global_quiet(mock_remove_gps):
    mock_remove_gps.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "remove-gps", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_remove_gps.assert_called_once_with(
        {"src_path": "images", "output": "", "quiet": True}
    )


@patch("batch_img.main.Main.resize")
def test_resize_default(mock_resize):
    mock_resize.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["resize", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_resize.assert_called_once_with(
        {"src_path": "images", "output": "", "length": 0}
    )


@patch("batch_img.main.Main.resize")
def test_resize_with_options(mock_resize):
    mock_resize.return_value = True
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=["resize", "-i", "images", "-l", "1920", "-o", "output/dir"],
    )
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_resize.assert_called_once_with(
        {"src_path": "images", "output": "output/dir", "length": 1920}
    )


@patch("batch_img.main.Main.resize")
def test_resize_global_quiet(mock_resize):
    mock_resize.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "resize", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_resize.assert_called_once_with(
        {"src_path": "images", "output": "", "length": 0, "quiet": True}
    )


@patch("batch_img.main.Main.resize")
def test_error_resize(mock_resize):
    mock_resize.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["resize", "-i", "images", "-l", "-9"])
    assert result.exception


@patch("batch_img.main.Main.rotate")
def test_rotate_default(mock_rotate):
    mock_rotate.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["rotate", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_rotate.assert_called_once_with(
        {"src_path": "images", "output": "", "angle": 0}
    )


@patch("batch_img.main.Main.rotate")
def test_rotate_with_options(mock_rotate):
    mock_rotate.return_value = True
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=["rotate", "-i", "images", "-a", "90", "-o", "output/dir"],
    )
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_rotate.assert_called_once_with(
        {"src_path": "images", "output": "output/dir", "angle": 90}
    )


@patch("batch_img.main.Main.rotate")
def test_rotate_global_quiet(mock_rotate):
    mock_rotate.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "rotate", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_rotate.assert_called_once_with(
        {"src_path": "images", "output": "", "angle": 0, "quiet": True}
    )


@patch("batch_img.main.Main.rotate")
def test_error_rotate(mock_rotate):
    mock_rotate.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["rotate", "-i", "images", "-a", "-90"])
    assert result.exception


@patch("batch_img.main.Main.transparent")
def test_transparent_default(mock_transparent):
    mock_transparent.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["transparent", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_transparent.assert_called_once_with(
        {
            "src_path": "images",
            "output": "",
            "transparency": 127,
            "white": False,
        }
    )


@patch("batch_img.main.Main.transparent")
def test_transparent_with_options(mock_transparent):
    mock_transparent.return_value = True
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=["transparent", "-i", "images", "-t", "200", "-w", "-o", "output/file"],
    )
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_transparent.assert_called_once_with(
        {
            "src_path": "images",
            "output": "output/file",
            "transparency": 200,
            "white": True,
        }
    )


@patch("batch_img.main.Main.transparent")
def test_transparent_global_quiet(mock_transparent):
    mock_transparent.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["--quiet", "transparent", "-i", "images"])
    assert not result.exception
    assert result.output == f"{MSG_OK}\n"
    mock_transparent.assert_called_once_with(
        {
            "src_path": "images",
            "output": "",
            "transparency": 127,
            "white": False,
            "quiet": True,
        }
    )


@patch("batch_img.main.Main.transparent")
def test_error_transparent(mock_transparent):
    mock_transparent.return_value = True
    runner = CliRunner()
    result = runner.invoke(cli, args=["transparent", "-i", "images", "-t", "-1"])
    assert result.exception


def test_missing_input():
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto"])
    assert result.exception
    assert "Missing option '-i' / '--input'" in result.output


def test_help_output():
    runner = CliRunner()
    result = runner.invoke(cli, args=["--help"])
    assert not result.exception
    assert "info" in result.output
    assert "auto" in result.output
    assert "border" in result.output
    assert "resize" in result.output
    assert "rotate" in result.output
    assert "do-effect" in result.output
    assert "remove-bg" in result.output
    assert "remove-gps" in result.output
    assert "--quiet" in result.output


def test_command_help_output():
    runner = CliRunner()
    result = runner.invoke(cli, args=["auto", "--help"])
    assert not result.exception
    assert "--input" in result.output
    assert "--output" in result.output
    assert "--auto_rotate" in result.output


def test_info_help_output():
    runner = CliRunner()
    result = runner.invoke(cli, args=["info", "--help"])
    assert not result.exception
    assert "--input" in result.output
    assert "Print EXIF information" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, args=["--version"])
    assert not result.exception


def test_update():
    runner = CliRunner()
    result = runner.invoke(cli, args=["--update"])
    assert not result.exception


def test_no_command():
    runner = CliRunner()
    result = runner.invoke(cli, args=[])
    assert not result.exception
    assert "Usage" in result.output
