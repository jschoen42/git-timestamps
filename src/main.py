# .venv/Scripts/activate
# python src/main.py

import sys

from pathlib import Path

from utils.globals   import DRIVE #, BASE_PATH
from utils.trace     import Trace
from utils.prefs     import Prefs

from helper.read_data import read_metadata

def main() -> None:
    projects  = Prefs.get("projects")
    ignore_list = Prefs.get("ignore_list")

    for project in projects:
        dest = DRIVE / project["path"] / project["name"]

        if not dest.exists():
            Trace.error(f"Project '{dest}' not found")
            continue

        read_metadata(DRIVE, Path(project["path"]) / project["name"], ignore_list)

if __name__ == "__main__":
    Trace.set( debug_mode=True, timezone=False )
    Trace.action(f"Python version {sys.version}")

    Prefs.init("settings", "")
    Prefs.load("projects.yaml")
    Prefs.load("ignore.yaml")

    try:
        main()
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit()
