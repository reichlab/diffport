"""
Command Line::

  Usage:
    diffport save [--identifier=ID] [--config=CFG]
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
    -h, --help           Open help
    -v, --version        Show version
"""

import os
import sys
from .core import Diffport
from docopt import docopt  # type: ignore
from pathlib import Path


def main():
    args = docopt(__doc__, argv=sys.argv[1:], version="v0.1.0")

    config_file = Path(args["--config"])
    store_path = config_file.parent.joinpath("diffport.d")

    if not config_file.is_file():
        raise ConfigError("Config file not found")

    try:
        database_url = os.environ["DATABASE_URL"]
    except KeyError:
        print("DATABASE_URL environment variable not set.")
        sys.exit(1)

    with config_file.open() as fp:
        diffp = Diffport(yaml.load(fp), database_url, store_path)

    if args["save"]:
        diffp.save_snapshot(args["--identifier"])
    elif args["rm"] or args["remove"]:
        reply = input("Are you sure? [y/n] : ").lower().strip()
        if reply[0] == "y":
            diffp.remove_snapshot(args["<snap-hash>"])
    elif args["ls"] or args["list"]:
        diffp.list_snapshots(args["--json"])
    elif args["diff"]:
        if args["<snap-old>"] and args["<snap-new>"]:
            # Both snapshot ids given
            diffp.diff(args["<snap-old>"], args["<snap-new>"])
        else:
            # Ask diffp to use latest two snapshots
            diffp.diff()
