"""
Modules for watchers
"""

from abc import ABC, abstractmethod

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
        return db[config["table"]].count()

    @staticmethod
    def diff(a, b):
        pass

class WatcherTablesInSchema(Watcher):

    @staticmethod
    def take_snapshot(db, config):
        """
        Save list of tables in given schema
        """

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
