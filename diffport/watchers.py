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

            # ORDER BY lets us switch rows on sequentially
            grouped_data = []
            hashes = []
            prev_group_values = None
            for res in db.query(stmt):
                group_values = [res[field] for field in config["groupby"]]

                if prev_group_values is None:
                    prev_group_values = group_values

                if group_values != prev_group_values:
                    grouped_data.append([*group_values, list(hashes)])
                    prev_group_values = group_values
                    hashes = []
                else:
                    hashes.append(res["hash"])
            return grouped_data
        else:
            # Total count
            stmt = f"SELECT md5({config['table']}::text) as hash FROM {config['table']}"
            return [r["hash"] for r in db.query(stmt)]

    @staticmethod
    def diff(old, new):

        def _get_diff(old_hashes, new_hashes):
            """
            Get diff counts between list of hashes
            """

            # [removed, added]
            return [len(set(old) - set(new)), len(set(new) - set(old))]

        if type(old[0]) == type(new[0]) == str:
            # This data is without grouping
            diff = _get_diff(old, new)
            return {
                "removed": diff[0],
                "added": diff[1]
            }
        else:
            # Work with group values of the old snapshot
            new_group_identifiers = [group_row[:-1] for group_row in new]
            changes = []
            for group_row in old:
                old_group_identifier = group_row[:-1]
                if old_group_identifier in new_group_identifiers:
                    new_hashes = new[new_group_identifiers.index(old_group_identifier)][-1]
                    old_hashes = group_row[-1]
                    changes.append([*old_group_identifier, *_get_diff(old_hashes, new_hashes)])

            return changes

    @staticmethod
    def report(diff, config: Dict) -> str:

        out = f"## Changes in number of rows\n\n### Table `{config['table']}`\n\n"

        if type(diff) is dict:
            change = f"{diff['removed']} rows removed, {diff['added']} added"
        else:
            change = tabulate(diff, headers=[*config["groupby"], "rows removed", "rows added"])

        return tpl_number_of_rows.render(
            table_name=config,
            change=change,
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
