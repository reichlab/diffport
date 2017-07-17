"""
Test core class
"""

from diffport.core import Diffport
from diffport.watchers import WatcherNumberOfRows
from pathlib import Path
from random import random


# Test config for checking snapshots
TEST_TABLE = "test-table"
CONFIG = [{
    "name": "number-of-rows",
    "config": {
        "groupby": [],
        "table": TEST_TABLE
    }
}]


def db_seed(db):
    """
    Add dummy item to db for testing
    """

    table = db[TEST_TABLE]
    table.insert({
        "rand": random()
    })

def test_list(tmpdir):
    """
    Test that listing is alright
    """

    diffp = Diffport(CONFIG, "sqlite:///:memory:", Path(tmpdir).joinpath("store"))
    assert len(diffp.index) == 0
    db_seed(diffp.db)
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_remove(tmpdir):
    """
    Test that remove works
    """

    diffp = Diffport(CONFIG, "sqlite:///:memory:", Path(tmpdir).joinpath("store"))
    db_seed(diffp.db)
    snap_hash = diffp.save_snapshot()
    diffp.remove_snapshot(snap_hash)
    assert len(diffp.index) == 0


def test_duplicates(tmpdir):
    """
    Test that duplicate snaps don't get added
    """

    diffp = Diffport(CONFIG, "sqlite:///:memory:", Path(tmpdir).joinpath("store"))
    db_seed(diffp.db)
    diffp.save_snapshot()
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_diff(tmpdir):
    """
    Test diff reporting
    """

    diffp = Diffport(CONFIG, "sqlite:///:memory:", Path(tmpdir).joinpath("store"))
    db_seed(diffp.db)
    old_hash = diffp.save_snapshot()
    db_seed(diffp.db)
    new_hash = diffp.save_snapshot()
    expected_report = WatcherNumberOfRows.report(1, CONFIG[0]["config"])
    assert diffp.diff(old_hash, new_hash) == expected_report
