# .venv/Scripts/activate
# python src/main.py

# python src/main.py -r
# python src/main.py -w -s projects.yaml
# python src/main.py -r -s projects_all.yaml

import sys

from pathlib import Path

from utils.globals   import DRIVE
from utils.trace     import Trace
from utils.prefs     import Prefs

from helper.argsparse  import parse_arguments
from helper.timestamps import read_metadata, write_metadata

def main( write: bool = False ) -> None:
    projects  = Prefs.get("projects")
    ignore_list = Prefs.get("ignore_list")

    for project in projects:
        dest = DRIVE / project["path"] / project["name"]

        if not dest.exists():
            Trace.error(f"Project '{dest}' not found")
            continue

        if write:
            write_metadata(DRIVE, Path(project["path"]) / project["name"], verbose=True)
        else:
            read_metadata(DRIVE, Path(project["path"]) / project["name"], ignore_list, reset=True)

if __name__ == "__main__":
    Trace.set( debug_mode=True, timezone=False )
    Trace.action(f"Python version {sys.version}")

    setting = "projects_all.yaml"    # projects_all.yaml projects.yaml
    args = parse_arguments(setting)

    Prefs.init("settings", "")
    if not Prefs.load(args["setting"]):
        Trace.fatal( f"setting '/settings/{args["setting"]}' not exist" )
    Prefs.load("ignore.yaml")

    try:
        main( args["write"] )
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit()
