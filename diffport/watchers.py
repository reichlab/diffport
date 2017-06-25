"""
Modules for watchers
"""

import pandas as pd
from abc import ABC, abstractmethod
from tabulate import tabulate

# Exceptions
class WatcherNotImplemented(Exception):
    pass

class WatcherError(Exception):
    pass

class Watcher(ABC):

    @staticmethod
    @abstractmethod
    def take_snapshot(db, config):
        ...

    @staticmethod
    @abstractmethod
    def diff(old, new):
        ...

class WatcherNumberOfRows(Watcher):

    @staticmethod
    def take_snapshot(db, config):
        """
        Take snapshot for number of rows in given table grouped by asked fields
        """

        # TODO Support multiple entries
        if len(config["groupby"]) > 0:
            stmt = "SELECT {0}, count(*) AS count FROM {1} GROUP BY {0} ORDER BY {0}".format("', ".join(config["groupby"]), config["table"])
            return [r for r in db.query()]
        else:
            # Total count
            return db[config["table"]].count()

    @staticmethod
    def diff(a, b):
        # Check if both have same type of snapshot
        assert type(a) == type(b)

        if type(a) is int:
            return "Change: {} rows".format(b - a)
        else:
            a = pd.DataFrame(a)
            b = pd.DataFrame(b)
            merge_keys = list(a.columns[:-1])
            merged = pd.merge(a, b, how="outer", on=merge_keys)
            merged["count diff"] = merged["count_x"] - merged["count_y"]
            del merged["count_x"]
            del merged["count_y"]

            out = "Changes: \n\n"
            out += tabulate(merged, headers="keys")
            out += "\n\n"
            return out

class WatcherTablesInSchema(Watcher):

    @staticmethod
    def take_snapshot(db, config):
        """
        Save list of tables in given schema
        """

        # TODO Support multiple entries
        res = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(config["schema"]))
        return [r["table_name"] for r in res]

    @staticmethod
    def diff(a, b):
        """
        Assume b to be the newer one
        """

        removed = list(set(a) - set(b))
        added = list(set(b) - set(a))

        out = ""
        if len(removed) != 0:
            out += "Removed tables :\n\n"
            for tb in removed:
                out += "- {}\n".format(tb)
            out += "\n\n"

        if len(added) != 0:
            out += "Added tables :\n\n"
            for tb in added:
                out += "- {}\n".format(tb)
            out += "\n\n"

        return out
