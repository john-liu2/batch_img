"""Test main.py
pytest -sv tests/test_main.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from unittest.mock import patch

import pytest

from batch_img.main import Main


@pytest.fixture(
    params=[
        (
            "v_1",
            "v_2",
            {
                "src_path": "src/file",
                "output": f"{dirname(__file__)}/.out/",
            },
            "v_2",
        ),
        (
            "v_1",
            "v_2",
            {
                "src_path": "src/file",
            },
            "v_2",
        ),
    ]
)
def data_auto(request):
    return request.param


@patch("batch_img.common.Common.check_latest_version")
@patch("batch_img.auto.Auto.auto_on_all")
@patch("batch_img.auto.Auto.auto_do_1_image")
def test_auto(
    mock_auto_do_1_image,
    mock_auto_on_all,
    mock_check_latest_version,
    data_auto,
):
    v_1, v_2, options, expected = data_auto
    mock_auto_do_1_image.return_value = v_1
    mock_auto_on_all.return_value = v_2
    mock_check_latest_version.return_value = "ok"
    actual = Main.auto(options)
    assert actual == expected


@pytest.fixture(
    params=[
        ("any", "any", {"src_path": "src/file"}, False),
        ("any", "any", {"src_path": "src/file", "border_width": 0}, False),
        ("v_1", "v_2", {"src_path": "src/file", "border_width": 20}, False),
        (
            "v_1",
            "v_2",
            {"src_path": "src/file", "border_width": 20, "border_color": "red"},
            "v_2",
        ),
        (
            "v_1",
            "v_2",
            {
                "src_path": "src/file",
                "border_width": 20,
                "border_color": "red",
                "output": "out/path",
            },
            "v_2",
        ),
    ]
)
def data_border(request):
    return request.param


@patch("batch_img.common.Common.check_latest_version")
@patch("batch_img.border.Border.border_all_in_dir")
@patch("batch_img.border.Border.border_1_image")
def test_border(
    mock_border_1_image, mock_border_all_in_dir, mock_check_latest_version, data_border
):
    v_1, v_2, options, expected = data_border
    mock_border_1_image.return_value = v_1
    mock_border_all_in_dir.return_value = v_2
    mock_check_latest_version.return_value = "ok"
    actual = Main.border(options)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            {
                "src_path": f"{dirname(__file__)}/data/mixed",
                "output": f"{dirname(__file__)}/.out/",
                "border_width": 10,
                "border_color": "red",
            },
            True,
        )
    ]
)
def data_border_all(request):
    return request.param


def test_border_all_in_dir(data_border_all):
    options, expected = data_border_all
    actual = Main.border(options)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            "v_1",
            "v_2",
            {
                "src_path": "src/file",
                "output": f"{dirname(__file__)}/.out/",
            },
            "v_2",
        ),
        (
            "v_1",
            "v_2",
            {
                "src_path": "src/file",
            },
            "v_2",
        ),
    ]
)
def data_no_gps(request):
    return request.param


@patch("batch_img.common.Common.check_latest_version")
@patch("batch_img.no_gps.NoGps.remove_all_images_gps")
@patch("batch_img.no_gps.NoGps.remove_1_image_gps")
def test_no_gps(
    mock_remove_1_image_gps,
    mock_remove_all_images_gps,
    mock_check_latest_version,
    data_no_gps,
):
    v_1, v_2, options, expected = data_no_gps
    mock_remove_1_image_gps.return_value = v_1
    mock_remove_all_images_gps.return_value = v_2
    mock_check_latest_version.return_value = "ok"
    actual = Main.no_gps(options)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            {
                "src_path": f"{dirname(__file__)}/data/mixed",
            },
            True,
        ),
        (
            {
                "src_path": f"{dirname(__file__)}/data/HEIC",
            },
            True,
        ),
        (
            {
                "src_path": f"{dirname(__file__)}/data/JPG",
            },
            True,
        ),
        (
            {
                "src_path": f"{dirname(__file__)}/data/PNG",
            },
            True,
        ),
    ]
)
def data_no_gps_all(request):
    return request.param


def test_all_in_dir_no_gps(data_no_gps_all):
    options, expected = data_no_gps_all
    actual = Main.no_gps(options)
    assert actual == expected


@pytest.fixture(
    params=[
        ("any", "any", {"src_path": "src/file"}, False),
        ("any", "any", {"src_path": "src/file", "length": 0}, False),
        ("v_1", "v_2", {"src_path": "src/file", "length": 1024}, "v_2"),
        (
            "v_1",
            "v_2",
            {"src_path": "src/file", "length": 1024, "output": "out/path"},
            "v_2",
        ),
    ]
)
def data_resize(request):
    return request.param


@patch("batch_img.common.Common.check_latest_version")
@patch("batch_img.resize.Resize.resize_all_progress_bar")
@patch("batch_img.resize.Resize.resize_an_image")
def test_resize(
    mock_resize_an_image,
    mock_resize_all_progress_bar,
    mock_check_latest_version,
    data_resize,
):
    v_1, v_2, options, expected = data_resize
    mock_resize_an_image.return_value = v_1
    mock_resize_all_progress_bar.return_value = v_2
    mock_check_latest_version.return_value = "ok"
    actual = Main.resize(options)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            {
                "src_path": f"{dirname(__file__)}/data/mixed",
                "output": f"{dirname(__file__)}/.out/",
                "length": 1024,
            },
            True,
        )
    ]
)
def data_resize_all(request):
    return request.param


def test_resize_all_in_dir(data_resize_all):
    options, expected = data_resize_all
    actual = Main.resize(options)
    assert actual == expected


@pytest.fixture(
    params=[
        ("any", "any", {"src_path": "src/file"}, False),
        ("any", "any", {"src_path": "src/file", "angle": 0}, False),
        ("v_1", "v_2", {"src_path": "src/file", "angle": 90}, "v_2"),
        (
            "v_1",
            "v_2",
            {"src_path": "src/file", "angle": 90, "output": "out/path"},
            "v_2",
        ),
    ]
)
def data_rotate(request):
    return request.param


@patch("batch_img.common.Common.check_latest_version")
@patch("batch_img.rotate.Rotate.rotate_all_in_dir")
@patch("batch_img.rotate.Rotate.rotate_1_image")
def test_rotate(
    mock_rotate_1_image,
    mock_rotate_all_in_dir,
    mock_check_latest_version,
    data_rotate,
):
    v_1, v_2, options, expected = data_rotate
    mock_rotate_1_image.return_value = v_1
    mock_rotate_all_in_dir.return_value = v_2
    mock_check_latest_version.return_value = "ok"
    actual = Main.rotate(options)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            {
                "src_path": f"{dirname(__file__)}/data/mixed",
                "output": f"{dirname(__file__)}/.out/",
                "angle": 180,
            },
            True,
        )
    ]
)
def data_rotate_all(request):
    return request.param


def test_rotate_all_in_dir(data_rotate_all):
    options, expected = data_rotate_all
    actual = Main.rotate(options)
    assert actual == expected
