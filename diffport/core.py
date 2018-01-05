"""
Core things
"""

import dataset  # type: ignore
import hashlib
import json
import sys
import time
from .watchers import (
    NumberOfRowsHash, NumberOfRows,
    SchemaTables, SchemaColumns,
    TableChange
)
from datetime import datetime
from pathlib import Path
from typing import Dict
from .store import StoreDirectory


WATCHER_MAP = {
    "number-of-rows-hash": NumberOfRowsHash,
    "number-of-rows": NumberOfRows,
    "tables-in-schema": SchemaTables,
    "columns-in-schema": SchemaColumns,
    "table-change": TableChange
}


class Diffport:
    """
    Main diffport class. Coordinates the cli, watchers and the storage backend
    """

    def __init__(self, config: Dict, store_path: Path) -> None:
        """
        Initialize diffport using the provided config
        """

        self.config = config
        self.store = StoreDirectory(store_path)
        self.index = self.store.get_index()

    def connect(self, database_url: str):
        """
        Connect to the database
        """

        self.db = dataset.connect(database_url)

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

    def report(self, old_snap_hash, new_snap_hash):
        """
        Report diff for the given hashes
        """

        old_snap = self.store.get_snapshot(old_snap_hash)
        new_snap = self.store.get_snapshot(new_snap_hash)

        old_items = old_snap["items"]
        new_items = new_snap["items"]

        # Take diffs only for watchers present in both old and new items
        old_watchers = [item["watcher"] for item in old_items]
        new_watchers = [item["watcher"] for item in new_items]
        reports = []

        for watcher in self.config:
            name = watcher["name"]
            try:
                old = old_items[old_watchers.index(name)]["data"]
                new = new_items[new_watchers.index(name)]["data"]
                diff = WATCHER_MAP[name].diff(old, new)
                if diff is not None:
                    reports.append(WATCHER_MAP[name].report(diff))
            except ValueError:
                continue

        # Add time information about snapshots as the header
        old_time = datetime.fromtimestamp(old_snap["time"]).strftime("%Y-%m-%d %H:%M:%S")
        new_time = datetime.fromtimestamp(new_snap["time"]).strftime("%Y-%m-%d %H:%M:%S")

        header = "# Database changes\n\n"
        header += "> Between snapshots\n\n"
        header += f"> - at {old_time} (*{old_snap_hash}*)\n"
        header += f"> - at {new_time} (*{new_snap_hash}*)\n\n"

        return header + "\n\n".join(reports)
