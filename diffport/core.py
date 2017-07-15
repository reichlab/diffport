"""
Core things
"""

import colorama  # type: ignore
import dataset  # type: ignore
import hashlib
import json
import sys
import time
import yaml
from colorama import Fore, Back, Style
from datetime import datetime
from pathlib import Path
from .watchers import WatcherNumberOfRows, WatcherTablesInSchema
from .store import StoreDirectory
from .exceptions import ConfigError


WATCHER_MAP = {
    "number-of-rows": WatcherNumberOfRows,
    "tables-in-schema": WatcherTablesInSchema
}

# Colored prints
colorama.init(autoreset=True)


def err(text, end="\n"):
    print(Fore.RED + Style.BRIGHT + text, end=end)


def info(text, end="\n"):
    print(Fore.BLUE + Style.BRIGHT + text, end=end)


def warn(text, end="\n"):
    print(Fore.YELLOW + Style.BRIGHT + text, end=end)


class Diffport:
    """
    Main diffport class. Coordinates the cli, watchers and the storage backend
    """

    def __init__(self, config_file: Path) -> None:
        """
        Initialize diffport using the provided config file path.
        """

        if not config_file.is_file():
            raise ConfigError("Config file not found")

        with config_file.open() as fp:
            self._config = yaml.load(fp)

        self.db = dataset.connect()

        self.store = StoreDirectory(config_file.parent.joinpath("diffport.d"))
        self.index = self.store.get_index()

    def save_snapshot(self, identifier: str = None) -> None:
        """
        Take a snapshot by looping over the watchers specified in the config
        and save it via store object. Optionally apply identifier to it.
        """

        items = [{
            "watcher": watcher["name"],
            "data": WATCHER_MAP[watcher["name"]].take_snapshot(self.db, watcher["config"])
        } for watcher in self._config]

        sorted_dump = json.dumps(items, sort_keys=True)
        snap_hash = hashlib.sha1(sorted_dump.encode("utf-16be")).hexdigest()

        snap = {"hash": snap_hash, "time": int(time.time()), "items": items}

        if identifier:
            snap["identifier"] = identifier

        if snap["hash"] in [item["hash"] for item in self.index]:
            warn("Snapshot {} already exists, skipping".format(snap["hash"]))
        else:
            self.store.add_snapshot(snap)
            info("Snapshot {} saved".format(snap["hash"]))

    def remove_snapshot(self, snap_hash: str):
        """
        Remove given snap hash from the store
        """

        self.store.remove_snapshot(snap_hash)
        info("Snapshot {} removed".format(snap_hash))

    def list_snapshots(self, json_output=False):
        """
        List snapshots in most recent first order. Print output in json for
        program ingestion if json_output is true.
        """

        if json_output:
            print(json.dumps(self.index), end="")
            return

        if len(self.index) == 0:
            err("No snaphots found")
            sys.exit(1)
        else:
            print()
            for it in self.index:
                time_str = datetime.fromtimestamp(
                    it["time"]).strftime("%Y-%m-%d %H:%M:%S")
                info("hash: {}".format(it["hash"]))
                print("time: {}\n".format(time_str))
                if "identifier" in it:
                    print("\t{}\n".format(it["identifier"]))

    def diff(self, old_snap_hash=None, new_snap_hash=None):
        """
        Return diff for the given hashes (or the last two snapshots)
        """

        if not (old_snap_hash and new_snap_hash):
            if len(sel.index) < 2:
                err("Not enough snapshots available for diffing")
                sys.exit(1)
            else:
                new_snap_hash, old_snap_hash = [
                    snap["hash"] for snap in self.index[:2]
                ]

        old_snap = self.store.get_snapshot(old_snap_hash)
        new_snap = self.store.get_snapshot(new_snap_hash)

        report = ""

        # TODO Assuming the snaps to have same type of items as of now
        for idx, item in enumerate(old_snap["items"]):
            report += WATCHER_MAP[item["watcher"]]().diff(item["data"], new_snap["items"][idx]["data"])

        print(report)
