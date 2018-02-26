"""
Command Line::

  Usage:
    diffport save [--identifier=ID] [--config=CFG] [--source=CON] [--dialect=DIA]
    diffport (rm | remove) <snap-hash> [--config=CFG]
    diffport (ls | list) [--json] [--config=CFG]
    diffport diff [<snap-old> <snap-new>] [--config=CFG]

  Arguments:
    save                 Save a snapshot at current time
    rm, remove           Remove a snapshot
    ls, list             List all the summary snapshots
    diff                 Return diff summary for the two snapshots
                         (or the two latest ones if hashes not provided)

  Options:
    --json               Output for machines
    --config=CFG         Configuration file [default: ./diffport.yaml]
    --source=CON         Database source [default: env]
    --dialect=DIA        Database type [default: postgresql]
    -h, --help           Open help
    -v, --version        Show version
"""

import colorama
import os
import sys
import yaml
from .core import Diffport
from .connection import get_connection_string
from colorama import Fore, Back, Style
from datetime import datetime
from docopt import docopt  # type: ignore
from pathlib import Path


# Colored prints
colorama.init(autoreset=True)


def err(text, end="\n"):
    print(Fore.RED + Style.BRIGHT + text, end=end)


def info(text, end="\n"):
    print(Fore.BLUE + Style.BRIGHT + text, end=end)


def warn(text, end="\n"):
    print(Fore.YELLOW + Style.BRIGHT + text, end=end)


def main():
    args = docopt(__doc__, argv=sys.argv[1:], version="v0.4.0")

    config_file = Path(args["--config"])
    store_path = config_file.parent.joinpath("diffport.d")

    if not config_file.is_file():
        raise Exception("Config file not found")

    with config_file.open() as fp:
        diffp = Diffport(yaml.load(fp), store_path)

    if args["save"]:
        source_path = str(Path(args["--source"]).expanduser().absolute())
        database_url = get_connection_string(source_path, args["--dialect"])
        diffp.connect(database_url)

        saved_hash = diffp.save_snapshot(args["--identifier"])
        if saved_hash:
            info(f"Snapshot {saved_hash} saved")
        else:
            warn("Snapshot data not changed, skipping")
    elif args["rm"] or args["remove"]:
        reply = input("Are you sure? [y/n] : ").lower().strip()
        if reply[0] == "y":
            diffp.remove_snapshot(args["<snap-hash>"])
            info(f"Snapshot {args['snap-hash']} removed")
    elif args["ls"] or args["list"]:
        if args["--json"]:
            print(json.dumps(diffp.index), end="")
        else:
            if len(diffp.index) == 0:
                err("No snapshots found")
                sys.exit(1)
            else:
                print()
                for it in diffp.index:
                    time_str = datetime.fromtimestamp(it["time"]).strftime("%Y-%m-%d %H:%M:%S")
                    info(f"hash: {it['hash']}")
                    print(f"time: {time_str}")
                    if "identifier" in it:
                        print(f"\t{it['identifier']}\n")
    elif args["diff"]:
        if args["<snap-old>"] and args["<snap-new>"]:
            # Both snapshot ids given
            print(diffp.report(args["<snap-old>"], args["<snap-new>"]))
        else:
            # Get last two snapshots
            if len(diffp.index) < 2:
                err("Not enough snapshots available for diffing")
                sys.exit(1)
            else:
                new_snap_hash, old_snap_hash = [
                    snap["hash"] for snap in diffp.index[:2]
                ]
                print(diffp.report(old_snap_hash, new_snap_hash))
