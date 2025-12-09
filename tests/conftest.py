import os
from pathlib import Path

import pytest

path_here = Path(__file__).resolve().parent
path_recordings = path_here.glob("raw_*.xml")


@pytest.fixture
def example_path() -> Path:
    path = path_here.parent / "examples"
    os.chdir(path)
    return path
