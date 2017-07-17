"""
Test core class
"""

from diffport.core import Diffport
from pathlib import Path


def test_list(tmpdir):
    """
    Test that listing is alright
    """

    diffp = Diffport({}, "sqlite:///:memory:", Path(tmpdir).joinpath("store"))
    assert diffp.list_snapshots(json_output=True) == []
