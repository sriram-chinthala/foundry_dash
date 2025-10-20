# foundry_dash/callbacks/universe_manager_cbs.py (FINAL COMPLETE FIX)

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
import time
import copy
import pandas as pd 

# --- Import Core Logic ---
from core.io.data_persistence import save_universes, load_universes, get_all_known_tickers
from core.logic.universe_helpers import apply_universe_changes, create_table_data, get_available_stocks, get_stock_details_df # Added get_stock_details_df

# --- Mock UI Imports (Needed for the code to compile) ---
# NOTE: This assumes you have access to dash_table
# -----------------------------------------------------------------

# 1. INITIAL LOAD: (Code is correct)
@dash.callback(
    Output('universe-data-store', 'data'),
    Input('selected-universe-name-store', 'data') 
)
def load_initial_data(_):
    try:
        universes_path = Path('./data/universes.yaml') 
        universes = load_universes(universes_path)
        return universes
    except Exception as e:
        print(f"Error initializing data: {e}")
        return {"Nifty 50": []} 

# 2. PERSISTENCE TRIGGER: (Code is correct)
@dash.callback(
    Output('status-output', 'children'),
    Input('save-trigger-store', 'data'),
    State('universe-data-store', 'data'),
    prevent_initial_call=True
)
def trigger_persistence_save(save_trigger_count, universe_data):
    if save_trigger_count == 0:
        raise PreventUpdate

    universes_path = Path('./data/universes.yaml') 
    save_universes(universes_path, universe_data)
    return f"✅ Changes saved and persisted at {time.strftime('%H:%M:%S')}"


# 3. DROPDOWN OPTIONS: (Code is correct)
@dash.callback(
    Output('universe-dropdown', 'options'),
    Output('selected-universe-name-store', 'data', allow_duplicate=True),
    Input('universe-data-store', 'data'),
    State('selected-universe-name-store', 'data'),
    prevent_initial_call=True
)
def update_dropdown_options(universe_data, selected_name):
    if not universe_data:
        raise PreventUpdate

    names = sorted(list(universe_data.keys()))
    new_selected_name = selected_name if selected_name in names else (names[0] if names else "")

    return names, new_selected_name

# 4. EDITOR UPDATE: (CRITICAL FIXES APPLIED)
@dash.callback(
    Output('editing-title', 'children'),                                  # 1
    Output('table-count', 'children'),                                    # 2
    Output('stocks-to-add-dropdown', 'options'),                          # 3
    Output('stocks-to-remove-dropdown', 'options'),                       # 4
    Output('stocks-to-add-dropdown', 'value', allow_duplicate=True),      # 5 (Reset)
    Output('stocks-to-remove-dropdown', 'value', allow_duplicate=True),   # 6 (Reset)
    Output('selected-universe-name-store', 'data', allow_duplicate=True), # 7 (Maintain selection)
    Output('stock-viewer-area', 'children'),                              # 8 (The new professional table content)
    
    Input('selected-universe-name-store', 'data'),
    Input('universe-data-store', 'data'),
    State('global-known-tickers-store', 'data'),
    prevent_initial_call=True # Must be True due to allow_duplicate
)
def update_editor_content(selected_name, universe_data, all_known_tickers):
# CRITICAL: Initialize variables that are complex outputs to safe defaults
    current_stocks = []
    
    # 1. Immediate exit if inputs are not ready
    if selected_name is None or universe_data is None:
        raise PreventUpdate
    
    # 2. Define current_stocks
    current_stocks = universe_data.get(selected_name, [])
    
    # 3. Execution flow continues safely:
    stock_details_df = get_stock_details_df(current_stocks) # NOW SAFE
    
    # Check if a non-DataFrame object is returned due to empty current_stocks
    if stock_details_df.empty: 
        viewer_table_data = []
    else:
        viewer_table_data = stock_details_df.to_dict('records')
    
    # 2. Build the new professional DataTable component
    viewer_table = dash_table.DataTable(
        id='current-universe-viewer-table', 
        columns=[{"name": col, "id": col} for col in stock_details_df.columns],
        data=viewer_table_data,
        page_action='native',
        page_size=12,
        sort_action='native',
        style_header={'backgroundColor': 'var(--bs-gray-200)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'column_id': 'Change (%)', 'filter_query': '{Change (%)} > 0.0'}, 'color': 'green'},
            {'if': {'column_id': 'Change (%)', 'filter_query': '{Change (%)} < 0.0'}, 'color': 'red'},
        ],
        
    )

    # 3. Update Add/Remove Dropdowns
    available_to_add = get_available_stocks(current_stocks, all_known_tickers)
    remove_options = current_stocks
    
    return (
        f"Editing: {selected_name}",      # 1
        f"Stocks in Universe: {len(current_stocks)}", # 2
        available_to_add,                 # 3
        remove_options,                   # 4
        None,                             # 5
        None,                             # 6
        selected_name,                    # 7
        viewer_table                      # 8
    )


