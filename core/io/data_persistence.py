# foundry_dash/core/io/data_persistence.py

from pathlib import Path
from typing import Dict, List, Any
import yaml
import pandas as pd

# Assume the actual file operations (yaml.safe_load, etc.) are wrapped 
# in a separate data_io utility module that is accessible here.
# We will mock the wrapper calls for this example.

def load_universes(path: Path) -> Dict[str, List[str]]:
    """Loads stock universes from the YAML file."""
    if not path.exists():
        # IMPORTANT: Return a valid structure with a default universe if file is missing
        return {"Nifty 50": []}
    
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            # Ensure the structure is a dict, even if the file is empty
            return data if isinstance(data, dict) else {"Nifty 50": []}
    except Exception as e:
        print(f"Error loading universes from {path}: {e}")
        return {"Nifty 50": []}

def save_universes(path: Path, data: Dict[str, List[str]]):
    """Saves the current stock universes dictionary to the YAML file."""
    try:
        # Ensure the parent directory exists before writing
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)
        print(f"[I/O] Universes saved to disk successfully at {path}")
    except Exception as e:
        print(f"[I/O ERROR] Could not save universes to {path}: {e}")

# --- Utility to get Tickers (Replaces DataManagementState's all_known_tickers logic) ---
def get_all_known_tickers() -> List[str]:
    """Returns a placeholder list of all known tickers."""
    # CRITICAL: Returning a simple list of strings ensures serialization works.
    return [
        "NSE:RELIANCE-EQ", "BSE:TCS-EQ", "NSE:INFY-EQ", "NSE:HDFCBANK", 
        "ADANIENT", "ASIANPAINT", "ICICIBANK", "KOTAKBANK", "MARUTI",
        "WIPRO", "TECHM", "TITAN", "ULTRACEMCO", "HEROMOTOCO", "EICHERMOT",
        "TCS", "SBIN", "BHARTIARTL" # Added more to guarantee options
    ]