# tests/test_version.py

from src import agix


def test_package_version_matches():
    assert agix.__version__ == "1.1.0"
