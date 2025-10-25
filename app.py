import dash
from dash import dcc, html
from pathlib import Path
import diskcache
from dash.background_callback.managers.diskcache_manager import DiskcacheManager
import dash_bootstrap_components as dbc
from layouts.helpers import system_health_sidebar # Assuming this file exists
from dash.dependencies import Input, Output
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

# ====================================================================
# CRITICAL FIX: Import callbacks AFTER app initialization
# Update the import path for the renamed universe callbacks file!
# ====================================================================
from callbacks import universe_cbs
# Import other callback modules as you create them:
# from callbacks import screener_cbs
# from callbacks import backtester_cbs
# ====================================================================


def create_nav_links():
    """Generates horizontal navigation links using modern symbols."""
    PAGES = [
        {'path': '/', 'name': '🏠 Home', 'order': 0, 'icon': 'fa-house'},
        {'path': '/research-hub', 'name': '🔭 Research Hub', 'order': 1, 'icon': 'fa-flask'},
        {'path': '/screener', 'name': '🔭 Screener', 'order': 2, 'icon': 'fa-magnifying-glass-chart'},
        {'path': '/audit', 'name': '🔥 Audit Lab', 'order': 3, 'icon': 'fa-scale-balanced'},
        {'path': '/backtester', 'name': '🔬 Backtester', 'order': 4, 'icon': 'fa-chart-line'},
        {'path': '/journal', 'name': '📝 Journal', 'order': 5, 'icon': 'fa-book'},
        {'path': '/settings', 'name': '⚙️ Settings', 'order': 6, 'icon': 'fa-gear'},
    ]
    nav_list = []
    
    for page in sorted(PAGES, key=lambda p: p['order']):
        # Using FontAwesome 6 icons (Ensure FontAwesome CSS is included in assets/ or external_stylesheets if available)
        nav_list.append(
            dbc.NavLink(
                [html.I(className=f"fa-solid {page['icon']} me-2"), page['name'].split(" ")[1]],
                href=page['path'], 
                active="exact",
                className="mx-2 fw-bold"
            )
        )
    return dbc.Nav(nav_list, navbar=True, className="ms-auto")

# The update_layout_on_nav callback is fine as-is for initial integration
@app.callback(
    Output('sidebar-container', 'className'),
    Output('page-content-container', 'className'),
    Input('url', 'pathname')
)
def update_layout_on_nav(pathname):
    # Determine which pages should show the Governor/Health sidebar
    PAGES_WITH_SIDEBAR = ['/', '/audit'] 
    
    if pathname in PAGES_WITH_SIDEBAR:
        # Show sidebar
        sidebar_class = "w-64 bg-dark p-3 h-full fixed overflow-auto" # Retaining your Tailwind/Custom classes
        # Content needs margin to move past the sidebar
        content_class = "ml-64 p-4 flex-grow-1" 
    else:
        # Hide sidebar
        sidebar_class = "d-none" 
        # Content needs no margin and should take full width
        content_class = "ml-0 p-4 w-100" 
        
    return sidebar_class, content_class

app.layout = html.Div(
    [
        # URL Location component - ONLY ONE INSTANCE NEEDED
        dcc.Location(id='url', refresh=False),
        
        # TOP NAVIGATION BAR
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarBrand("⚒️ FOUNDRY", className="fw-bold fs-4 text-primary"),
                    dbc.Collapse(
                        create_nav_links(), 
                        id="navbar-collapse", 
                        is_open=True, 
                        navbar=True
                    )
                ], fluid=True
            ),
            color="light",
            dark=False,
            className="shadow-sm sticky-top"
        ),
        
        # MAIN BODY (Sidebar and Content)
        html.Div(
            [
                # Sidebar Container: Governor/System Health (Dynamically shown/hidden)
                html.Div(
                    system_health_sidebar(),
                    id='sidebar-container',
                    className="w-64 fixed h-full" # Initial class applied
                ),

                # Page Content Container: Renders the actual page layouts
                html.Div(
                    [
                        dash.page_container,  # This renders your pages
                    ],
                    id='page-content-container',
                    className="ml-64 p-4 flex-grow-1" # Initial class applied
                )
            ],
            className="d-flex" 
        ),
        
        # Global Store for Shared Data 
        dcc.Store(id='global-app-store', data={}),
    ]
)


if __name__ == '__main__':
    server = app.server
    print("--- FOUNDRY DASH STARTING ---")
    print(f"Running on DiskCache Manager for background tasks.")
    print(f"Registered pages: {list(dash.page_registry.keys())}")
    app.run(debug=True, host='127.0.0.1', port=8050)