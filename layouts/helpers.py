# foundry_dash/layouts/helpers.py

import dash_bootstrap_components as dbc
from dash import html

def render_page_header(title, subtitle):
    """Creates a consistent, professional header card with reduced vertical space."""
    return dbc.Card(
        dbc.CardBody([
            # Reduced heading size to H4
            html.H4(title, className="card-title text-primary"), 
            html.P(subtitle, className="card-text text-muted"),
        ]),
        # Reduced bottom margin to mb-2
        className="mb-2 shadow-sm border-start border-primary border-5" 
    )

def system_health_sidebar():
    """Renders the persistent health monitoring panel with high-contrast text."""
    # NOTE: This content is moved here from app.py
    return html.Div(
        [
            # Headers are correct (text-white)
            html.H5("📊 SYSTEM HEALTH", className="text-white mt-4 mb-2"),
            dbc.Progress(value=45, label="CPU: 45%", color="success", className="mb-2"),
            dbc.Progress(value=62, label="RAM: 62%", color="warning", className="mb-2"),
            dbc.Progress(value=78, label="Disk: 78%", color="warning", className="mb-4"),
            
            html.H5("📈 DATA STATUS", className="text-white mt-4 mb-2"),
            html.Hr(className="border-light my-1"), 
            
            # CRITICAL FIX: Ensure ALL essential text is explicitly text-white
            html.P("✅ Fresh (Updated 2h ago)", className="text-white small"), 
            html.P("Last Library Build: ✅ Success", className="text-white small"), 
            html.P("250/250 Strategies Processed", className="text-white small"), # Changed from text-muted
            
            html.H5("🐛 DEBUG", className="text-white mt-4 mb-2"),
            dbc.Button("Show Debug Info", color="secondary", outline=True, size="sm")
        ],
        className="w-64 bg-dark p-3 h-full fixed overflow-auto"
    )