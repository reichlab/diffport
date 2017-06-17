"""
Storate for snapshots
"""

import yaml
from abc import ABC, abstractmethod
from pathlib import Path


class Store(ABC):

    @abstractmethod
    def get_snapshot(self, snap_hash):
        pass

    @abstractmethod
    def get_index(self):
        pass

class StoreDirectory(Store):
    """
    Store snapshots in a directory
    """

    def __init__(self, directory_path: Path) -> None:
        self.path = directory_path
        self.path.mkdir(parents=True, exist_ok=True)

        # Load everything upfront
        self.init_snaps()

    def init_snaps(self):
        self.snaps = []
        files = [it for it in self.path.iterdir() if it.is_file()]

        for sf in files:
            with sf.open() as fp:
                self.snaps.append(yaml.load(fp))

    def get_index(self):
        """
        Return a thin index of items in store
        """

        return [{k:v for k, v in snap if k != "items"} for snap in self.snaps]

    def get_snapshot(self, snap_hash):
        """
        Return snap item for hash
        """

        try:
            (snap for snap in self.snaps if snap["hash"] == snap_hash)[0]
        except IndexError:
            return None
