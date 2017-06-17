"""
Core things
"""

import hashlib
import json
import yaml
from pathlib import Path
from .watchers import Watcher


WATCHER_MAP = {
    "number-of-rows": Watcher
}


# Exceptions
class ConfigError(Exception):
    pass

class Diffport:
    def __init__(self, config_file: Path) -> None:
        if not config_file.is_file():
            raise ConfigError("Config file not found")

        with config_file.open() as f:
            self._config = yaml.load(f)

        if "db" not in self._config:
            raise ConfigError("`db` not in config")

        self.config_dir = config_file.parent
        self.init_store()

    def init_store(self):
        store_path = self.config_dir.joinpath("diffport")
        snapshots_path = store_path.joinpath("snapshots")
        snapshots_path.mkdir(parents=True, exist_ok=True)

        index_path = store_path.joinpath("index")

        if not index_path.is_file():
            default_index = []
            with index_path.open("w") as fp:
                yaml.dump(default_index, fp)
            self._index = default_index
        else:
            with index_path.open() as fp:
                self._index = yaml.load(fp)

    def take_snapshot(self, identifier=None):
        pass

    def remove_snapshot(self, snap_hash):
        pass

    def list_snapshots(self):
        pass

    def diff(self):
        pass


class Snapshot:
    def __init__(self, items=[]):
        self._items = items

    def __add__(self, other):
        """
        Merge snapshots
        """

        return Snapshot(self._items + other._items)

    def __eq__(self, other):
        return self.hash == other.hash

    @property
    def hash(self):
        sorted_dump = json.dumps(self._items, sort_keys=True)
        return hashlib.sha1(sorted_dump.encode("utf-16be")).hexdigest()

    def save(self, directory_path):
        """
        Write data to the directory using the hash name
        """

        with directory_path.joinpath(self.hash).open("w") as fp:
            yaml.dump(self._items, fp)

    def load(self, file_path):
        """
        Load a snapshot from the given file
        """

        with file_path.open() as fp:
            self._items = yaml.load(fp)
