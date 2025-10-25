# foundry_dash/callbacks/universe_cbs.py (FINAL FIX)

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
import time
import copy
import pandas as pd 
import dash_bootstrap_components as dbc

# --- CORE LOGIC IMPORTS ---
from core.io.data_persistence import save_universes, load_universes, get_all_known_tickers
from core.logic.universe_helpers import apply_universe_changes, get_available_stocks, get_stock_details_df

# --- MODULAR UI IMPORTS (Used to render the content for each tab) ---
from components.universe_manager_ui import layout as universe_manager_layout
from components.strategy_builder_ui import layout as strategy_builder_layout
from components.performance_engine_ui import layout as performance_engine_layout
from components.research_library_ui import layout as research_library_layout


# ============================================================================
# CALLBACK 1: Render Tab Content (Final Structure Rework)
# ============================================================================
@dash.callback(
    Output('tabs-content', 'children'),
    Output('research-hub-active-flag', 'data'),
    Input('research-hub-tabs', 'value'),
    Input('url', 'pathname'),
    prevent_initial_call=False  
)
def render_tab_content_modular(active_tab, pathname):
    """Renders the content for the active tab and sets the system-wide active flag."""
    
    # 1. PAGE-LEVEL GATE (OFF Signal)
    if pathname != '/research-hub':
        # Must return *empty* content and the OFF signal (False)
        return html.Div(), False 

    # 2. TAB-LEVEL CONTENT RENDER
    content = html.Div() # Initialize a fallback content container

    if active_tab == 'universe-manager-tab':
        content = universe_manager_layout() # <-- CRITICAL: Must be called here!
    elif active_tab == 'strategy-builder-tab':
        content = strategy_builder_layout()
    elif active_tab == 'performance-engine-tab':
        content = performance_engine_layout()
    elif active_tab == 'research-library-tab':
        content = research_library_layout()
    else:
        content = html.Div("Error: Unknown Tab Selected", className='alert alert-danger mt-3')
        
    # 3. Signal ON: Only when the correct content is rendered
    return content, True

