"""
Test core class
"""

from diffport.core import Diffport
from diffport.watchers import *
from pathlib import Path
from random import random
import pytest
import dataset


# Test config
SCHEMAS = [
    "scm_one",
    "scm_two"
]
TABLES = [
    "pub_table",
    "scm_one.test_table_one",
    "scm_two.test_table_one",
    "scm_two.test_table_two",
    "scm_two.test_table_three",
    "scm_two.test_table_four",
    "scm_two.test_table_five",
]
CONFIG = [{
    "name": "number-of-rows",
    "config": {
        "groupby": [],
        "table": TEST_TABLE
    }
}]

@pytest.fixture
def pgurl(request):
    """
    Return url for connecting to postgres
    """

    # Fill in stuff
    url = "postgresql://postgres@localhost:5432/diffport_test_db"
    db = dataset.connect(url)

    for schema in SCHEMAS:
        db.query(f"CREATE SCHEMA {schema};")

    for table in TABLES:
        db.query(f"CREATE TABLE {table};")

    def clear_db():
        for table in TABLES:
            db.query(f"DROP TABLE {table};")
        for schema in SCHEMAS:
            db.query(f"DROP SCHEMA {schema} CASCADE;")

    request.addfinalizer(clear_db)
    return url

@pytest.fixture
def diffp(tmpdir, pgurl):
    """
    Return a diffport instance
    """

    diffp = Diffport(CONFIG, Path(tmpdir).joinpath("store"))
    diffp.connect(pgurl)
    return diffp


def db_seed(db):
    """
    Add dummy item to db for testing
    """

    table = db[TEST_TABLE]
    table.insert({
        "rand": random()
    })

def test_list(diffp):
    """
    Test that listing is alright
    """

    assert len(diffp.index) == 0
    db_seed(diffp.db)
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_remove(diffp):
    """
    Test that remove works
    """

    db_seed(diffp.db)
    snap_hash = diffp.save_snapshot()
    diffp.remove_snapshot(snap_hash)
    assert len(diffp.index) == 0


def test_duplicates(diffp):
    """
    Test that duplicate snaps don't get added
    """

    db_seed(diffp.db)
    diffp.save_snapshot()
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_diff(diffp):
    """
    Test diff reporting
    """

    db_seed(diffp.db)
    old_hash = diffp.save_snapshot()
    db_seed(diffp.db)
    new_hash = diffp.save_snapshot()
    expected_report_tail = WatcherNumberOfRows.report(1, CONFIG[0]["config"])
    assert diffp.diff(old_hash, new_hash).endswith(expected_report_tail)
