# foundry_dash/components/research_library_ui.py

from dash import html, dash_table
import dash_bootstrap_components as dbc

def layout() -> dbc.Card:
    """The complete UI layout for the Research Library tab."""
    # Renamed and self-contained
    return dbc.Card([
        dbc.CardHeader(html.H4("📚 Research Library", className="mb-0")),
        dbc.CardBody([
            html.P("Analyze backtest results, filter insights, and manage watchlists."),
            dbc.Alert("Showing 0 results. Run the Performance Engine first.", color="info", id='library-status-alert'),
            html.Div(id='library-data-table', children=[
                dash_table.DataTable(id='research-results-table', data=[], columns=[], page_size=15)
            ]),
        ])
    ], className="mt-3")