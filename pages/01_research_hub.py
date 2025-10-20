# foundry_dash/pages/01_research_hub.py (Complete Code with UI Fixes)

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
import time
import dash_bootstrap_components as dbc # New import for professional UI
import copy 

# --- Register the Page ---
dash.register_page(
    __name__, 
    path='/research-hub', 
    name='🔭 Research Hub',  
    order=1
)

# --- Import Core Logic ---
from core.io.data_persistence import save_universes, load_universes, get_all_known_tickers
from core.logic.universe_helpers import apply_universe_changes, create_table_data, get_available_stocks, get_stock_details_df

# --- UI Component Functions ---

def universe_controls_section() -> dbc.Card:
    """Controls for selecting, creating, and deleting universes, now using light card styling."""
    return dbc.Card([
        dbc.CardHeader(html.H4("Universe Management", className="card-title")),
        dbc.CardBody([
            html.P("Select/Change Universe:", className="card-text text-muted"),
            # Universe Selection Dropdown
            dcc.Dropdown(
                id='universe-dropdown',
                placeholder="Select Universe",
                value='Nifty 50',
                clearable=False,
                className="mb-4"
            ),
            
            # Delete Button (Now opens the Modal)
            dbc.Button(
                "Delete Selected Universe",
                id='open-delete-modal-button',
                color="danger", # Red for destructive action (high contrast)
                className="mb-4 w-100"
            ),
            
            html.Hr(),

            # Create New Universe Input
            html.H5("Create New Universe", className="h6"),
            dcc.Input(
                id='new-universe-name-input',
                placeholder="e.g., US_Tech_Giants",
                type='text',
                className="form-control mb-2"
            ),
            dbc.Button(
                "Create",
                id='create-universe-button',
                color="success", # Green for creation (high contrast)
                className="w-100"
            ),
        ])
    ], className="h-100") # Ensure card takes full height

def universe_editor_section() -> dbc.Card:
    """The editor section containing tabs for manipulation."""
    return dbc.Card([
        dbc.CardHeader(html.H4(id='editing-title', className="mb-0")),
        dbc.CardBody([
            # Tabs for Add/Remove/Manual Entry
            dcc.Tabs(id="edit-tabs", value='tab-add', children=[
                dcc.Tab(label='Add From List', value='tab-add', children=[
                    html.P("Select stocks to add:", className="mt-4"),
                    dcc.Dropdown(id='stocks-to-add-dropdown', options=[], multi=True),
                    html.P(id='selected-add-count', className="text-muted small mt-2"),
                ]),
                dcc.Tab(label='Remove From List', value='tab-remove', children=[
                    html.P("Select stocks to remove:", className="mt-4"),
                    dcc.Dropdown(id='stocks-to-remove-dropdown', options=[], multi=True),
                    html.P(id='selected-remove-count', className="text-muted small mt-2"),
                ]),
                dcc.Tab(label='Manual Entry', value='tab-manual', children=[
                    dcc.Textarea(
                        id='manual-stocks-textarea',
                        placeholder="NSE:RELIANCE-EQ\nBSE:TCS-EQ\n...",
                        className="form-control mt-4",
                        rows=5
                    ),
                    html.P("Format: EXCHANGE:SYMBOL-SUFFIX (one per line)", className="text-muted small mt-2"),
                ]),
            ]),
            
            # Save Button
            dbc.Button(
                "Save Changes",
                id='save-changes-button',
                n_clicks=0,
                color="primary",
                className="w-100 mt-4"
            ),
        ])
    ])

def stock_viewer_section() -> dbc.Card:
    """New section for professional stock viewing (Bug 6)."""
    return dbc.Card([
        dbc.CardHeader(html.H4("Current Universe Stock Details", className="mb-0")),
        dbc.CardBody([
            html.P(id='table-count', className="card-text font-weight-bold mb-3"),
            
            # The data will be rendered here via callback 
            html.Div(id='stock-viewer-area')
        ])
    ], className="h-100")

# --- Modal for Delete Confirmation (Bug 4) ---
delete_confirmation_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Confirm Universe Deletion")),
        dbc.ModalBody(
            html.P(
                id='delete-modal-body', 
                children=["Are you sure you want to delete the selected universe? This cannot be undone."]
            )
        ),
        dbc.ModalFooter([
            dbc.Button(
                "Cancel", 
                id="cancel-delete-button", 
                className="ms-auto", 
                n_clicks=0
            ),
            dbc.Button(
                "Confirm Delete", 
                id="confirm-delete-button", 
                color="danger", 
                n_clicks=0
            ),
        ]),
    ],
    id="delete-confirmation-modal",
    is_open=False,
)


# --- Page Layout ---
layout = html.Div([
    html.H1("Research Hub: Stock Universe Manager", className="display-4 mb-4"),
    
    # Hidden Stores (State Management)
    dcc.Store(id='universe-data-store', data={}),
    dcc.Store(id='global-known-tickers-store', data=get_all_known_tickers()),
    dcc.Store(id='save-trigger-store', data=0), 
    dcc.Store(id='selected-universe-name-store', data='Nifty 50'),
    dcc.Store(id='modal-trigger-store', data=0), # New store to track modal close/open

    delete_confirmation_modal, # Add the modal to the layout

    # Grid Layout (1fr 1fr 2fr for better data viewing)
    dbc.Row([
        # Column 1: Controls (Selection/Creation) - md=3 (Slightly smaller)
        dbc.Col(universe_controls_section(), md=3), 
        
        # Column 2: Editor Tabs (Add/Remove/Manual) - md=4
        dbc.Col(universe_editor_section(), md=4),
        
        # Column 3: Stock Viewer/Details (The widest, now md=5)
        dbc.Col(stock_viewer_section(), md=5), 
        
    ], className="g-4"),
    
    # Status and Notifications
    dbc.Alert(id='status-output', color="secondary", is_open=True, className="mt-4"),
])
