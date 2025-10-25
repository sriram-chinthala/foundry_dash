# foundry_dash/components/strategy_builder_ui.py

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout() -> dbc.Card:
    """The complete UI layout for the Strategy Builder tab."""
    # Renamed and self-contained
    return dbc.Card([
        dbc.CardHeader(html.H4("🧪 Strategy Builder", className="mb-0")),
        dbc.CardBody([
            html.P("Visually create and manage your trading strategies."),
            dcc.Tabs(id='strategy-builder-tabs', children=[
                dcc.Tab(label="Visual Rule Builder", value='visual-tab', children=[
                    dbc.Alert("Visualization logic will be migrated here.", color="info", className="mt-3"),
                ]),
                dcc.Tab(label="🐍 Python Coder's Pad", value='coder-tab', children=[
                    dcc.Textarea(
                        id='strategy-coder-pad',
                        placeholder="Paste Python Strategy Code here...", 
                        rows=10, 
                        className="form-control mt-3"
                    ),
                    dbc.Button(
                        "💾 Save as Python Strategy", 
                        id='save-strategy-button',
                        color="secondary", 
                        className="mt-3"
                    )
                ]),
            ])
        ])
    ], className="mt-3")