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

    @abstractmethod
    def take_snapshot(self, config):
        """
        Take snapshot and return Snapshot object for current watcher
        """

        pass

    @abstractmethod
    def diff(self, other):
        pass
