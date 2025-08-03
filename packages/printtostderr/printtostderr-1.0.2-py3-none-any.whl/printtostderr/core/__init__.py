import argparse
import sys
from typing import *

__all__ = ["main", "printtostderr"]


def main(args: Optional[Iterable] = None) -> None:
    "This function parses the args and hands them to the printtostderr function."
    if args is not None:
        args = [str(x) for x in args]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "args", nargs="*", help="These arguments will be printed to sys.stderr."
    )
    ns = parser.parse_args(args)
    printtostderr(*ns.args)


def printtostderr(*args: Any, **kwargs: Any) -> None:
    "This function prints to sys.stderr."
    print(*args, **kwargs, file=sys.stderr)
