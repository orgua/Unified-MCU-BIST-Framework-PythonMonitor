from pathlib import Path

from bistmon.cli import process_file

path_here = Path(__file__).parent
path_test = path_here.parent / "tests"
paths_raw = path_here.glob("raw_*.xml")

for path in paths_raw:
    process_file(path)
