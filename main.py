import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import html as page, dcc, Input, State, Output, callback, ALL, MATCH, callback_context, ctx, clientside_callback, no_update



"""
All content of behind the scene is placed in the asset folders
"""
from assets import Backend
from assets import login_back
from assets.Layout import modalCreate, modalLogin, leftLayout, rightLayout, navbar, modal, offcanvas
from assets import Layout
from assets import Callbacks




app = dash.Dash(__name__)
app.title = "My Expence"


app.layout = page.Div(
  
            [dcc.Location(id="refresh-Login", refresh=True),

            page.Div(id="Dark_state",
                        style={"display": "None"}),

            dcc.Store(id="User_ids"),

            page.Div(id="graph_cable",
                        style={"display": "None"}), 

            page.Div([  navbar, offcanvas,
                        modal, 
                        modalLogin, modalCreate,
                        dcc.Location(id="url", refresh=True)]
                    ), 

            page.Div([rightLayout, 
                        leftLayout],
            id = "Main-background",
            **{"data-theme": "dark"},
            style={
            "display": "flex",
            "flexDirection": "row", 
            "alignItems": "stretch",
            'minHeight': '100vh',
            'margin': '0', 
            'padding': '0',
            'top': '0', 
            'left': '0',
            'width': '100%'
            }
        )
    ]
)


if __name__ == '__main__':
    app.run(debug=True)   
    