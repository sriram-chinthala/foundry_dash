# foundry_dash/components/universe_manager_ui.py (Universe Manager Layout)

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
# Ensure core logic is available only to the component that needs it
from core.logic.universe_helpers import get_stock_details_df 

# --- Component Functions (Kept as internal helpers) ---

def _universe_controls_section() -> dbc.Card:
    """Controls for selecting, creating, and deleting universes."""
    # (Content remains identical to your original universe_controls_section)
    return dbc.Card([
        dbc.CardHeader(html.H4("Universe Management")),
        dbc.CardBody([
            html.P("Select/Change Universe:", className="card-text text-muted"),
            dcc.Dropdown(
                id='universe-dropdown',
                placeholder="Select Universe",
                value='Nifty 50',
                clearable=False,
                className="mb-4"
            ),
            # ... other controls ...
            dbc.Button(
                "Delete Selected Universe",
                id='open-delete-modal-button',
                color="danger", 
                className="mb-4 w-100"
            ),
            html.Hr(),
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
                color="success",
                className="w-100"
            ),
        ])
    ], className="h-100")

def _universe_editor_section() -> dbc.Card:
    """The editing section containing tabs for manipulation."""
    return dbc.Card([
        dbc.CardHeader(html.H4(id='editing-title', className="mb-0")),
        dbc.CardBody([
            
            # --- CRITICAL FIX: Ensure dropdowns are always in the layout ---
            # Place the dropdowns and text area here, outside the dynamic tabs
            html.Div(id='add-list-controls', children=[
                html.P("Select stocks to add:", className="mt-4"),
                dcc.Dropdown(id='stocks-to-add-dropdown', options=[], multi=True),
                html.P(id='selected-add-count', className="text-muted small mt-2"),
            ]),
            
            html.Div(id='remove-list-controls', style={'display': 'none'}, children=[
                html.P("Select stocks to remove:", className="mt-4"),
                dcc.Dropdown(id='stocks-to-remove-dropdown', options=[], multi=True),
                html.P(id='selected-remove-count', className="text-muted small mt-2"),
            ]),
            
            dcc.Textarea(
                id='manual-stocks-textarea',
                placeholder="NSE:RELIANCE-EQ\nBSE:TCS-EQ\n...",
                className="form-control mt-4",
                rows=5,
                style={'display': 'none'}
            ),
            html.P("Format: EXCHANGE:SYMBOL-SUFFIX (one per line)", id='manual-entry-hint', className="text-muted small mt-2", style={'display': 'none'}),
            # -----------------------------------------------------------------

            # Rework the Tabs to just be the controls for content/visibility
            dcc.Tabs(id="edit-tabs", value='tab-add', children=[
                dcc.Tab(label='Add From List', value='tab-add'),
                dcc.Tab(label='Remove From List', value='tab-remove'),
                dcc.Tab(label='Manual Entry', value='tab-manual'),
            ]),
            
            dbc.Button(
                "Save Changes",
                id='save-changes-button',
                n_clicks=0,
                color="primary",
                className="w-100 mt-4"
            ),
        ])
    ], className="h-100")


def _stock_viewer_section() -> dbc.Card:
    """New section for professional stock viewing."""
    # (Content remains identical to your original stock_viewer_section)
    mock_df = get_stock_details_df([])
    columns = [{"name": col, "id": col} for col in mock_df.columns]
    
    return dbc.Card([
        dbc.CardHeader(html.H4("Current Universe Stock Details", className="mb-0")),
        dbc.CardBody([
            html.P(id='table-count', className="card-text font-weight-bold mb-3"),
            
            html.Div(id='stock-viewer-area', children=[
                 dash_table.DataTable(id='current-universe-viewer-table', columns=columns, data=[], page_size=12, sort_action='native') #type:ignore
            ])
        ])
    ], className="h-100")


# --- MODULAR TAB EXPORT FUNCTION ---
def layout() -> dash.html.Div:
    """The main entry function for the Universe Manager Tab layout."""
    
    # NEW DIAGNOSTIC: Render each section sequentially to find the failure point
    return html.Div(
        id='universe-manager-content-wrapper',
        children=[
            html.H2("--- UI COMPONENT TEST ---"),
            
            # TEST A: Controls Section
            _universe_controls_section(),
            html.Hr(),
            
            # TEST B: Stock Viewer Section
            _stock_viewer_section(),
            html.Hr(),
            
            # TEST C: Editor Section
            _universe_editor_section(),
            html.Hr(),
            
        ],
        # Ensure it is visible by default for the test
        style={'display': 'block'} 
    )

# --- MODAL (Kept for reusability across pages, but defined here) ---
delete_confirmation_modal = dbc.Modal(
    # ... your modal content remains here ...
    [
        dbc.ModalHeader(dbc.ModalTitle("Confirm Universe Deletion")),
        dbc.ModalBody(
            html.P(
                id='delete-modal-body', 
                children=["Are you sure you want to delete the selected universe? This cannot be undone."]
            )
        ),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-delete-button", className="ms-auto", n_clicks=0),
            dbc.Button("Confirm Delete", id="confirm-delete-button", color="danger", n_clicks=0),
        ]),
    ],
    id="delete-confirmation-modal",
    is_open=False,
)