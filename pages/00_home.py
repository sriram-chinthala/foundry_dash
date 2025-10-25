# foundry_dash/pages/00_home.py (Aesthetic & Structural Upgrade)

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime

# Registration remains the same
dash.register_page(__name__, path='/', name='🏠 Home', order=0)

# Mock Data (Should be replaced by dcc.Store inputs later)
QUICK_STATS = {
    'strategies': 12,
    'universes': 3,
    'library_size': '3,450 backtests'
}

# --- Quick Stats Card (Enhanced Grid Layout) ---
def render_quick_stats() -> dbc.Card:
    """Uses a grid for a high-density, professional stats view."""
    return dbc.Card(
        dbc.CardBody([
            html.H5("📊 QUICK STATS", className="card-title text-muted mb-3"),
            dbc.Row([
                dbc.Col(html.P(f"Strategies: {QUICK_STATS['strategies']}"), md=6),
                dbc.Col(html.P(f"Universes: {QUICK_STATS['universes']}"), md=6),
                dbc.Col(html.P(f"Library Size: {QUICK_STATS['library_size']}"), md=12),
                dbc.Col(html.P(f"Last Update: {datetime.now().strftime('%H:%M')}"), md=12, className="text-info small"),
            ], className="g-1") # g-1 for compact spacing
        ]), className="shadow-sm border-start border-info border-5" # Add border for visual emphasis
    )

# --- Quick Actions Card (Modern Stack) ---
def render_quick_actions() -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.H5("🚀 QUICK ACTIONS", className="card-title text-muted mb-3"),
            dbc.Stack([
                # Using icons for professional feel
                dbc.Button(
                    [html.I(className="fa-solid fa-flask me-2"), "Go to Research Hub"], 
                    href="/research-hub", color="primary", className="w-100 fw-bold"
                ),
                dbc.Button(
                    [html.I(className="fa-solid fa-magnifying-glass-chart me-2"), "Open Screener"], 
                    href="/screener", color="primary", outline=True, className="w-100"
                ),
                dbc.Button(
                    [html.I(className="fa-solid fa-gear me-2"), "Build Performance Library"], 
                    color="secondary", className="w-100"
                ),
            ], gap=2)
        ]), className="shadow-sm border-start border-primary border-5"
    )

# --- Recent Activity Card ---
def render_recent_activity() -> dbc.Card:
    activity_list = [
        "Performance library built (2h ago)",
        "New strategy created: 'Momentum_V3'",
        "Screener scan completed: 12 signals",
        "Trade journal updated: 1 new entry"
    ]
    return dbc.Card(
        dbc.CardBody([
            html.H5("📚 RECENT ACTIVITY", className="card-title text-muted mb-3"),
            html.Ul([
                html.Li(
                    [html.I(className="fa-solid fa-circle-dot me-2 text-info small"), item], 
                    className="mb-1"
                ) for item in activity_list], 
                className="list-unstyled small"
            )
        ]), className="shadow-sm border-start border-secondary border-5"
    )

# --- Main Page Layout ---
layout = dbc.Container([
    html.H1("🎯 WELCOME TO FOUNDRY", className="display-3 fw-bold text-primary mb-4 mt-3"),
    html.P("Your systematic trading workflow in two phases:", className="lead text-muted"),

    # WORKFLOW BLOCKS (Cleaned up using CardGroups)
    dbc.CardGroup([
        dbc.Card(
            dbc.CardBody([
                html.H4("📚 RESEARCH PHASE (Periodic)", className="text-success"),
                html.P("Build strategies → Generate Performance Library → Organize insights"),
            ]), className="text-center border-success"
        ),
        dbc.Card(
            dbc.CardBody([
                html.H4("🎯 HUNTING PHASE (Daily)", className="text-info"),
                html.P("Filter → Compare → Verify → Stress-Test"),
            ]), className="text-center border-info"
        ),
    ], className="mb-5 shadow"),

    # STATS AND ACTIONS ROW
    dbc.Row([
        dbc.Col(render_quick_stats(), md=4),
        dbc.Col(render_quick_actions(), md=4),
        dbc.Col(render_recent_activity(), md=4),
    ], className="g-4")
    
], fluid=True, className="mt-2")