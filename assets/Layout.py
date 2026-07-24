import dash
from dash import html as page, dcc, Input, State, Output, callback, ALL, MATCH, callback_context, ctx, clientside_callback, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from assets.Backend import expenceRegister, CategoryRegister, \
                    CategoryViewer, View, CategoryDeleter, \
                    logFrame, Scrape, Download, Upload, rowDeleter, state, \
                    create_table, load_table



Category = list(CategoryViewer().keys())
Time_line = ["All spending", "Today", "This_week", "This_month", "This_Year"]

#### style
empty = [{'category': 'None', 'name': 'None', 'spending': 0}]
navbarcol = {"color": "#ffffff", "textDecoration": "none"}



def itemInList(i, item):
    return page.Div([
        page.Span(f"{i}. {item}", style={"marginTop": "2px"}),
        page.Div([
            dbc.Button(
                "Delete",
                id={"type": "open-del", "item": item}, color= "danger", size="sm"
            ),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                dbc.ModalBody(f"Delete '{item}' ?"),
                dbc.ModalFooter([
                    dbc.Button(
                        "Cancel",
                        id={"type": "close-del", "item": item},
                        className="ms-auto"
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "confirm-del", "item": item},
                        color="danger"
                    ),
                ])
            ],
            id={"type": "modal-del", "item": item},
            is_open=False)
        ])
    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItem": "center",
        "borderBottom" : "1px solid grey",
        "padding" : "2px"
    })

modalLogin = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Login"), close_button=False),
                dbc.ModalBody([
                    dbc.Label("Username"),
                    dbc.Input(placeholder="Type your Username...", type="text", id="Auth_user"),
                    dbc.NavLink("create account", style={"size":"12px"}, id="change_panel1")
                    
            ], style={"padding":"20px"}),
            dbc.ModalFooter([dbc.Button("Login", id="Enter")]),
            ],
            id="modal-dismiss",
            keyboard=False,
            backdrop="static",
            centered=True,
            is_open=True,
            )

modalCreate = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Sign-in"), close_button=False),
                dbc.ModalBody([
                    dbc.Label("Username"),
                    dbc.Input(placeholder="Type your Username...", type="text", id="input_create"),
                    dbc.NavLink("Login", style={"size":"12px"}, id="change_panel2")
                    
            ], style={"padding":"20px"}),
            dbc.ModalFooter([dbc.Button("Create Account", id="button_create")]),
            ],
            id="modalCreate",
            keyboard=False,
            backdrop="static",
            centered=True,
            is_open=False,
            )

rightLayout = page.Div(
    [
        dcc.Dropdown(
            id='timeline',
            options=Time_line,
            value=Time_line[0],
            clearable=False
        ),
        
        dbc.Fade(
            dcc.Graph(id="graph"),
            style={
                "display": "flex",
                "justifyContent": "center",
                "width": "100%"
            } | {"transition": "opacity 2000ms ease"},
            id="fade-transition",
            timeout=2000,
            is_in=False,
        )
    ],
    style={"flex": "1"}
)

leftLayout = page.Div([
    page.Header([page.H1('My Expence')]),
    page.Div([
    page.Header(page.H2("Category:")),
    page.Header([page.H2(id="types")]),
    
    ],style={"display": "flex", "flexDirection": "row", "gap":"5px"}),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add or delete category")),
        page.Div([ 
            dcc.Input(
                id="category2",
                type="text",
                placeholder="add more category",
                debounce=True),
            dcc.Button("add", id= "btn1")],
            style={'display': 'flex','flexDirection': 'row', "paddingInline": "20px"}
            ),
        page.Div([
            itemInList(i, item)
            for i, item in enumerate(Category, start=1)
        ], id="list-container", style = {"padding": "20px"}),
        dbc.ModalFooter(
            dbc.Button(
                "Close",
                id="close-body-scroll",
                className="ms-auto",
                n_clicks=0,
            )
        ),
    ],
    id="modal-body-scroll",
    scrollable=True,
    is_open=False,),
    
    page.Main(style={"display": "grid",
        "gridTemplateColumns": "1fr auto",
        "gap": "2px",
        "width": "fit-content",
        "alignItems": "stretch"},
            
            children=[
            page.Div([ 
                ### section of expence input
                dcc.Input(
                    id="name",
                    type="text",
                    placeholder="Your spending name",
                    debounce=True,
                    style={"minWidth": "360px"}
                ), 
                dcc.Input(
                    id="expence",
                    type="text",
                    placeholder="Spending count",
                    debounce=False,
                    style={"minWidth": "360px"}
                ),
                dcc.Store(id="expense-raw"),
                dcc.Store(id="Trigger"),
                ], 
                style={"display": "flex", "flexDirection": "column"}),
            
            dbc.Button("Send", 
                        id="btn2",
                        n_clicks=0, 
                        style={"marginLeft": "2px"}),

            page.Div([
                dcc.Dropdown(
                    id="category",
                    options=Category,
                    value=Category[0] if Category else None,
                    style = {"minWidth":"251px","height":"38px", "marginRight":"2px"},

                    clearable=False),

                dbc.Button("Manage category", 
                           id="open-body-scroll", 
                           n_clicks=0, 
                           color="white", 
                           style=  {"border":"1px solid grey", 
                                    "alignItems": "center", 
                                    "display": "flex",
                                    "justifyContent": 
                                    "center",  
                                    "height":"35px"}),

                dbc.Button("Del", 
                           id="open_del", 
                           n_clicks=0, 
                           color="white", 
                           style={"border":"1px solid grey", 
                                  "alignItems": "center", 
                                  "display": "flex",
                                  "justifyContent": "center",  
                                  "height":"35px", 
                                  "minWidth":"65px"}),
                ], 
                style={
                        "gridColumn": "1 / -1",
                        "paddingTop": "8px",
                        "marginTop": "4px",
                        "borderTop": "2px solid grey",
                        "display": "flex",
                        "flexDirection": "row",
                    }
                )
            ]
        ),
    page.Div(style={"marginTop":"2px",
                    "display": "flex", 
                    "flexDirection": "row", 
                    "alignItems": "stretch"}),
    page.P(id="List_test"),

    dbc.Fade(
        dag.AgGrid(
            id="List",
            style={"flex": "2"},
            columnSize= "sizeToFit"
        ),
        id="fade-transition2",
        style={"transition": "opacity 2000ms ease"},
        timeout=2000,
        is_in=False
    )
    
    
], style={"padding": "10px"}
)


modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirmation Upload")),
                dbc.ModalBody("This will overwrite your data\nAre you sure?", style={"whiteSpace": "pre-line"}),
                dbc.ModalBody(id="Status"),
                dbc.ModalFooter([
                   
                    dcc.Upload(
                        dbc.Button("Upload data", style=navbarcol, color='danger'),
                        id="uploadnow",
                        accept=".csv"),
                    dbc.Button("Close", id="close1", className="ms-auto", n_clicks=0),
            ]),
            ],
            id="modal1",
            is_open=False,
        )
   
navbar = dbc.Nav(
            [
                dbc.NavLink("Upload data", 
                            style=navbarcol, 
                            id='upload-btn'),
                dbc.NavLink("Download data", 
                            id='download-btn', 
                            style=navbarcol),
                dcc.Download(id="download-df"),
                dbc.NavLink("Add balance", 
                            id="add-balance",
                            style=navbarcol),
                dbc.NavLink(id="Dark_mode", 
                            style=navbarcol),
                dbc.NavLink(id="Show_user", 
                            style=navbarcol | {"marginLeft": "auto"}),
                dbc.Button("Log-out", id="log_out", style={"paddingLeft": "20px"}),
                dcc.Location(id="refresh", refresh=True)

            ], style={"backgroundColor": "#212529", 
                      'top': '0', 
                      'left': '0', 
                      "alignItems": "stretch",
                      'margin': '0', 
                      'padding': '0'}
        )

offcanvas = dbc.Offcanvas(
            [
            page.Div(
                [
                dcc.Input(
                    id="Balance-input", 
                    style={"height":"38px"}, 
                    debounce=False,
                    placeholder="Enter your Income..."
                ), 
                dbc.Button("Add", id="Balance-btn")
                      ], style={"display":"flex", "flexDirection":"row"}),
            
            dcc.Store(id="input-format"),
            
            page.P(id="invis-trigger",  style = {"display": "None"}),
            page.P(id="refresher",  style = {"display": "None"}),
            page.Div(
                    [
                        page.Div(
                            [
                                page.P("Total added balance"),
                                page.P(id="total-added-balance"),
                            ],
                            style={"display": "flex", "justifyContent": "space-between"},
                        ),

                        page.Div(
                            [
                                page.P("Total expense"),
                                page.P(id="total-expense"),
                            ],
                            style={"display": "flex", "justifyContent": "space-between"},
                        ),

                        page.Div(
                            [
                                page.P("Balance left"),
                                page.P(id="current-balance"),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "borderTop": "1px solid grey",
                                "paddingTop": "12px",
                                "marginTop": "12px",
                            },
                        ),
                    ],
                    style={"paddingBlock": "20px"},
                ),
            
            dag.AgGrid(
                columnDefs=[
                    {"field": 'id', "hide":True},
                    {"field": 'date'},
                    {"field": 'income'},
                    {"headerName": "",
                    "cellRenderer": "DeleteButton",
                    "lockPosition":'left',
                    "maxWidth":35,
                    "filter": False,
                    'cellStyle': {
                            "padding": 0,
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                        },
                    }
                    
                    
                    
                    ],
                columnSize="sizeToFit",
                id="Balance-grid"
                )
                
            ],
            id="offcanvas-backdrop",
            title="Add / see current Balance",
            is_open=False,
            backdrop=False
        )