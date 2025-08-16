"""Test common.py
pytest -sv tests/test_common.py
"""

from unittest.mock import MagicMock, patch

import pytest

from batch_img.common import Common
from batch_img.const import NAME, PKG_NAME, VER
from .helper import DotDict


@pytest.fixture(params=[({NAME: PKG_NAME, VER: "0.1.2"}, "0.0.7"), ({}, "0.0.7")])
def ver_data(request):
    return request.param


def test_get_version(ver_data):
    fake_v, expected = ver_data
    mock = MagicMock()
    mock.version = expected
    actual = Common.get_version()
    assert actual == expected


@pytest.fixture(
    params=[
        ({}, "cmd1 -op1 | grep k1", (0, "", "")),
        (
            DotDict({"returncode": 0, "stdout": "\n My Std Output\n", "stderr": ""}),
            "cmd2 -op2 | grep k2",
            (0, "\n My Std Output\n", ""),
        ),
        (
            DotDict({"returncode": 2, "stdout": "\n My Output\n", "stderr": "SomeErr"}),
            "cmd3 -op3 | grep k3",
            (2, "\n My Output\n", "SomeErr"),
        ),
        (
            DotDict({"returncode": 0, "stdout": "\n \t \n", "stderr": ""}),
            "cmd3 -op3 | grep k3",
            (0, "\n \t \n", ""),
        ),
    ]
)
def run_cmd_data(request):
    return request.param


@patch("subprocess.run")
def test_run_cmd(mock_s_run, run_cmd_data):
    v_1, cmd, expected = run_cmd_data
    if v_1:
        mock_s_run.return_value = v_1
        actual = Common.run_cmd(cmd)
        assert actual == expected
    else:
        mock_s_run.side_effect = KeyError("KE")
        with pytest.raises(KeyError):
            Common.run_cmd(cmd)
