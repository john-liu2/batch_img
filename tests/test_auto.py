"""Test auto.py
pytest -sv tests/test_auto.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest
from batch_img.auto import Auto


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_2530.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/IMG_2530_1280_bw5.HEIC")),
        ),
    ]
)
def data_resize_add_border(request):
    return request.param


def test_resize_add_border(data_resize_add_border):
    in_path, out_path, expected = data_resize_add_border
    actual = Auto.resize_add_border(in_path, out_path)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_resize_add_border(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Auto.resize_add_border(Path("img/file"), Path("out/path"))
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        # (
        #     Path(f"{dirname(__file__)}/data/HEIC/chef_180cw.heic"),
        #     Path(f"{dirname(__file__)}/.out/"),
        #     (True, Path(f"{dirname(__file__)}/.out/chef_180cw_180cw.heic")),
        # ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/chef_show2.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            (False, Path(f"{dirname(__file__)}/data/HEIC/chef_show2.heic")),
        ),
    ]
)
def data_rotate_if_needed(request):
    return request.param


def test_rotate_if_needed(data_rotate_if_needed):
    in_path, out_path, expected = data_rotate_if_needed
    actual = Auto.rotate_if_needed(in_path, out_path)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/chef_orientation_3.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            (
                True,
                Path(
                    f"{dirname(__file__)}/.out/chef_orientation_3_180cw_1280_bw5.heic"
                ),
            ),
        ),
    ]
)
def data_do_actions(request):
    return request.param


@pytest.mark.slow(reason="This test modifies test data file.")
def test_do_actions(data_do_actions):
    in_path, out_path, expected = data_do_actions
    actual = Auto.do_actions(in_path, out_path)
    assert actual == expected


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}"),
            Path(f"{dirname(__file__)}/.out/"),
            False,
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            True,
        ),
    ]
)
def data_run_on_all(request):
    return request.param


@pytest.mark.slow(reason="This test modifies test data file.")
def test_run_on_all(data_run_on_all):
    in_path, out_path, expected = data_run_on_all
    actual = Auto.run_on_all(in_path, out_path)
    assert actual == expected
