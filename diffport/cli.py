"""
Command Line::

  Usage:
    diffport

  Options:
    -h --help                   Open help
    -v --version                Show version
"""

import sys
from docopt import docopt  # type: ignore

def main():
    args = docopt(__doc__, argv=sys.argv[1:], version="v0.1.0")
