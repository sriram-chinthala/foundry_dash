# foundry_dash/components/performance_engine_ui.py

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout() -> dbc.Card:
    """The complete UI layout for the Performance Engine tab."""
    # Renamed and self-contained
    return dbc.Card([
        dbc.CardHeader(html.H4("⚙️ Performance Engine", className="mb-0")),
        dbc.CardBody([
            html.P("Launch bulk computation jobs to generate the Performance Library. (Long Callback Integration)"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='engine-universe-selector', placeholder="Select Stock Universes", multi=True), md=4),
                dbc.Col(dcc.Dropdown(id='engine-strategy-selector', placeholder="Select Strategy Presets", multi=True), md=4),
                dbc.Col(dcc.Dropdown(id='engine-mode-selector', options=['update', 'full'], value='update', placeholder="Execution Mode"), md=4),
            ], className="mb-4 g-2"),
            dbc.Button("🚀 Launch Engine", id='launch-engine-button', color="success", className="w-100"),
            html.Div(id='engine-log-output', className="mt-4"),
        ])
    ], className="mt-3")