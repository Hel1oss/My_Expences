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
            ### Refresh when user login with their account by redirect web to self
            [dcc.Location(id="refresh-Login", refresh=True),
            
            ### Save dark or light to reuse in darkmode callback
            page.Div(id="Dark_state",
                        style={"display": "None"}),

            ### Save login id to activate other callback chain
            dcc.Store(id="User_ids"),

            ### Graph style need string, dark/light|color to change theme automatically base on theme 
            page.Div(id="graph_cable",
                        style={"display": "None"}), 

            ### this was navbar section and hidden modal
            page.Div([  navbar, offcanvas,
                        modal, 
                        modalLogin, modalCreate,
                        dcc.Location(id="url", refresh=True)]
                    ), 

            ### this was left and right layout instanciated 
            page.Div([rightLayout, 
                        leftLayout],
            id = "Main-background",
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
    app.run(debug=True)    ### test 2
    