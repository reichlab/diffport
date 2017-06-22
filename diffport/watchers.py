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
        return 0

    @staticmethod
    def diff(a, b):
        pass