# ============================================================================
# CALLBACK 1b (NEW): Control Wrapper Visibility (THE GLOBAL GATE)
# ============================================================================
@dash.callback(
    Output('universe-manager-content-wrapper', 'style'),
    Input('research-hub-tabs', 'value'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def toggle_universe_manager_visibility(active_tab, pathname):
    """The only component that determines if the Universe Manager's IDs are active."""
    
    # Check 1: Is the user on the correct page?
    if pathname != '/research-hub':
        return {'display': 'none'}

    # Check 2: Is the user on the correct tab?
    if active_tab == 'universe-manager-tab':
        # Signal ON: The component is now visible and its internal callbacks can fire.
        return {'display': 'block'}
    else:
        # Signal OFF: The component is present but hidden, effectively preventing
        # its internal callbacks (3-10) from firing while inactive.
        return {'display': 'none'}
    
# ============================================================================
# CALLBACK 2 (REMOVED/ABSORBED): No longer a separate callback. The data 
# loading logic is executed in 01_research_hub.py's initialization phase.
# The `universe-data-store` is initialized directly from disk and is static.
# ============================================================================

# ============================================================================
# CALLBACK 3: Persistence Trigger (Saves the state to disk)
# ============================================================================
@dash.callback(
    Output('status-output', 'children'),
    Input('save-trigger-store', 'data'),
    State('universe-data-store', 'data'),
    State('research-hub-active-flag', 'data'), # <--- NEW ACTIVE FLAG STATE
    prevent_initial_call=True
)
def trigger_persistence_save(save_trigger_count, universe_data, is_active): # <--- NEW ARGUMENT
    if not is_active: # <-- CHECK THE MASTER SWITCH
        raise PreventUpdate
        
    if save_trigger_count == 0:
        raise PreventUpdate

    universes_path = Path('./data/universes.yaml') 
    save_universes(universes_path, universe_data)
    return f"✅ Changes saved and persisted at {time.strftime('%H:%M:%S')}"


# ============================================================================
# CALLBACK 4 (REWORKED): Update Dropdown Options with delayed trigger.
# This callback is the main source of the error and MUST be refactored.
# ============================================================================
@dash.callback(
    Output('universe-dropdown', 'options'),
    Output('universe-dropdown', 'value'),
    # Note: Outputting to selected-universe-name-store here causes a chain reaction
    # We will output it only from the dropdown input for synchronization.
    
    Input('research-hub-load-trigger', 'data'), # <--- NEW: ONLY fires when the page is loaded
    Input('research-hub-tabs', 'value'), 
    State('universe-data-store', 'data'),
    State('research-hub-active-flag', 'data'),
    State('selected-universe-name-store', 'data'),
    prevent_initial_call=True # <--- KEEP TRUE: Only run on trigger
)
def update_dropdown_options_delayed(load_trigger, active_tab, universe_data, is_active, selected_name): 
    # Must use the Active Flag and Tab Gate
    if not is_active or active_tab != 'universe-manager-tab':
        raise PreventUpdate

    if load_trigger is None: # Initial load will trigger the content, but this ensures no double fire
        raise PreventUpdate
    
    # ... (Rest of logic from old Callback 4 remains the same) ...
    names = sorted(list(universe_data.keys()))
    new_selected_name = selected_name if selected_name in names else (names[0] if names else None)

    options = [{'label': n, 'value': n} for n in names]
    # Removed output for selected-universe-name-store to avoid unnecessary triggers
    return options, new_selected_name 

# ============================================================================
# CALLBACK 5: Sync Dropdown to Store (MODIFIED)
# ============================================================================
# This callback must now handle the `selected-universe-name-store` update 
# which was previously also in Callback 4.
@dash.callback(
    Output('selected-universe-name-store', 'data', allow_duplicate=True),
    Input('universe-dropdown', 'value'),
    State('research-hub-active-flag', 'data'),
    prevent_initial_call=True
)
def sync_dropdown_to_store(dropdown_value, is_active):
    if not is_active:
        raise PreventUpdate

    if dropdown_value is None:
        raise PreventUpdate
    return dropdown_value

# ============================================================================
# CALLBACK 6a: Update Editor UI (Title and Dropdown Options)
# ============================================================================
@dash.callback(
    Output('editing-title', 'children'),
    Output('stocks-to-add-dropdown', 'options'),
    Output('stocks-to-remove-dropdown', 'options'),
    Output('stocks-to-add-dropdown', 'value', allow_duplicate=True),
    Output('stocks-to-remove-dropdown', 'value', allow_duplicate=True),
    
    Input('research-hub-tabs', 'value'),            
    Input('selected-universe-name-store', 'data'),  
    Input('universe-data-store', 'data'),   
    Input('url', 'pathname'), # <--- CORRECTLY ADDED INPUT        
    State('global-known-tickers-store', 'data'),
    prevent_initial_call=True
)
def update_editor_ui_options(active_tab, selected_name, universe_data, pathname, all_known_tickers):
    if pathname != '/research-hub':
        raise PreventUpdate
        
    if active_tab != 'universe-manager-tab':
        raise PreventUpdate

    if selected_name is None or universe_data is None:
        raise PreventUpdate
    
    current_stocks = universe_data.get(selected_name, [])
    available_to_add = get_available_stocks(current_stocks, all_known_tickers)
    remove_options = current_stocks
    
    return (
        f"Editing: {selected_name}",
        available_to_add,
        remove_options,
        [],  # Reset add dropdown
        [],  # Reset remove dropdown
    )


# ============================================================================
# CALLBACK 6b: Isolated Stock Viewer Table Update (Data Processing)
# ============================================================================
@dash.callback(
    Output('table-count', 'children'),
    Output('stock-viewer-area', 'children'),
    Input('selected-universe-name-store', 'data'), 
    Input('universe-data-store', 'data'),
    Input('research-hub-tabs', 'value'),           
    Input('url', 'pathname'), # <--- CORRECTLY ADDED INPUT
    prevent_initial_call=True
)
def update_stock_viewer_table(selected_name, universe_data, active_tab, pathname):
    if pathname != '/research-hub':
        raise PreventUpdate
        
    if active_tab != 'universe-manager-tab':
        raise PreventUpdate

    if selected_name is None or universe_data is None:
        raise PreventUpdate

    current_stocks = universe_data.get(selected_name, [])
    stock_details_df = get_stock_details_df(current_stocks)
    
    if stock_details_df.empty: 
        viewer_table_data = []
    else:
        viewer_table_data = stock_details_df.to_dict('records')
    
    viewer_table = dash_table.DataTable(
        id='current-universe-viewer-table', 
        columns=[{"name": col, "id": col} for col in stock_details_df.columns],
        data=viewer_table_data,# type: ignore
        page_action='native',
        page_size=12,
        sort_action='native',
        style_header={'backgroundColor': 'var(--bs-gray-200)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'column_id': 'Change (%)', 'filter_query': '{Change (%)} > 0.0'}, 'color': 'green'},
            {'if': {'column_id': 'Change (%)', 'filter_query': '{Change (%)} < 0.0'}, 'color': 'red'},
        ],# type: ignore
    )
    
    return (
        f"Stocks in Universe: {len(current_stocks)}",
        viewer_table
    )


# ============================================================================
# CALLBACK 7: Create Universe
# ============================================================================
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('new-universe-name-input', 'value'),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Input('create-universe-button', 'n_clicks'),
    Input('url', 'pathname'), # <--- CRITICAL FIX: ADDED INPUT
    State('new-universe-name-input', 'value'),
    State('universe-data-store', 'data'),
    State('research-hub-tabs', 'value'), 
    prevent_initial_call=True
)
def create_new_universe(n_clicks, pathname, new_name, universe_data, active_tab): # <--- CRITICAL FIX: ADDED ARGUMENT
    if pathname != '/research-hub':
        raise PreventUpdate # <-- NEW GLOBAL GATE CHECK

    if active_tab != 'universe-manager-tab':
        raise PreventUpdate
        
    if not n_clicks or not new_name or new_name in universe_data:
        raise PreventUpdate
        
    updated_universes = copy.deepcopy(universe_data)
    updated_universes[new_name] = []
    
    return updated_universes, "", n_clicks


# ============================================================================
# CALLBACK 8: Save Changes
# ============================================================================
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Output('stocks-to-add-dropdown', 'value', allow_duplicate=True),
    Output('stocks-to-remove-dropdown', 'value', allow_duplicate=True),
    Output('manual-stocks-textarea', 'value'), 
    
    Input('save-changes-button', 'n_clicks'),
    Input('url', 'pathname'), # <--- CRITICAL FIX: ADDED INPUT
    State('selected-universe-name-store', 'data'),
    State('universe-data-store', 'data'),
    State('stocks-to-add-dropdown', 'value'),
    State('stocks-to-remove-dropdown', 'value'),
    State('manual-stocks-textarea', 'value'),
    State('research-hub-tabs', 'value'), 
    prevent_initial_call=True
)
def save_universe_changes(n_clicks, pathname, selected_name, universe_data, stocks_to_add, stocks_to_remove, manual_stocks_text, active_tab): # <--- CRITICAL FIX: ADDED ARGUMENT
    if pathname != '/research-hub':
        raise PreventUpdate # <-- NEW GLOBAL GATE CHECK
        
    if active_tab != 'universe-manager-tab':
        raise PreventUpdate

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
    
    return updated_universes, n_clicks, [], [], ""


