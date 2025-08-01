
import os
import shutil
from pathlib import Path
from .rules import default_rules


def organize(folder_path: str, rules: dict = None):
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError(f"❌ {folder_path} is not a valid directory.")

    print("➡ Organizing:", folder_path)

    # Use default rules if none provided
    rules = rules or default_rules

    for file in folder.iterdir():
        if file.is_file():
            destination_folder = classify(file, folder, rules)
            destination_folder.mkdir(exist_ok=True)
            shutil.move(str(file), destination_folder / file.name)

    print("✅ Done organizing.")


def classify(file_path: Path, base_folder: Path, rules: dict) -> Path:
    ext = file_path.suffix.lower().lstrip('.')

    for folder_name, extensions in rules.items():
        if ext in extensions:
            return base_folder / folder_name

    return base_folder / "others"

def delete_empty_folders(base_folder: Path):
    for dirpath, _, _ in os.walk(base_folder, topdown=False):
        path = Path(dirpath)
        if path != base_folder and not any(path.iterdir()):
            try:
                path.rmdir()
                print(f"🗑️ Removed empty folder: {path}")
            except OSError:
                print(f"⚠️ Could not remove: {path}")


def clean(folder_path: str):
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError(f"❌ {folder_path} is not a valid directory.")

    delete_empty_folders(folder)
    print("🧹 Cleaned up empty folders.")
