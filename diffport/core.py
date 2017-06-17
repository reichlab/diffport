"""
Core things
"""

import colorama # type: ignore
import hashlib
import json
import yaml
import time
from colorama import Fore, Back, Style
from datetime import datetime
from pathlib import Path
from .watchers import Watcher


WATCHER_MAP = {
    "number-of-rows": Watcher
}


# Colored prints
colorama.init(autoreset=True)

def err(text, end="\n"):
    print(Fore.RED + Style.BRIGHT + text, end=end)

def info(text, end="\n"):
    print(Fore.BLUE + Style.BRIGHT + text, end=end)

def warn(text, end="\n"):
    print(Fore.YELLOW + Style.BRIGHT + text, end=end)


# Exceptions
class ConfigError(Exception):
    pass


class Diffport:
    def __init__(self, config_file: Path) -> None:
        if not config_file.is_file():
            raise ConfigError("Config file not found")

        with config_file.open() as fp:
            self._config = yaml.load(fp)

        if "db" not in self._config:
            raise ConfigError("`db` not in config")

        self.config_dir = config_file.parent
        self.store_path = self.config_dir.joinpath("diffport.d")
        self.index_path = self.store_path.joinpath("index")
        self.snapshots_path = self.store_path.joinpath("snapshots")
        self.init_store()

    def init_store(self):
        """
        Initialize store and create stubs
        """

        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        if not self.index_path.is_file():
            self._index = []
            self.write_index()
        else:
            with self.index_path.open() as fp:
                self._index = yaml.load(fp)

    def write_index(self):
        """
        Write index content back to file
        """

        with self.index_path.open("w") as fp:
            yaml.dump(self._index, fp)

    def take_snapshot(self, identifier=None):
        # TODO: save snapshot
        # Insert info in index
        it = {
            "hash": snap.hash,
            "time": int(time.time())
        }
        if identifier:
            it["identifier"] = identifier
        self._index.append(it)
        self.write_index()

    def remove_snapshot(self, snap_hash):
        """
        Remove given snapshot
        """

        self.snapshots_path.joinpath(snap_hash).unlink()
        self._index = [it for it in self._index if it["hash"] != snap_hash]
        self.write_index()

    def list_snapshots(self):
        if len(self._index) == 0:
            err("No snaphots found")
        else:
            print()
            sorted_snaps = sorted(self._index, key=lambda x: x["time"], reverse=True)
            for it in sorted_snaps:
                time_str = datetime.fromtimestamp(it["time"]).strftime("%Y-%m-%d %H:%M:%S")
                info("hash: {}".format(it["hash"]))
                print("time: {}\n".format(time_str))
                if "identifier" in it:
                    print("\t{}\n".format(it["identifier"]))

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
