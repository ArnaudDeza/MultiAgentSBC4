"""
Utility functions for multi-agent debate system.
"""

import json
from datetime import datetime
from typing import Dict, Any


def now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.utcnow().isoformat()


class JsonLogger:
    """Simple JSONL logger that appends records with timestamps."""
    
    def __init__(self, path: str) -> None:
        """Initialize logger with output file path."""
        self.path = path
        
    def log(self, record: Dict[str, Any]) -> None:
        """
        Append a record to the JSONL file with timestamp.
        
        Args:
            record: Dictionary to log
        """
        timestamped_record = {
            "timestamp": now_iso(),
            **record
        }
        
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(timestamped_record) + '\n') 