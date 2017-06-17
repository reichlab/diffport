"""
Modules for watchers
"""

# Exceptions
class WatcherNotImplemented(Exception):
    pass

class WatcherError(Exception):
    pass

class Watcher:
    def __init__(self, watcher_config):
        pass

    def take_snapshot(self, config):
        """
        Take snapshot and return Snapshot object for current watcher
        """

        pass

    def diff(self, other):
        pass
