import json
from typing import Union, List, Dict, Any

### Utility functions for JSON handling ###
def load_json_file(filepath: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Load JSON file and return data structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f'Invalid JSON: {e}')
        return []
    except FileNotFoundError:
        print(f'File not found: {filepath}')
        return []

def is_json_array(data) -> bool:
    """Check if loaded data is a list/array."""
    return isinstance(data, list)
