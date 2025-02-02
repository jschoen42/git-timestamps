import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    stat = file_path.stat()
    return {
        "path": str(file_path.relative_to(file_path.anchor)),
        "name": file_path.name,
        "DateModified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "DateCreated": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "size": stat.st_size
    }

def calculate_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_existing_metadata(metadata_path: Path) -> Dict[str, Any]:
    if metadata_path.exists():
        with metadata_path.open("r") as f:
            return json.load(f)
    return {}

def scan_files(directory: Path, ignore_list: List[str]) -> Dict[str, Tuple[str, bool]]:
    hashes: Dict[str, Tuple[str, bool]] = {}
    for file_path in directory.rglob('*'):
        if file_path.is_file() and not any(ignore in str(file_path) for ignore in ignore_list):
            md5 = calculate_md5(file_path)
            hashes[str(file_path)] = (md5, False)
    return hashes

def update_timestamps(hashes: Dict[str, Tuple[str, bool]], metadata: Dict[str, Any]) -> None:
    for file_path_str, (md5, used) in hashes.items():
        file_path = Path(file_path_str)
        if md5 in metadata:
            file_metadata = metadata[md5]["file"]
            if file_metadata["path"] != str(file_path.relative_to(file_path.anchor)) or file_metadata["name"] != file_path.name:
                file_metadata["path"] = str(file_path.relative_to(file_path.anchor))
                file_metadata["name"] = file_path.name
                metadata[md5]["DateScan"] = datetime.now().isoformat()
            if file_metadata["DateModified"] != datetime.fromtimestamp(file_path.stat().st_mtime).isoformat():
                os.utime(file_path, (file_path.stat().st_atime, datetime.fromisoformat(file_metadata["DateModified"]).timestamp()))
            hashes[file_path_str] = (md5, True)
        else:
            metadata[md5] = {
                "DateScan": datetime.now().isoformat(),
                "file": get_file_metadata(file_path)
            }
            hashes[file_path_str] = (md5, True)

def clean_unused_hashes(hashes: Dict[str, Tuple[str, bool]], metadata: Dict[str, Any]) -> None:
    used_md5s = {md5 for md5, used in hashes.values() if used}
    metadata = {md5: data for md5, data in metadata.items() if md5 in used_md5s}

def save_metadata(metadata: Dict[str, Any], metadata_path: Path) -> None:
    with metadata_path.open("w") as f:
        json.dump(metadata, f, indent=2)

def main() -> None:
    directory = Path("path/to/your/project")
    metadata_path = directory / ".metadata.json"
    ignore_list: List[str] = [".venv", ".type-check-result", ".mypy_cache"]

    existing_metadata = load_existing_metadata(metadata_path)
    file_hashes = scan_files(directory, ignore_list)
    update_timestamps(file_hashes, existing_metadata)
    clean_unused_hashes(file_hashes, existing_metadata)
    save_metadata(existing_metadata, metadata_path)

if __name__ == "__main__":
    main()
