"""
Modules for watchers
"""

import pandas as pd
from abc import ABC, abstractmethod
from tabulate import tabulate
from typing import Dict
from .templates import *


class Watcher(ABC):

    @staticmethod
    @abstractmethod
    def take_snapshot(db, config: Dict):
        """
        Return a snapshot dictionary using the config and db.
        """
        ...

    @staticmethod
    @abstractmethod
    def diff(old, new):
        """
        Return a dictionary representing the diff between old and new snapshot.
        The output goes into report function for getting a markdown string.
        """
        ...

    @staticmethod
    @abstractmethod
    def report(diff, config: Dict) -> str:
        """
        Return a report in markdown format for given diff.
        """
        ...


class WatcherNumberOfRows(Watcher):
    """
    Watch for changes in number of rows in tables. Also provides grouped
    counts.
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Take snapshot for number of rows in given table grouped by asked fields

        config:
          groupby:
            - <list-item>
            - <list-item>
          table: <string>
        """

        # TODO Support multiple entries
        if "groupby" in config:
            group_fields = ", ".join(config["groupby"])
            select_fields = f"{group_fields}, md5({config['table']}::text) as hash"
            stmt = f"SELECT {select_fields} FROM {config['table']} ORDER BY {group_fields}"
            return [dict(r) for r in db.query(stmt)]
        else:
            # Total count
            return db[config["table"]].count()

    @staticmethod
    def diff(old, new):
        # Check if both have same type of snapshot
        assert type(old) == type(new)

        if type(old) is int:
            return new - old
        else:
            old = pd.DataFrame(old)
            new = pd.DataFrame(new)
            merge_keys = list(old.columns[:-1])
            merged = pd.merge(old, new, how="outer", on=merge_keys)
            merged["count diff"] = merged["count_y"] - merged["count_x"]
            del merged["count_x"]
            del merged["count_y"]
            return merged[merged["count diff"] != 0].reset_index(drop=True)

    @staticmethod
    def report(diff, config: Dict) -> str:

        out = f"## Changes in number of rows\n\n### Table `{config['table']}`\n\n"

        return tpl_number_of_rows.render(
            table_name=config,
            change=f"{diff} rows" if type(diff) else tabulate(diff, headers="keys")
        )


class WatcherTablesInSchema(Watcher):
    """
    Watch for tables added/removed in schema
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save list of tables in given schema

        config: <string>
        """

        # TODO Support multiple entries
        res = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(config))
        return [r["table_name"] for r in res]

    @staticmethod
    def diff(old, new):

        return {
            "removed": list(set(old) - set(new)),
            "added": list(set(new) - set(old))
        }

    @staticmethod
    def report(diff, config: Dict) -> str:

        return tpl_tables_in_schema.render(
            schema_name=config,
            added_tables=diff["added"],
            removed_tables=diff["removed"]
        )


class WatcherColumnsInSchema(Watcher):
    """
    Watch for columns added/removed considering all tables of a schema at a time
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save all distinct table in given schema

        config: <string>
        """

        # TODO Support multiple entries
        res = db.query(f"SELECT DISTINCT column_name FROM information_schema.columns WHERE table_schema = '{config}'")
        return [r["column_name"] for r in res]

    @staticmethod
    def diff(old, new):

        return {
            "removed": list(set(old) - set(new)),
            "added": list(set(new) - set(old))
        }

    @staticmethod
    def report(diff, config: Dict) -> str:

        return tpl_columns_in_schema.render(
            schema_name=config,
            added_columns=diff["added"],
            removed_columns=diff["removed"]
        )


class WatcherTableChange(Watcher):
    """
    Watch for table changes
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save all table hashes in given schema

        config:
          schemas:
            - <schema-one>
            - <schema-two>
          tables:
            - <table-one>
            - <table-two>
        """

        # Create a list of tables to look for
        tables = []
        try:
            tables += config["tables"]
        except KeyError:
            pass

        if "schemas" in config:
            for schema in config["schemas"]:
                res = db.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
                tables += [f"{schema}.{r['table_name']}" for r in res]

        # Create hash of tables
        def _table_hash(table):
            res = db.query(f"""SELECT md5(array_agg(md5((t.*)::varchar))::varchar) as hash
              FROM (
                SELECT *
                  FROM {table}
                ORDER BY 1
              ) AS t""")
            return res.next()["hash"]

        return { table: _table_hash(table) for table in tables }

    @staticmethod
    def diff(old, new):
        changed = []
        for table, checksum in old:
            if table in new:
                if new[table] != checksum:
                    changed.append(table)

        return changed

    @staticmethod
    def report(diff, config: Dict) -> str:

        return tpl_table_change.render(
            watched_schemas=config["schemas"],
            watched_tables=config["tables"],
            changed_tables=diff
        )
