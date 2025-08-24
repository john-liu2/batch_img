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
            (True, Path(f"{dirname(__file__)}/.out/IMG_2530_bw5.HEIC")),
        ),
    ]
)
def data_process_an_image(request):
    return request.param


def test_process_an_image(data_process_an_image):
    in_path, out_path, expected = data_process_an_image
    actual = Auto.process_an_image(in_path, out_path)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_process_an_image(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Auto.process_an_image(Path("img/file"), Path("out/path"))
    assert "img/file" in actual[1]


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}/data/HEIC/chef_180cw.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/chef_180cw_180cw.heic")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/chef2_90cw.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/chef2_90cw_270cw.heic")),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0131.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            (True, Path(f"{dirname(__file__)}/.out/IMG_0131_270cw.HEIC")),
        ),
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
            Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"),
            Path(f"{dirname(__file__)}/.out/"),
            False,
            (
                True,
                Path(f"{dirname(__file__)}/.out/Cartoon_bw5.heic"),
            ),
        ),
        (
            Path(f"{dirname(__file__)}/data/HEIC/IMG_0131.HEIC"),
            Path(f"{dirname(__file__)}/.out/"),
            True,
            (
                True,
                Path(f"{dirname(__file__)}/.out/IMG_0131_bw5_270cw.HEIC"),
            ),
        ),
    ]
)
def data_auto_1_image(request):
    return request.param


def test_auto_do_1_image(data_auto_1_image):
    in_path, out_path, auto_rotate, expected = data_auto_1_image
    actual = Auto.auto_do_1_image((in_path, out_path, auto_rotate))
    assert actual == expected


@pytest.fixture(
    params=[
        (
            Path(f"{dirname(__file__)}"),
            Path(f"{dirname(__file__)}/.out/"),
            True,
            False,
        ),
        (
            Path(f"{dirname(__file__)}/data/PNG"),
            Path(f"{dirname(__file__)}/.out/"),
            False,
            True,
        ),
    ]
)
def data_run_on_all(request):
    return request.param


def test_auto_on_all(data_run_on_all):
    in_path, out_path, auto_rotate, expected = data_run_on_all
    actual = Auto.auto_on_all(in_path, out_path, auto_rotate)
    assert actual == expected