# ============================================================================
# CALLBACK 9: Modal Control (Open/Close)
# ============================================================================
@dash.callback(
    Output("delete-confirmation-modal", "is_open", allow_duplicate=True),
    Output("delete-modal-body", "children"),
    Input("open-delete-modal-button", "n_clicks"),
    Input("cancel-delete-button", "n_clicks"),
    Input('url', 'pathname'), # <--- CRITICAL FIX: ADDED INPUT
    State("delete-confirmation-modal", "is_open"),
    State("selected-universe-name-store", "data"),
    State('research-hub-tabs', 'value'), 
    prevent_initial_call=True
)
def toggle_delete_modal(open_clicks, cancel_clicks, pathname, is_open, selected_name, active_tab): # <--- CRITICAL FIX: ADDED ARGUMENT
    if pathname != '/research-hub':
        raise PreventUpdate # <-- NEW GLOBAL GATE CHECK
        
    if active_tab != 'universe-manager-tab':
        raise PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "open-delete-modal-button" and open_clicks:
        body_text = f"Are you sure you want to delete the '{selected_name}' universe? This cannot be undone."
        return True, body_text
    
    if trigger_id == "cancel-delete-button" and cancel_clicks:
        return False, dash.no_update
    
    raise PreventUpdate


# ============================================================================
# CALLBACK 10: Delete Universe (Confirmed Action)
# ============================================================================
@dash.callback(
    Output('universe-data-store', 'data', allow_duplicate=True),
    Output('save-trigger-store', 'data', allow_duplicate=True),
    Output('delete-confirmation-modal', 'is_open', allow_duplicate=True),

    Input('confirm-delete-button', 'n_clicks'), 
    Input('url', 'pathname'), # <--- CRITICAL FIX: ADDED INPUT
    State('selected-universe-name-store', 'data'),
    State('universe-data-store', 'data'),
    State('research-hub-tabs', 'value'), 
    prevent_initial_call=True
)
def delete_universe_confirmed(n_clicks, pathname, selected_name, universe_data, active_tab): # <--- CRITICAL FIX: ADDED ARGUMENT
    if pathname != '/research-hub':
        raise PreventUpdate # <-- NEW GLOBAL GATE CHECK

    if active_tab != 'universe-manager-tab':
        raise PreventUpdate
        
    if not n_clicks:
        raise PreventUpdate

    if selected_name in universe_data:
        updated_universes = copy.deepcopy(universe_data)
        del updated_universes[selected_name]
        
        return updated_universes, n_clicks, False 
        
    return dash.no_update, dash.no_update, False

