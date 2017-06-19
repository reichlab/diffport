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
    def take_snapshot(db_config):
        ...

    @staticmethod
    @abstractmethod
    def diff(a, b):
        ...

class WatcherNumberOfRows(Watcher):

    @staticmethod
    def take_snapshot(db_config):
        return {"12": "ererere"}

    @staticmethod
    def diff(a, b):
        pass

class WatcherTablesInSchema(Watcher):

    @staticmethod
    def take_snapshot(db_config):
        return {"12": "sdsds"}

    @staticmethod
    def diff(a, b):
        pass
