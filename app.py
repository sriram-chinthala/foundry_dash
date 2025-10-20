# foundry_dash/app.py

import dash
from dash import dcc, html
from pathlib import Path
import diskcache
from dash.background_callback import DiskcacheManager
import dash_bootstrap_components as dbc
# ----------------------------
import os
import sys

# --- CRITICAL FIX: Add project root to path for absolute imports ---
sys.path.append(os.path.join(os.path.dirname(__file__))) 
# ----------------------------------------------------

# --- 1. SETUP: Initialize Cache and Background Manager ---
cache = diskcache.Cache(Path("./cache/dash_cache"))
bcm = DiskcacheManager(cache)

# Initialize the Dash app with an external stylesheet for utility classes (e.g., Tailwind)
external_stylesheets = [dbc.themes.FLATLY]

# --- 2. SETUP: Initialize Dash Application ---
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    background_callback_manager=bcm,
    title="Foundry Trading System",
    external_stylesheets=external_stylesheets,
    
)

# --- CRITICAL: IMPORT CALLBACKS TO REGISTER THEM ---
# This line runs the @dash.callback decorators in the file.
import callbacks.universe_manager_cbs 
# ----------------------------------------------------

# --- 3. LAYOUT: Define the Main Page Structure ---
def create_nav_links():
    """Generates navigation links based on registered pages."""
    nav_list = []
    # Sort pages by their 'order' attribute
    for page in sorted(dash.page_registry.values(), key=lambda p: p.get('order', 0)):
        nav_list.append(
            dcc.Link(
                f"{page['name']}", 
                href=page['path'], 
                className="block p-2 text-white hover:bg-gray-700"
            )
        )
    return html.Div(nav_list)

app.layout = html.Div(
    [
        # Sidebar/Header Area (Navigation)
        html.Div(
            [
                html.H1("FOUNDRY", className="text-3xl font-bold p-4 text-white"),
                create_nav_links(),
                html.Hr(className="border-gray-700 my-2")
            ],
            className="w-64 bg-gray-800 fixed h-full shadow-lg"
        ),
        
        # Main Content Area
        html.Div(
            [
                dash.page_container
            ],
            className="ml-64 p-8"
        ),
        
        # Global Store for Shared Data 
        dcc.Store(id='global-app-store', data={}),
    ]
)


if __name__ == '__main__':
    server = app.server
    print("--- FOUNDRY DASH STARTING ---")
    print(f"Running on DiskCache Manager for background tasks.")
    app.run(debug=True, host='127.0.0.1', port=8050)