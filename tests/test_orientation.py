"""Test orientation.py
pytest -sv tests/test_orientation.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from pathlib import Path
from unittest.mock import patch

import pytest

from batch_img.orientation import Orientation, EXIF_CW_ANGLE


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/PNG/Checkmark.PNG"), EXIF_CW_ANGLE[1]),
        (Path(f"{dirname(__file__)}/data/JPG/P1040566.jpeg"), -1),
        (Path(f"{dirname(__file__)}/data/PNG/LagrangePoints.png"), -1),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"), EXIF_CW_ANGLE[1]),
        # JL 2025-08-18: the below two cases got 'Orientation': 1
        # (
        #     Path(f"{dirname(__file__)}/data/HEIC/chef_orientation_3.heic"),
        #     EXIF_CW_ANGLE[3],
        # ),
        # (
        #     Path(f"{dirname(__file__)}/data/HEIC/chef_orientation_8.heic"),
        #     EXIF_CW_ANGLE[8],
        # ),
    ]
)
def data_exif_orientation(request):
    return request.param


def test_exif_orientation_2_cw_angle(data_exif_orientation):
    file, expected = data_exif_orientation
    actual = Orientation.exif_orientation_2_cw_angle(file)
    assert actual == expected


@patch("PIL.Image.open")
def test_error_exif_orientation_2_cw_angle(mock_open):
    mock_open.side_effect = ValueError("VE")
    actual = Orientation.exif_orientation_2_cw_angle(Path("img/file"))
    assert actual == -1


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon.heic"), 0),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_180cw.heic"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_270cw.heic"), 90),
        (Path(f"{dirname(__file__)}/data/HEIC/Cartoon_90cw.heic"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_0070.HEIC"), -1),
        (Path(f"{dirname(__file__)}/data/PNG/LagrangePoints.png"), -1),
        (Path(f"{dirname(__file__)}/data/JPG/152.JPG"), -1),
        (Path(f"{dirname(__file__)}/data/HEIC/chef2_90cw.heic"), 270),
    ]
)
def data_detect_by_face(request):
    return request.param


def test_get_cw_angle_by_face(data_detect_by_face):
    file, expected = data_detect_by_face
    actual = Orientation().get_cw_angle_by_face(file)
    assert actual == expected


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/HEIC/chef_180cw.heic"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/chef_90cw.heic"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/chef_270cw.heic"), 90),
        (Path(f"{dirname(__file__)}/data/HEIC/chef2_180cw.heic"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/chef2_90cw.heic"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/chef2_270cw.heic"), 90),
        # JL 2025-08-20: check sky/clouds orientation by floor
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2529_180cw.HEIC"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2529_90cw.HEIC"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2529_270cw.HEIC"), 90),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_180cw.HEIC"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_90cw.HEIC"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_270cw.HEIC"), 90),
    ]
)
def data_get_orientation_by_floor(request):
    return request.param


def test_get_orientation_by_floor(data_get_orientation_by_floor):
    file, expected = data_get_orientation_by_floor
    actual = Orientation.get_orientation_by_floor(file)
    assert actual == expected


@pytest.fixture(
    params=[
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2527_180cw.HEIC"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2527_90cw.HEIC"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2527_270cw.HEIC"), 90),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_180cw.HEIC"), 180),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_90cw.HEIC"), 270),
        (Path(f"{dirname(__file__)}/data/HEIC/IMG_2530_270cw.HEIC"), 90),
    ]
)
def data_get_cw_angle_by_sky(request):
    return request.param


def test_get_cw_angle_by_sky(data_get_cw_angle_by_sky):
    file, expected = data_get_cw_angle_by_sky
    actual = Orientation().get_cw_angle_by_sky(file)
    assert actual == expected
