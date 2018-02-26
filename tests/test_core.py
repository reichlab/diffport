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


@pytest.fixture
def config():
    """
    Return default diffport config
    """

    return [{
        "name": "tables-in-schema",
        "config": ["scm"]
    }]


@pytest.fixture
def diffp(request, tmpdir, config, pgurl):
    """
    Return a diffport instance
    """

    diffp = Diffport(config, Path(tmpdir).joinpath("store"))
    diffp.connect(pgurl)

    diffp.db.query("CREATE SCHEMA scm;")
    diffp.db.query("CREATE TABLE scm.tab (num INTEGER);")

    def clear_db():
        diffp.db.query("DROP SCHEMA scm CASCADE;")

    request.addfinalizer(clear_db)

    return diffp


def test_list(diffp):
    """
    Test that listing is alright
    """

    assert len(diffp.index) == 0
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_remove(diffp):
    """
    Test that remove works
    """

    snap_hash = diffp.save_snapshot()
    diffp.remove_snapshot(snap_hash)
    assert len(diffp.index) == 0


def test_duplicates(diffp):
    """
    Test that duplicate snaps don't get added
    """

    snap_hash = diffp.save_snapshot()
    diffp.save_snapshot()
    diffp.save_snapshot()
    assert len(diffp.index) == 1


def test_diff(diffp):
    """
    Test diff reporting
    """

    old_hash = diffp.save_snapshot()
    diffp.db.query("CREATE TABLE scm.second (num INTEGER);")
    new_hash = diffp.save_snapshot()
    diff = {
        "config": ["scm"],
        "data": [["scm", {
            "removed": [],
            "added": ["second"]
        }]]
    }
    report = SchemaTables.report(diff)
    assert diffp.report(old_hash, new_hash).endswith(report)
