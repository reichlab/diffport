"""
Tests for store module
"""

from diffport.store import StoreDirectory
from pathlib import Path
import os
import time
import json
import gzip


def test_create_directory(tmpdir):
    """
    Test that store is creating a new directory
    """

    store_path = Path(tmpdir.join("store"))
    store = StoreDirectory(store_path)
    assert store_path.is_dir()

def test_add_snap(tmpdir):
    """
    Test that snapshot is added and persists
    """

    store_path = Path(tmpdir.join("store"))
    store = StoreDirectory(store_path)

    snap = {
        "time": time.time(),
        "identifier": "Test snapshot",
        "hash": "some-hash-here",
        "items": []
    }

    store.add_snapshot(snap)

    assert len(store.get_index()) == 1
    assert store.get_index()[0]["hash"] == snap["hash"]
    assert store.get_snapshot(snap["hash"]) == snap
    with gzip.open(store_path.joinpath(f"{snap['time']}.gz")) as fp:
        assert snap == json.load(fp)

def test_remove_snap(tmpdir):
    """
    Test that snap removal works
    """

    store_path = Path(tmpdir.join("store"))
    store = StoreDirectory(store_path)

    snap = {
        "time": time.time(),
        "identifier": "Test snapshot",
        "hash": "some-hash-here",
        "items": []
    }

    store.add_snapshot(snap)
    store.remove_snapshot(snap["hash"])

    assert len(store.get_index()) == 0
    assert not store_path.joinpath(str(snap["time"])).exists()
