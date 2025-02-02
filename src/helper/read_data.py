import os
import hashlib

from typing import Any, Dict, List, Tuple
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone

from utils.trace import Trace
# from utils.decorator import duration

from utils.util import export_json, import_json

from helper.rekursion import get_filepaths_ancor

def format_time( time: float ) -> str:
    datetime_object = datetime.fromtimestamp(time, tz=timezone.utc).astimezone(tz=None)
    return datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f%z")

def scan_time( timestamp: str ) -> float:
    datetime_object = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    return datetime_object.timestamp()

"""
    https://learn.microsoft.com/en-gb/windows/win32/fileio/file-attribute-constants?redirectedfrom=MSDN
"""
def get_file_arributes( path: Path ) -> str:
    attributes = os.stat(path).st_file_attributes

    ret = ""
    if attributes & 0x00000001: # Read-only
        ret += "R"
    if attributes & 0x00000002: # Hidden
        ret += "H"
    if attributes & 0x00000004: # System
        ret += "S"
    if attributes & 0x00000010: # Directory
        ret += "D"
    if attributes & 0x00000020: # Archive
        ret += "A"
    if attributes & 0x00001000: # Offline
        ret += "O"
    if attributes & 0x00002000: # Indexable
        ret += "I"
    if attributes & 0x00080000: # Pinned
        ret += "P"

    return ret

def get_file_metadata(file_path: Path, project_path: Path) -> Tuple[str, Dict[str, str | int]]:

    # file_path:    "G:\Python\_empty\.gitignore"
    # project_path: "\Python\_empty"
    #
    # rel_path:     ""
    # name:         ".gitignore"

    # file_path:    "G:\Python\_empty\src\utils\util.py"
    # project_path: "\Python\_empty"
    #
    # rel_path:     "/src/utils"
    # name:         "util.py"

    p1 = str(PurePosixPath(file_path).parent)
    p2 = str(PurePosixPath(project_path))
    rel_path = p1.split(p2)[-1]

    if rel_path == "":
        key = file_path.name
    else:
        key = rel_path + "/" + file_path.name

    return (
        key,
        {
            "md5":  calculate_md5(file_path),
            "path": rel_path,
            "name": file_path.name,
            "size": os.stat(file_path).st_size,
            "attr": get_file_arributes(file_path),
            "modified": format_time(os.path.getmtime(file_path)),

            # "created": format_time(os.path.getctime(file_path)),
            # "access": format_time(os.path.getatime(file_path)),
        }
    )

def calculate_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def scan_files(drive: Path, project_path: Path, files: List[str]) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    for file in files:
        file_path = drive / project_path / file

        key, data = get_file_metadata(Path(file_path), project_path)
        metadata[key] = data

    return metadata

def update_metadata(existing_metadata: Dict[str, Any], new_metadata: Dict[str, Any]) -> Dict[str, Any]:
    updated = {}

    for key, data in new_metadata.items():
        if key in existing_metadata:
            if existing_metadata[key]["md5"] == data["md5"]:
                updated[key] = existing_metadata[key]
            else:
                updated[key] = data
        else:
            updated[key] = data

    return updated

# @duration("{__name__} '{project_path}'")
def read_metadata(drive_path: Path, project_path: Path, ignore_list: Dict[str, List[str]]) -> None:

    files, _folders, _errors = get_filepaths_ancor( drive_path / project_path, exclude=ignore_list, show_result=False )
    metadata = scan_files(drive_path, project_path, files)

    old_data = import_json( project_path, ".timestamps.json", show_error = False )
    if old_data is not None:
        metadata = update_metadata( old_data["metadata"], metadata )

    filedata = {
        "scan": {
            "date": datetime.now().isoformat(),
            "path": (drive_path / project_path).as_posix(),
            "files": len(files),
            "ignore": ignore_list,
        },
        "metadata": metadata
    }

    export_json( project_path, ".timestamps.json", filedata, show_message=False )
    Trace.result( f"'{project_path}' {len(files)} files" )