# ============================================================================
# CALLBACK 11 (NEW): Layout Auto-Incrementer (The Clock Pulse)
# This fires ONCE when the Research Hub page and its contents are initially mounted.
# ============================================================================
@dash.callback(
    Output('research-hub-load-trigger', 'data'),
    Input('tabs-content', 'children'), # Fires when content of research hub is first rendered
    Input('url', 'pathname'),
    State('research-hub-load-trigger', 'data'),
    prevent_initial_call=False
)
def increment_load_trigger(tabs_content, pathname, current_data):
    # Only fire when we are on the correct page and content is not None/empty
    if pathname == '/research-hub' and tabs_content is not None:
        return current_data + 1
    
    # Prevent update on every other page, ensuring the counter is stable
    raise PreventUpdate

# ============================================================================
# CALLBACK 12 (NEW): Toggle Editor Tab Visibility
# ============================================================================
@dash.callback(
    Output('add-list-controls', 'style'),
    Output('remove-list-controls', 'style'),
    Output('manual-stocks-textarea', 'style'),
    Output('manual-entry-hint', 'style'),
    Input('edit-tabs', 'value'),
    State('research-hub-active-flag', 'data'),
    prevent_initial_call=True
)
def toggle_editor_tab_visibility(active_editor_tab, is_active):
    if not is_active:
        raise PreventUpdate

    hide = {'display': 'none'}
    show = {'display': 'block'}
    
    if active_editor_tab == 'tab-add':
        return show, hide, {'display': 'none', 'rows': 5}, {'display': 'none'}
    elif active_editor_tab == 'tab-remove':
        return hide, show, {'display': 'none', 'rows': 5}, {'display': 'none'}
    elif active_editor_tab == 'tab-manual':
        return hide, hide, {'display': 'block', 'rows': 5}, {'display': 'block'}
        
    return hide, hide, {'display': 'none', 'rows': 5}, {'display': 'none'}