# .venv/Scripts/activate
# python src/main.py

import sys

from typing import Dict, List
from pathlib import Path

from utils.globals   import DRIVE, BASE_PATH
from utils.trace     import Trace
from utils.prefs     import Prefs

from read_data import read_metadata

def main() -> None:
    projects  = Prefs.get("projects")
    ignore_list = Prefs.get("ignore_list")

    for project in projects:
        dest = DRIVE / project["path"] / project["name"]

        if not dest.exists():
            Trace.error(f"Project '{dest}' not found")
            continue

        # Trace.action( f"Project '{project['name']}'" )
        read_metadata(DRIVE, Path(project["path"]) / project["name"], ignore_list)

if __name__ == "__main__":
    Trace.set( debug_mode=True, timezone=False )
    Trace.action(f"Python version {sys.version}")
    Trace.action(f"BASE_PATH: '{BASE_PATH.resolve()}'")

    Prefs.init("settings", "")
    Prefs.load("projects.yaml")
    Prefs.load("ignore.yaml")
    try:
        main()
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit()