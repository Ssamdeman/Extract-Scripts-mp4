import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

def get_file_id(file_path: str) -> str:
    """Generates a fast, unique MD5 hash based on the file name and size."""
    path = Path(file_path)
    if not path.exists():
        return ""
    file_stat = path.stat()
    unique_str = f"{path.name}-{file_stat.st_size}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def is_file_processed(history_file: str, source_file: str, file_id: str) -> bool:
    """Checks if a file with the given source_file or file_id already exists in the JSON history."""
    path = Path(history_file)
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                history = json.loads(content)
                for entry in history:
                    if entry.get("source_file") == source_file:
                        return True
                    if entry.get("file_id") == file_id:
                        return True
    except json.JSONDecodeError:
        pass
    return False

def append_to_metrics(history_file: str, source_file: str, file_id: str, metrics: dict):
    """
    Appends the new metrics dict to a JSON array in history_file.
    Creates the file if it doesn't exist.
    """
    path = Path(history_file)
    
    # Structure of the new entry
    entry = {
        "date": datetime.now().isoformat(),
        "source_file": source_file,
        "file_id": file_id,
        "metrics": metrics
    }
    
    history = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    history = json.loads(content)
        except json.JSONDecodeError:
            backup_path = path.with_suffix(".json.bak")
            os.rename(path, backup_path)
            history = []
            print(f"Warning: Could not decode {history_file}. Backed up corrupted file to {backup_path}.")
            
    history.append(entry)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
        
    print(f"Successfully appended metrics to {history_file}")

if __name__ == "__main__":
    # Debug test
    test_file = "test_metrics.json"
    append_to_metrics(test_file, "dummy.mp4", {"dummy_metric": 123})
    print(f"Testing output manager: Wrote dummy metric to {test_file}")
