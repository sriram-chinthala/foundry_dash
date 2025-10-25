#foundry_dash/pages/01_research_hub.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from pathlib import Path

# --- CORE UTILS ---
# NOTE: These utilities (data_persistence) should not be imported here unless 
# absolutely necessary for INITIALIZING the layout's stores.
from core.io.data_persistence import get_all_known_tickers, load_universes

# --- MODULAR UI IMPORTS ---
from components.universe_manager_ui import delete_confirmation_modal
# We import the layouts here for the tab rendering logic defined later in the callbacks file
# NOTE: The actual layout functions (e.g., universe_manager_layout) are imported 
# inside the callback file for rendering, but we ensure the modals/global elements 
# like delete_confirmation_modal are imported here if needed for the main page layout.


# --- Register the Page ---
dash.register_page(
    __name__, 
    path='/research-hub', 
    name='🔭 Research Hub',  
    order=1
)

# --- Reduced Header Content (Global Page Header) ---
reduced_header = html.Div(
    [
        html.H3("Research Hub", className="text-primary fw-bold mb-1"),
        html.H6("The central control panel for managing universes, strategies, and data processing.", className="text-muted"),
        html.Hr(className="my-3")
    ]
)

# Load initial data for stores
# This logic is necessary to initialize the dcc.Store components on startup
try:
    universes_path = Path('./data/universes.yaml')
    initial_universes = load_universes(universes_path)
    # Safely select the first key or default to 'Nifty 50'
    initial_universe_name = sorted(list(initial_universes.keys()))[0] if initial_universes else 'Nifty 50'
except:
    # Fail-safe initialization
    initial_universes = {"Nifty 50": []}
    initial_universe_name = 'Nifty 50'


# --- Page Layout (The main wiring harness for all tabs) ---
layout = html.Div([
    
    # 1. Header
    reduced_header,
    
    # 2. Hidden Stores (Global State)
    dcc.Store(id='universe-data-store', data=initial_universes),
    dcc.Store(id='global-known-tickers-store', data=get_all_known_tickers()),
    dcc.Store(id='save-trigger-store', data=0), 
    dcc.Store(id='selected-universe-name-store', data=initial_universe_name),
    # Modal related stores are not strictly needed here if they are only 
    # triggered by N_CLICKS, but keeping them if your other files rely on them:
    dcc.Store(id='modal-trigger-store', data=0), 
    dcc.Store(id='modal-close-trigger-store', data=0),
    dcc.Store(id='research-hub-active-flag', data=False),
    dcc.Store(id='research-hub-load-trigger', data=0),

    # 3. Modal (A global component placed in the layout)
    delete_confirmation_modal,

    # 4. Main Tabs (The central router)
    dcc.Tabs(
        id="research-hub-tabs", 
        value='universe-manager-tab',
        parent_className="card mb-4 border-primary",
        className="custom-tabs-container",
        children=[
            dcc.Tab(label='🌍 Universe Manager', value='universe-manager-tab', selected_style={'backgroundColor': 'var(--bs-primary)', 'color': 'white'}, style={'backgroundColor': 'var(--bs-light)'}),
            dcc.Tab(label='🧪 Strategy Builder', value='strategy-builder-tab', selected_style={'backgroundColor': 'var(--bs-primary)', 'color': 'white'}, style={'backgroundColor': 'var(--bs-light)'}),
            dcc.Tab(label='⚙️ Performance Engine', value='performance-engine-tab', selected_style={'backgroundColor': 'var(--bs-primary)', 'color': 'white'}, style={'backgroundColor': 'var(--bs-light)'}),
            dcc.Tab(label='📚 Research Library', value='research-library-tab', selected_style={'backgroundColor': 'var(--bs-primary)', 'color': 'white'}, style={'backgroundColor': 'var(--bs-light)'}),
        ]
    ),
    
    # 5. Tab Content Container (The dynamically updated area)
    html.Div(id='tabs-content'), 

    # 6. Status Output
    dbc.Alert(id='status-output', color="secondary", is_open=True, className="mt-4"),
])