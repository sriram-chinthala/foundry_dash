# foundry_dash/core/logic/universe_helpers.py (Complete Code)

import copy # Required for deepcopy
from typing import Dict, List, Set, Tuple
import pandas as pd

def get_available_stocks(current_stocks: List[str], all_tickers: List[str]) -> List[str]:
    """Calculates which stocks can be added (available minus current)."""
    current_stocks_set = set(current_stocks)
    available_stocks = [s for s in all_tickers if s not in current_stocks_set]
    return sorted(available_stocks)

def apply_universe_changes(
    current_universes: Dict[str, List[str]],
    selected_universe: str,
    stocks_to_add: List[str],
    stocks_to_remove: List[str],
    manual_stocks_text: str
) -> Dict[str, List[str]]:
    """Applies additions and removals to the selected universe and returns the updated dict."""
    
    if not selected_universe or selected_universe not in current_universes:
        return current_universes
    
    # CRITICAL FIX: Use deepcopy to prevent state mutation in other universes (Bug 2)
    new_universes = copy.deepcopy(current_universes) 
    
    # Work on a set for efficient manipulation
    current_stocks = set(new_universes.get(selected_universe, []))
    
    # 1. Additions from Checkboxes
    current_stocks.update(set(s for s in stocks_to_add if s))

    # 2. Additions from Manual Entry
    if manual_stocks_text:
        manual_additions = {s.strip().upper() for s in manual_stocks_text.splitlines() if s.strip()}
        current_stocks.update(manual_additions)
        
    # 3. Removals
    stocks_to_remove_set = set(s for s in stocks_to_remove if s)
    current_stocks.difference_update(stocks_to_remove_set)
    
    # Update the specific universe list
    new_universes[selected_universe] = sorted(list(current_stocks))
    
    return new_universes

def create_table_data(stocks: List[str]) -> List[Dict[str, str]]:
    """Converts a list of stocks into the format Dash DataTable expects."""
    # NOTE: This function is required and was previously missing from imports.
    return [{"tickers": s} for s in stocks]

# --- Placeholder function for V2.0 Stock Details (Pricing, etc.) ---
def get_stock_details_df(stocks: List[str]) -> pd.DataFrame:
    """Mocks fetching real-time data for the current universe stocks."""
    if not stocks:
        return pd.DataFrame()
        
    # Mock data for demonstration and new layout
    data = []
    for i, ticker in enumerate(stocks):
        data.append({
            "Ticker": ticker,
            "Price (INR)": round(1500 + i * 10.5, 2),
            "Change (%)": round((-0.5 + (i % 5) / 4) * 1.5, 2),
            "RS Ranking": (i % 99) + 1,
            "Signal": ["HOLD", "TRIGGERED_BUY", "WATCHLIST", "EXTENDED"][i % 4]
        })
        
    return pd.DataFrame(data)