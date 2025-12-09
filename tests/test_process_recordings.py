from pathlib import Path

import pytest
from bistmon.cli import load

from tests.conftest import path_recordings


@pytest.mark.skip(reason="won't work without interactive input")
@pytest.mark.parametrize("file", path_recordings)
def test_process_recording(file: Path):
    load(file)
