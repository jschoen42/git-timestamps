"""
    © Jürgen Schoenemeyer, 03.02.2025

    PUBLIC:
     - path: Path, exclude: Dict[str, Any] = {"folder": None, "files": None}, show_result: bool = True ) -> Tuple[List[str], List[str], List[str]]
     - get_filepaths_ancor( ancor_path: Path, exclude: Dict[str, Any] = {"folder": None, "files": None}, show_result: bool = True ) -> Tuple[List[str], List[str], List[str]]
        - ancor path: relative/absolute path
        - folder, files, error paths: relative to ancor_path

    PRIVAT:
     - match_not_exclude( name: str, excludes: None | Dict[str, str] ) -> bool
"""
import fnmatch

from typing import Any, Dict, List, Tuple
from pathlib import Path

from utils.trace     import Trace
from utils.decorator import duration

# exclude = {
#     "folder": [".git", ".venv", "__pycache__", "__MACOSX"],
#     "files": ["desktop.ini", "folderico*.ico"]
# }

def match_not_exclude( name: str, excludes: None | Dict[str, str] ) -> bool:
    if excludes is None:
        return True

    for exclude in excludes:
        if fnmatch.fnmatch(name, exclude):
            return False

    return True

@duration("{__name__} '{0}'")
def get_filepaths_all(
    path: Path,
    exclude: Dict[str, Any] = {"folder": None, "files": None},
    show_result: bool = True
) -> Tuple[List[str], List[str], List[str]]:

    Trace.action(f"path '{path}'")

    files:   List[str] = []
    folders: List[str] = []
    errors:  List[str] = []

    def get_filepaths( path: Path ) -> None:
        try:
            for entry in path.iterdir():
                if entry.is_file():
                    if match_not_exclude(entry.name, exclude["files"]):
                        files.append( entry.as_posix() )
                elif entry.is_dir():
                    if match_not_exclude(entry.name, exclude["folder"]):
                        folders.append( path.as_posix() )
                        get_filepaths( entry )

        except PermissionError as err:
            errors.append( path.as_posix() )
            Trace.error( f"{err}" )

        except NotADirectoryError as err: # symlink
            errors.append( path.as_posix() )
            Trace.error( f"{err}" )

    get_filepaths( path )

    if len(errors)>0:
        Trace.error(f"errors: {errors}")

    if show_result:
        Trace.result(f"folders: {len(folders)}, files: {len(files)}, errors: {len(errors)} - exclude: {exclude}")

    return files, folders, errors

# @duration("{__name__} '{0}'")
def get_filepaths_ancor(
    ancor_path: Path,
    exclude: Dict[str, Any] = {"folder": None, "files": None},
    show_result: bool = True
) -> Tuple[List[str], List[str], List[str]]:

    files:   List[str] = []
    folders: List[str] = []
    errors:  List[str] = []

    def get_filepaths( rel_path: str ) -> None:
        curr_path = ancor_path / rel_path
        try:
            for entry in Path(curr_path).iterdir():
                if rel_path == "":
                    name = entry.name
                else:
                    name = rel_path + "/" + entry.name # as posix

                if entry.is_file():
                    if match_not_exclude(entry.name, exclude["files"]):
                        files.append( name )
                elif entry.is_dir():
                    if match_not_exclude(entry.name, exclude["folder"]):
                        folders.append( name )
                        get_filepaths( name )

        except PermissionError as err:
            errors.append( Path(curr_path).as_posix() )
            Trace.error( f"{err}" )

        except NotADirectoryError as err: # symlink
            errors.append( Path(curr_path).as_posix() )
            Trace.error( f"{err}" )

    get_filepaths("")

    if len(errors)>0:
        Trace.error(f"errors: {errors}")

    if show_result:
        Trace.result(f"folders: {len(folders)}, files: {len(files)}, errors: {len(errors)} - exclude: {exclude}")

    return files, folders, errors
