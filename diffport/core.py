"""
Core things
"""

import dataset  # type: ignore
import hashlib
import json
import sys
import time
import yaml
from pathlib import Path
from typing import Dict
from .watchers import WatcherNumberOfRows, WatcherTablesInSchema
from .store import StoreDirectory


WATCHER_MAP = {
    "number-of-rows": WatcherNumberOfRows,
    "tables-in-schema": WatcherTablesInSchema
}


class Diffport:
    """
    Main diffport class. Coordinates the cli, watchers and the storage backend
    """

    def __init__(self, config: Dict, database_url: str, store_path: Path) -> None:
        """
        Initialize diffport using the provided config
        """

        self.config = config
        self.db = dataset.connect(database_url)
        self.store = StoreDirectory(store_path)
        self.index = self.store.get_index()

    def save_snapshot(self, identifier: str = None):
        """
        Take a snapshot by looping over the watchers specified in the config
        and save it via store object. Optionally apply identifier to it.
        """

        items = [{
            "watcher": watcher["name"],
            "data": WATCHER_MAP[watcher["name"]].take_snapshot(self.db, watcher["config"])
        } for watcher in self.config]

        sorted_dump = json.dumps(items, sort_keys=True)
        snap_hash = hashlib.sha1(sorted_dump.encode("utf-16be")).hexdigest()

        snap = {"hash": snap_hash, "time": int(time.time()), "items": items}

        if identifier:
            snap["identifier"] = identifier

        if snap["hash"] in [item["hash"] for item in self.index]:
            return None
        else:
            self.store.add_snapshot(snap)
            self.index = self.store.get_index()
            return snap["hash"]

    def remove_snapshot(self, snap_hash: str):
        """
        Remove given snap hash from the store
        """

        self.store.remove_snapshot(snap_hash)
        self.index = self.store.get_index()

    def diff(self, old_snap_hash, new_snap_hash):
        """
        Return diff for the given hashes
        """

        old_items = self.store.get_snapshot(old_snap_hash)["items"]
        new_items = self.store.get_snapshot(new_snap_hash)["items"]

        # Take diffs only for watchers present in both old and new items
        old_watchers = [item["watcher"] for item in old_items]
        new_watchers = [item["watcher"] for item in new_items]
        reports = []

        for watcher in self.config:
            name = watcher["name"]
            try:
                old = old_items[old_watchers.index(name)]["data"]
                new = new_items[new_watchers.index(name)]["data"]
                diff = WATCHER_MAP[name]().diff(old, new)
                if diff is not None:
                    reports.append(WATCHER_MAP[name]().report(diff, watcher["config"]))
            except ValueError:
                continue

        return "\n".join(reports)
