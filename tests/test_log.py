"""Test log.py
pytest -sv tests/test_log.py
Copyright © 2025 John Liu
"""

from os.path import dirname
from unittest.mock import patch

import pytest

from batch_img.log import Log


@pytest.fixture(
    params=[
        (
            f"{dirname(__file__)}/../batch_img/config.json",
            {"mode": "dev", "level": "DEBUG", "to_file": True},
        ),
        (
            f"{dirname(__file__)}/../batch_img/config_prod.json",
            {"mode": "prod", "level": "INFO", "to_file": False},
        ),
    ]
)
def data_load_config(request):
    return request.param


def test_load_config(data_load_config):
    file, expected = data_load_config
    actual = Log.load_config(file)
    assert actual == expected


@patch("builtins.open")
def test_error_log_config(mock_open):
    mock_open.side_effect = FileNotFoundError("NotFound")
    actual = Log.load_config("config/file")
    assert actual == {}


def test_get_settings():
    Log._get_settings()
