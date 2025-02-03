"""
    © Jürgen Schoenemeyer, 03.02.2025

    src/helper/argsparse.py

    PUBLIC:
     - parse_arguments() -> Dict[str, Any]
"""

# https://docs.python.org/3.12/howto/argparse.html#argparse-tutorial

import sys
from typing import Any, Dict
from argparse import ArgumentParser, Namespace

# from utils.trace import Trace

def parse_arguments(default_settings) -> Dict[str, Any]:
    parser = ArgumentParser(description="save/restore file timestamps")
    parser.add_argument("-w", "--write", action="store_true", help="Write timestamps")
    parser.add_argument("-r", "--read", action="store_true", help="Read timestamps")
    parser.add_argument("-s", "--settings", type=str, help="Settings file (e.g., projects.yaml)")

    args: Namespace = parser.parse_args()

    if args.write and args.read:
        parser.print_help()
        sys.exit(2)

    if args.write:
        write = True
    else:
        write = False

    if args.settings is None:
        setting = default_settings
    else:
        setting = args.settings

    return {
        "write":   write,
        "setting": setting,
    }
