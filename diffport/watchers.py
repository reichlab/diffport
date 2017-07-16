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
        """

        # TODO Support multiple entries
        if len(config["groupby"]) > 0:
            stmt = "SELECT {0}, count(*) AS count FROM {1} GROUP BY {0} ORDER BY {0}".format(", ".join(config["groupby"]), config["table"])
            return [r for r in db.query(stmt)]
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
            merged["count diff"] = merged["count_x"] - merged["count_y"]
            del merged["count_x"]
            del merged["count_y"]
            return merged

    @staticmethod
    def report(diff, config: Dict) -> str:

        if type(diff) is int:
            return f"Change: {diff} rows"
        else:
            out = "Changes: \n\n"
            out += tabulate(merged, headers="keys")
            return out

class WatcherTablesInSchema(Watcher):
    """
    Watch for tables added/removed in schema
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save list of tables in given schema
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
