"""
Storate for snapshots
"""

import gzip
import json
from abc import ABC, abstractmethod
from pathlib import Path


class Store(ABC):

    @abstractmethod
    def get_snapshot(self, snap_hash):
        ...

    @abstractmethod
    def get_index(self):
        ...

    @abstractmethod
    def add_snapshot(self, snap):
        ...

    @abstractmethod
    def remove_snapshot(self, snap_hash):
        ...

class StoreDirectory(Store):
    """
    Store snapshots in a directory
    """

    def __init__(self, directory_path: Path) -> None:
        self.path = directory_path
        self.path.mkdir(parents=True, exist_ok=True)

        # Load everything upfront
        # TODO: Don't load everything upfront
        self.init_snaps()

    def init_snaps(self):
        self.snaps = []
        files = [it for it in self.path.iterdir() if it.is_file() and it.suffix == ".gz"]

        for sf in files:
            with gzip.open(sf) as fp:
                self.snaps.append(json.loads(fp.read().decode("utf-8")))

    def get_index(self):
        """
        Return a thin index of items in store
        """

        return sorted([
            {k:v for k, v in snap.items() if k != "items"} for snap in self.snaps
        ], key=lambda x: x["time"], reverse=True)

    def get_snapshot(self, snap_hash):
        """
        Return snap item for hash
        """

        try:
            return next((snap for snap in self.snaps if snap["hash"] == snap_hash))
        except IndexError:
            return None

    def add_snapshot(self, snap):
        self.snaps.append(snap)

        with gzip.open(self.path.joinpath(f"{snap['time']}.gz"), "w") as fp:
            fp.write(json.dumps(snap).encode("utf-8"))

    def remove_snapshot(self, snap_hash):
        snap_idx = next((idx for idx, it in enumerate(self.snaps) if it["hash"] == snap_hash))
        self.path.joinpath(str(self.snaps[snap_idx]["time"]) + ".gz").unlink()
        self.snaps.pop(snap_idx)
