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
    do_effect,
    remove_bg,
    remove_gps,
    resize,
    rotate,
    transparent,
)


@pytest.fixture(
    params=[
        ("src_path -o out/dir", True, MSG_OK),
        ("img/file --output out/file -ar", False, MSG_BAD),
        ("src_path --auto_rotate", True, MSG_OK),
    ]
)
def data_auto(request):
    return request.param


@patch("batch_img.main.Main.auto")
def test_auto(mock_auto, data_auto):
    _input, res, expected = data_auto
    mock_auto.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(auto, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(
    params=[
        ("src_path -bw 3 --border_color #AABBCC", True, MSG_OK),
        ("img/file --border_width 9 -bc blue -o out/file", False, MSG_BAD),
        ("src_path -o out/dir", True, MSG_OK),
    ]
)
def data_border(request):
    return request.param


@patch("batch_img.main.Main.border")
def test_border(mock_border, data_border):
    _input, res, expected = data_border
    mock_border.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(border, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(params=["img/file -bw -9", "img/file --border_width 31"])
def data_error_border(request):
    return request.param


@patch("batch_img.main.Main.border")
def test_error_border(mock_border, data_error_border):
    _input = data_error_border
    mock_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(border, args=_input.split())
    print(result.output)
    assert result.exception


@pytest.fixture(
    params=[
        ("src_path -e blur", True, MSG_OK),
        ("img/file --effect hdr", False, MSG_BAD),
        ("src_path -e neon", True, MSG_OK),
    ]
)
def data_effect(request):
    return request.param


@patch("batch_img.main.Main.do_effect")
def test_do_effect(mock_border, data_effect):
    _input, res, expected = data_effect
    mock_border.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(do_effect, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(
    params=[
        ("src_path -o out/dir", True, MSG_OK),
        ("img/file --output out/file", False, MSG_BAD),
        ("src_path", True, MSG_OK),
    ]
)
def data_remove_bg(request):
    return request.param


@patch("batch_img.main.Main.remove_bg")
def test_remove_bg(mock_remove_bg, data_remove_bg):
    _input, res, expected = data_remove_bg
    mock_remove_bg.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(remove_bg, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(
    params=[
        ("src_path -o out/dir", True, MSG_OK),
        ("img/file --output out/file", False, MSG_BAD),
        ("src_path", True, MSG_OK),
    ]
)
def data_no_gps(request):
    return request.param


@patch("batch_img.main.Main.remove_gps")
def test_remove_gps(mock_remove_gps, data_no_gps):
    _input, res, expected = data_no_gps
    mock_remove_gps.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(remove_gps, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(
    params=[
        ("src_path -l 1234 -o out/dir", True, MSG_OK),
        ("img/file --length 9876 --output out/file", False, MSG_BAD),
        ("src_path -l 1234", True, MSG_OK),
    ]
)
def data_resize(request):
    return request.param


@patch("batch_img.main.Main.resize")
def test_resize(mock_resize, data_resize):
    _input, res, expected = data_resize
    mock_resize.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(resize, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@patch("batch_img.main.Main.resize")
def test_error_resize(mock_resize):
    _input = "img/file --length -9"
    mock_resize.return_value = True
    runner = CliRunner()
    result = runner.invoke(resize, args=_input.split())
    print(result.output)
    assert result.exception


@pytest.fixture(
    params=[
        ("src_path -a 90 -o out/dir", True, MSG_OK),
        ("img/file --angle 270 --output out/file", False, MSG_BAD),
        ("src_path -a 90", True, MSG_OK),
    ]
)
def data_rotate(request):
    return request.param


@patch("batch_img.main.Main.rotate")
def test_rotate(mock_rotate, data_rotate):
    _input, res, expected = data_rotate
    mock_rotate.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(rotate, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@patch("batch_img.main.Main.rotate")
def test_error_rotate(mock_rotate):
    _input = "img/file --angle -90"
    mock_rotate.return_value = True
    runner = CliRunner()
    result = runner.invoke(rotate, args=_input.split())
    print(result.output)
    assert result.exception


@pytest.fixture(
    params=[
        ("src_path -t 123 -o out/dir -w", True, MSG_OK),
        ("img/file --transparency 255 --output out/file", False, MSG_BAD),
        ("src_path -t 0 --white", True, MSG_OK),
    ]
)
def data_transparent(request):
    return request.param


@patch("batch_img.main.Main.transparent")
def test_transparent(mock_rotate, data_transparent):
    _input, res, expected = data_transparent
    mock_rotate.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(transparent, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@patch("batch_img.main.Main.transparent")
def test_error_transparent(mock_transparent):
    _input = "img/file --transparency -1"
    mock_transparent.return_value = True
    runner = CliRunner()
    result = runner.invoke(transparent, args=_input.split())
    print(result.output)
    assert result.exception
