"""
Test core class
"""

from diffport.core import Diffport
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