# 5. CREATE UNIVERSE: (Code is correct)
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('new-universe-name-input', 'value'),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Input('create-universe-button', 'n_clicks'),
    State('new-universe-name-input', 'value'),
    State('universe-data-store', 'data'),
    prevent_initial_call=True
)
def create_new_universe(n_clicks, new_name, universe_data):
    if not n_clicks or n_clicks == 0 or not new_name or new_name in universe_data:
        raise PreventUpdate
        
    updated_universes = copy.deepcopy(universe_data) # Use deepcopy for creation
    updated_universes[new_name] = []
    
    return updated_universes, "", n_clicks


# 6. DELETE UNIVERSE: (Final Fixes Applied)
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Output('universe-dropdown', 'value', allow_duplicate=True),
    Output('delete-confirmation-modal', 'is_open', allow_duplicate=True),

    Input('confirm-delete-button', 'n_clicks'), 
    State('selected-universe-name-store', 'data'),
    State('universe-data-store', 'data'),
    prevent_initial_call=True
)
def delete_universe_confirmed(n_clicks, selected_name, universe_data):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    if selected_name in universe_data:
        updated_universes = copy.deepcopy(universe_data) # CRITICAL FIX: Use deepcopy here
        del updated_universes[selected_name] 
        
        names = sorted(list(updated_universes.keys()))
        new_default_name = names[0] if names else ""
    
        return updated_universes, n_clicks, new_default_name, False 
        
    return dash.no_update, dash.no_update, dash.no_update, False

# 7. SAVE CHANGES: (Code is correct)
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Output('stocks-to-add-dropdown', 'value', allow_duplicate=True),
    Output('stocks-to-remove-dropdown', 'value', allow_duplicate=True),
    Output('manual-stocks-textarea', 'value'), 
    
    Input('save-changes-button', 'n_clicks'),
    State('selected-universe-name-store', 'data'),
    State('universe-data-store', 'data'),
    State('stocks-to-add-dropdown', 'value'),
    State('stocks-to-remove-dropdown', 'value'),
    State('manual-stocks-textarea', 'value'),
    
    prevent_initial_call=True
)
def save_universe_changes(n_clicks, selected_name, universe_data, stocks_to_add, stocks_to_remove, manual_stocks_text):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    stocks_to_add = stocks_to_add if stocks_to_add else []
    stocks_to_remove = stocks_to_remove if stocks_to_remove else []
    
    updated_universes = apply_universe_changes(
        current_universes=universe_data,
        selected_universe=selected_name,
        stocks_to_add=stocks_to_add,
        stocks_to_remove=stocks_to_remove,
        manual_stocks_text=manual_stocks_text if manual_stocks_text else ""
    )
    
    new_trigger_count = n_clicks
    
    return updated_universes, new_trigger_count, None, None, ""

# 8. MODAL CONTROL: (Code is correct)
@dash.callback(
    Output("delete-confirmation-modal", "is_open"),
    Output("delete-modal-body", "children"),
    Input("open-delete-modal-button", "n_clicks"),
    Input("cancel-delete-button", "n_clicks"),
    State("delete-confirmation-modal", "is_open"),
    State("selected-universe-name-store", "data"),
)
def toggle_delete_modal(open_clicks, cancel_clicks, is_open, selected_name):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "open-delete-modal-button":
        body_text = f"Are you sure you want to delete the '{selected_name}' universe? This cannot be undone."
        return True, body_text
    
    if trigger_id == "cancel-delete-button":
        return False, dash.no_update
    
    return is_open, dash.no_update