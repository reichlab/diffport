"""
Test core class
"""

from diffport.core import Diffport
from diffport.watchers import *
from pathlib import Path
from random import random
import pytest
import dataset

@pytest.fixture
def pgurl(request):
    """
    Return url for connecting to postgres
    """

    # Fill in stuff
    url = "postgresql://postgres@localhost:5432/diffport_test_db"
    db = dataset.connect(url)

    def clear_db():
        # Remove left-out stuff
        db.query("DROP SCHEMA public CASCADE;")
        db.query("CREATE SCHEMA public;")

    request.addfinalizer(clear_db)
    return url

def get_diffp(path, config, url):
    """
    Return a diffport instance
    """

    diffp = Diffport(config, Path(path).joinpath("store"))
    diffp.connect(url)
    return diffp

def test_list(tmpdir, pgurl):
    """
    Test that listing is alright
    """

    config = [{
        "name": "tables-in-schema",
        "config": "scm"
    }]

    diffp = get_diffp(tmpdir, config, pgurl)
    diffp.db.query("CREATE SCHEMA scm;")
    diffp.db.query("CREATE TABLE scm.tab (num integer);")

    assert len(diffp.index) == 0
    diffp.save_snapshot()
    assert len(diffp.index) == 1
    diffp.db.query("DROP SCHEMA scm CASCADE;")


def test_remove(tmpdir, pgurl):
    """
    Test that remove works
    """

    config = [{
        "name": "tables-in-schema",
        "config": "scm"
    }]

    diffp = get_diffp(tmpdir, config, pgurl)
    diffp.db.query("CREATE SCHEMA scm;")
    diffp.db.query("CREATE TABLE scm.tab (num integer);")

    snap_hash = diffp.save_snapshot()
    diffp.remove_snapshot(snap_hash)
    assert len(diffp.index) == 0
    diffp.db.query("DROP SCHEMA scm CASCADE;")


# def test_duplicates(diffp):
#     """
#     Test that duplicate snaps don't get added
#     """

#     db_seed(diffp.db)
#     diffp.save_snapshot()
#     diffp.save_snapshot()
#     assert len(diffp.index) == 1


# def test_diff(diffp):
#     """
#     Test diff reporting
#     """

#     db_seed(diffp.db)
#     old_hash = diffp.save_snapshot()
#     db_seed(diffp.db)
#     new_hash = diffp.save_snapshot()
#     expected_report_tail = WatcherNumberOfRows.report(1, CONFIG[0]["config"])
#     assert diffp.diff(old_hash, new_hash).endswith(expected_report_tail)
