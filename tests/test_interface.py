"""Test interface.py
pytest -sv tests/test_interface.py
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from batch_img.const import MSG_OK, MSG_BAD
from batch_img.interface import action


@pytest.fixture(
    params=[
        ("src_path --add_border 3 'blue'", True, MSG_OK),
        ("img/file --add_border 6 'red'", False, MSG_BAD),
        ("src_path --resize 0", True, MSG_OK),
        ("src_path --resize 1024", False, MSG_BAD),
        ("img/file --rotate 90", True, MSG_OK),
        ("src_path --rotate 180", False, MSG_BAD),
    ]
)
def action_data(request):
    return request.param


@patch("batch_img.main.Main.run")
def test_action(mock_run, action_data):
    _input, ret, expected = action_data
    mock_run.return_value = ret
    expected += "\n"
    runner = CliRunner()
    result = runner.invoke(action, args=_input.split())
    print(result.output)
    assert not result.exception
    assert result.output == expected
