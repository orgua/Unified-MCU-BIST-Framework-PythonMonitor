from pathlib import Path

import pytest
from bistmon.cli import cli
from click.testing import CliRunner

from tests.conftest import path_recordings


def test_cli_invoke_help_short() -> None:
    res = CliRunner().invoke(cli, ["-h"])
    assert res.exit_code == 0


def test_cli_invoke_help_long() -> None:
    res = CliRunner().invoke(cli, ["--help"])
    assert res.exit_code == 0


def test_cli_get_version() -> None:
    res = CliRunner().invoke(cli, ["--verbose", "version"])
    assert res.exit_code == 0


@pytest.mark.skip(reason="won't work without interactive input")
@pytest.mark.parametrize("file", path_recordings)
def test_cli_load_recording(file: Path) -> None:
    res = CliRunner().invoke(cli, ["--verbose", "load", file.as_posix()])
    assert res.exit_code == 0
