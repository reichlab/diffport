"""
Tests for watchers
"""

from diffport.core import Diffport
from diffport.watchers import *
from pathlib import Path
from random import random, randint
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


class TestNumberOfRows:
    """
    Tests for number-of-rows
    """

    pass


class TestTablesInSchema:
    """
    Tests for tables-in-schema watcher
    """

    pass


class TestColumnsInSchema:
    """
    Tests for columns-in-schema
    """

    config = [{
        "name": "columns-in-schema",
        "config": ["scm_one", "scm_two", "scm_three"]
    }]

    schema_tables = [
        "scm_one.tab_one",
        "scm_one.tab_two",
        "scm_two.tab_one",
        "scm_three.tab_one"
    ]

    to_add = ["scm_one.tab_one"]
    to_remove = ["scm_one.tab_one", "scm_one.tab_two", "scm_two.tab_one"]

    def init_db(self, db):
        for schema in self.config[0]["config"]:
            db.query(f"CREATE SCHEMA {schema};")
        for table in self.schema_tables:
            db.query(f"CREATE TABLE {table} (one INTEGER, pruned_col INTEGER);")

    def fill_db(self, db):
        for table in self.to_add:
            db.query(f"ALTER TABLE {table} ADD COLUMN added_col INTEGER;")
        for table in self.to_remove:
            db.query(f"ALTER TABLE {table} DROP COLUMN pruned_col;")

    def clean_db(self, db):
        for schema in self.config[0]["config"]:
            db.query(f"DROP SCHEMA {schema} CASCADE;")

    def test_diff(self, tmpdir, pgurl):
        diffp = get_diffp(tmpdir, self.config, pgurl)
        self.init_db(diffp.db)
        old_hash = diffp.save_snapshot()
        self.fill_db(diffp.db)
        new_hash = diffp.save_snapshot()
        self.clean_db(diffp.db)

        diff = [
            ["scm_one", {
                "removed": ["pruned_col"],
                "added": ["added_col"]
            }],
            ["scm_two", {
                "removed": ["pruned_col"],
                "added": []
            }]
        ]
        report = WatcherColumnsInSchema.report(diff, self.config[0]["config"])
        assert diffp.diff(old_hash, new_hash).endswith(report)


class TestTableChange:
    """
    Tests for table-change
    """

    config = [{
        "name": "table-change",
        "config": {
            "schemas": ["scm_one", "scm_two"],
            "tables": ["tab_one", "tab_two"]
        }
    }]

    schema_tables = [
        "scm_one.tab_one",
        "scm_one.tab_two",
        "scm_two.tab_one",
        "scm_two.tab_two",
        "scm_two.tab_three",
        "scm_two.tab_four"
    ]

    to_change = [
        "tab_one",
        "scm_one.tab_two",
        "scm_two.tab_three",
        "scm_two.tab_four"
    ]

    def init_db(self, db):
        for schema in self.config[0]["config"]["schemas"]:
            db.query(f"CREATE SCHEMA {schema};")
        for table in self.schema_tables + self.config[0]["config"]["tables"]:
            db.query(f"CREATE TABLE {table} (num INTEGER);")

    def fill_db(self, db):
        for table in self.to_change:
            db.query(f"INSERT INTO {table} VALUES ({randint(0, 100)});")

    def clean_db(self, db):
        for table in self.schema_tables + self.config[0]["config"]["tables"]:
            db.query(f"DROP TABLE {table};")
        for schema in self.config[0]["config"]["schemas"]:
            db.query(f"DROP SCHEMA {schema} CASCADE;")

    def test_diff(self, tmpdir, pgurl):
        diffp = get_diffp(tmpdir, self.config, pgurl)
        self.init_db(diffp.db)
        old_hash = diffp.save_snapshot()
        self.fill_db(diffp.db)
        new_hash = diffp.save_snapshot()
        self.clean_db(diffp.db)

        diff = self.to_change
        report = WatcherTableChange.report(diff, self.config[0]["config"])
        assert diffp.diff(old_hash, new_hash).endswith(report)
