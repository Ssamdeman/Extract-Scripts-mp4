import json
import os
from datetime import datetime
from pathlib import Path

def append_to_metrics(history_file: str, source_file: str, metrics: dict):
    """
    Appends the new metrics dict to a JSON array in history_file.
    Creates the file if it doesn't exist.
    """
    path = Path(history_file)
    
    # Structure of the new entry
    entry = {
        "date": datetime.now().isoformat(),
        "source_file": source_file,
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
