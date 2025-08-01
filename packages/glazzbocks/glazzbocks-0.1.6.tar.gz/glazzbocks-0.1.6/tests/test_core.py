import pytest
from glazzbocks import DataExplorer

def test_dataexplorer_init():
    de = DataExplorer()
    assert de is not None