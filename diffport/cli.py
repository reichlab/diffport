"""
Command Line::

  Usage:
    diffport save [--identifier=ID] [--config=CFG]
    diffport (rm | remove) <snap-hash> [--config=CFG]
    diffport (ls | list) [--config=CFG]
    diffport diff <snap-old> <snap-new> [--config=CFG]

  Arguments:
    save                 Save a snapshot at current time
    rm, remove           Remove a snapshot
    ls, list             List all the summary snapshots
    diff                 Return diff summary for the two snapshots

  Options:
    --config=CFG         Configuration file [default: ./diffport.yaml]
    -h, --help           Open help
    -v, --version        Show version
"""

import sys
from .core import Diffport
from docopt import docopt  # type: ignore
from pathlib import Path

def main():
    args = docopt(__doc__, argv=sys.argv[1:], version="v0.1.0")
    diffp = Diffport(Path(args["--config"]))

    if args["save"]:
        diffp.take_snapshot(args["--identifier"])
    elif args["rm"] or args["remove"]:
        reply = input("Are you sure? [y/n] : ").lower().strip()
        if reply[0] == "y":
            diffp.remove_snapshot(args["<snap-hash>"])
    elif args["ls"] or args["list"]:
        diffp.list_snapshots()
    elif args["diff"]:
        diffp.diff(args["<snap-old>"], args["<snap-new>"])
