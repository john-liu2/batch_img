"""Test interface.py
pytest -sv tests/test_interface.py
Copyright © 2025 John Liu
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from batch_img.const import MSG_OK, MSG_BAD
from batch_img.interface import border, defaults, resize, rotate


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
def test_border(mock_add_border, data_border):
    _input, res, expected = data_border
    mock_add_border.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(border, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected


@pytest.fixture(params=["img/file -bw -9", "img/file --border_width 21"])
def data_error_border(request):
    return request.param


@patch("batch_img.main.Main.border")
def test_error_border(mock_add_border, data_error_border):
    _input = data_error_border
    mock_add_border.return_value = True
    runner = CliRunner()
    result = runner.invoke(border, args=_input.split())
    print(result.output)
    assert result.exception


@pytest.fixture(
    params=[
        ("src_path --output out/dir", True, MSG_OK),
        ("img/file", False, MSG_BAD),
        ("src_path -o out/dir", True, MSG_OK),
    ]
)
def data_defaults(request):
    return request.param


@patch("batch_img.main.Main.default_run")
def test_defaults(mock_run, data_defaults):
    _input, res, expected = data_defaults
    mock_run.return_value = res
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(defaults, args=_input.split())
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
