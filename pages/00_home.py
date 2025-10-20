# foundry_dash/pages/00_home.py

import dash
from dash import dcc, html

dash.register_page(
    __name__, 
    path='/', 
    name='Home', 
    order=0 # Ensures this is the first item
)

layout = html.Div([
    html.H1("Welcome to Foundry Trading System", className="text-4xl font-extrabold mb-4"),
    html.P("A professional quantitative trading analysis platform.", className="text-lg text-gray-600"),
    
    # CRITICAL: This link provides the working navigation to the Research Hub
    dcc.Link(
        html.Button("Go to Research Hub", className="mt-8 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded"),
        href='/research-hub'
    ),
])