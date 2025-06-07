"""Utility functions for logging and timestamp generation."""

import json
from datetime import datetime
from typing import Dict, Any


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


class JsonLogger:
    """Logger that appends JSON records with timestamps to a JSONL file."""
    
    def __init__(self, path: str) -> None:
        """Initialize the JsonLogger with the target file path.
        
        Args:
            path: Path to the JSONL file to write to
        """
        self.path = path
    
    def log(self, record: Dict[str, Any]) -> None:
        """Log a record with timestamp to the JSONL file.
        
        Args:
            record: Dictionary containing the data to log
        """
        timestamped_record = {"timestamp": now_iso(), **record}
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(timestamped_record) + "\n") 