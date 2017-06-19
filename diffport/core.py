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
from .store import StoreDirectory


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

        self.store = StoreDirectory(config_file.parent.joinpath("diffport.d"))
        self.index = self.store.get_index()

    def take_snapshot(self, identifier=None):
        # TODO: save snapshot
        snap = {
            "hash": "",
            "time": int(time.time()),
            "items": ""
        }
        if identifier:
            snap["identifier"] = identifier

        if snap["hash"] in [item["hash"] for item in self.index]:
            warn("Snapshot {} already exists, skipping".format(snap["hash"]))
        else:
            self.store.add_snapshot(snap)

    def remove_snapshot(self, snap_hash):
        self.store.remove_snapshot(snap_hash)

    def list_snapshots(self):
        if len(self.index) == 0:
            err("No snaphots found")
        else:
            print()
            sorted_snaps = sorted(self.index, key=lambda x: x["time"], reverse=True)
            for it in sorted_snaps:
                time_str = datetime.fromtimestamp(it["time"]).strftime("%Y-%m-%d %H:%M:%S")
                info("hash: {}".format(it["hash"]))
                print("time: {}\n".format(time_str))
                if "identifier" in it:
                    print("\t{}\n".format(it["identifier"]))


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
