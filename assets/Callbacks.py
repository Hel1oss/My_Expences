import dash
from dash import html as page, dcc, Input, State, Output, callback, ALL, MATCH, callback_context, ctx, clientside_callback, no_update
from assets.Backend import expenceRegister, CategoryRegister, \
                    CategoryViewer, View, CategoryDeleter, \
                    logFrame, Scrape, Download, Upload, rowDeleter, state, \
                    create_table, load_table, Add_balance, sumALL, Load_balance, Delete_balance
from assets.login_back import Load_user, login, check_exist, create_account, logout
from assets.Layout import itemInList, modalCreate, modalLogin, Category, empty, navbarcol, Time_line, leftLayout, rightLayout, navbar, modal
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import re


@callback(
    Output("refresh", "href"),
    Input("log_out", "n_clicks"),
    prevent_initial_call=True
)
def Log_Out(clicks):
    if ctx.triggered_id == "log_out":
        logout()
        return "/"
    return no_update

###login and control modal
@callback(
    Output("modal-dismiss", "is_open"),
    Output("Auth_user", "value"),
    Output("Auth_user", "invalid"),
    Output("Show_user", "children"),
    Output("User_ids", "data"),
    Output("refresh-Login", "href"),
    Output("fade-transition", "is_in"),
    Output("fade-transition2", "is_in"),
    Input("Enter", "n_clicks"),
    State("Auth_user", "value"),
    State("modal-dismiss", "is_open"),
)
def Login_modal(n_open, user_info, is_open):
    if Load_user():
        active = Load_user()
        if active:
            load_table(active[0])
            return False, no_update, False, f"Welcome, {active[1]}", active[0], no_update, True, True
    if ctx.triggered_id == "Enter" and not user_info:
        return no_update, no_update, True, "", no_update, no_update, no_update, no_update
    if ctx.triggered_id == "Enter" and user_info:
        user = login(user_info)
        if user:
            load_table(user[0])
            return False, "", False, f"Welcome, {user[1]}", user[0],  "/", True, True
        return no_update, no_update, True, "", no_update, no_update, no_update, no_update
    else:
        return no_update, no_update, no_update, "", no_update, no_update, no_update, no_update


### Create account modal --------------------------------------------------------
@callback(
    Output("modalCreate", "is_open"),
    Output("input_create", "value"),
    Output("input_create", "invalid"),
    Input("change_panel1", "n_clicks"),
    Input("change_panel2", "n_clicks"),
    Input("button_create", "n_clicks"),
    State("input_create", "value"),
    State("modal-dismiss", "is_open"),
    prevent_initial_call=True
)

def modal_create(open, close, click_create, input_create, is_open):
    if ctx.triggered_id == "change_panel1": 
        ## open from the Login panel press create account
        return True, no_update, no_update
    if ctx.triggered_id == "change_panel2": 
        ## close with pressing login
        return False, no_update, no_update
    if ctx.triggered_id == "button_create" and input_create: 
        #allow only if input filled and pressing create account
        if not check_exist(input_create):
            create_account(input_create)
            create_table(input_create)
            return False, "", no_update
        else:
            return no_update, no_update, True
    else:
        return no_update, no_update, True
    
## This is for adding expence
@callback(
    Output("name", "value"),
    Output("List", "rowData"),
    Output("types", "children"),
    Input("Trigger", "data"), 
    State('name', 'value'),
    State("expense-raw", 'data'),
    Input('category', 'value'),
    Input("timeline", "value"),
    Input("User_ids", "data")
    )
def expence(n_clicks, name, expence, category, time, ids):
    if ids:
        if category is None:
            return name, empty, ""
        if name and expence:
            expenceRegister(category, name, expence)
        
        return "", logFrame(category, time)[::-1], category
    return no_update,  no_update,  no_update, 

#btn2
@callback(
    Output("Trigger", "data"),
    Input("btn2", "n_clicks"),
    prevent_initial_call=True
)
def btn2(n_clicks):
    return n_clicks

#Input expence cost with regex
@callback(
    Output("expence", "value"), ### okay set to input number
    Output("expense-raw", "data"),
    Input("expence", "value"), #check
    Input("Trigger", "data")
)
def format_expense(value, delete):
    if ctx.triggered_id == "Trigger":
        return "", None
    if not value:
        return "", None
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return "", None
    number = int(digits)
    return f"{number:,}", number


#Graph --------------------------------------------------------------------------------------------
@callback(
Output("graph", "figure"),
Input("List", "rowData"),
Input("timeline", "value"),
Input("List_test", "children"),
Input("graph_cable", "children"),
Input("User_ids", "data")
)
def figure(click, time, deleted, color_graph, ids):
    if ids:
        rows = Scrape(time)
        values=[row[1] for row in rows]
        sumall = sum(values)
        fig = px.pie(
            names=[row[0] for row in rows],
            values=values,
            hole=0.8,
            )
        fig.update_traces(sort=False, 
                        insidetextorientation="radial", 
                        textinfo='label+value+percent', 
                        texttemplate='%{label}<br>Rp%{value:,.0f}<br>(%{percent})',
                        ),
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            template= color_graph.split("|")[0],
            width=700,
            height=700,
            annotations=[
                dict(
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    text=f"{time}<br>Rp.{sumall:,}",
                    font=dict(
                        size=24,
                        color= color_graph.split("|")[1]
                    )
                )
            ]
        )                  
        return fig
    return no_update

## Modal for delete confirmation ---------------------------------------------------------
@callback(
    Output({"type": "modal-del", "item": MATCH}, "is_open"),
    Input({"type": "open-del", "item": MATCH}, "n_clicks"),
    Input({"type": "close-del", "item": MATCH}, "n_clicks"),
    State({"type": "modal-del", "item": MATCH}, "is_open"),
)
def toggle_modal(open_click, close_click, is_open):
    if ctx.triggered_id is not None:
        return not is_open
    return is_open

## Adding and delete category --------------------------------------------------------------
@callback(
    Output('category2', 'value'),
    Output('list-container', 'children'),
    Output('category', 'options'),
    Output('category', 'value'),
    Input('btn1', 'n_clicks'),
    Input({"type": "confirm-del", "item": ALL}, "n_clicks"),
    Input("User_ids", "data"),
    State('category2', 'value'),
    )
def update(n_click, delclick, ids, cat):
    if ids:
        ctx = callback_context.triggered_id
        if isinstance(ctx, dict) and ctx.get("type") == "confirm-del":
            CategoryDeleter(ctx["item"])
        elif ctx == "btn1":
            if cat:
                CategoryRegister(cat)
    
        Category = list(CategoryViewer().keys())
        selected = Category[0] if Category else None
        return "", [itemInList(i, item) for i, item in enumerate(Category, start=1)], Category, selected
    return no_update, [], no_update, no_update

## deleter row
@callback(
    Output("List_test", "children"),
    Input("List", "cellRendererData"),
    Input('category', 'value'),
    prevent_initial_call=True
)
def delrow(inputs, target):

    if inputs and ctx.triggered_id == "List":
        rowDeleter(target, inputs['value']['id'])
        inputs = None

    return ""
    

@callback(
    Output("List", "columnDefs"),
    Output("List", "columnSize"),
    Input("open_del", "n_clicks"),
    Input("User_ids", "data"),
    prevent_initial_call=True
)
def open_del(clicks, ids):
    Open_del = [
            {"field": 'id', "hide":True},
            {"field": 'date'},
            {"field": 'category'},
            {"field": 'name'},
            {"field": 'spending'},
            {
                "headerName": "",
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
        ]
    Close_del = [
            {"field": 'id', "hide":True},
            {"field": 'date'},
            {"field": 'category'},
            {"field": 'name'},
            {"field": 'spending'},
        ]
    open_delete = clicks%2 if clicks else 1
    if ctx.triggered_id == "open_del" and open_delete == 1:
        return Open_del, "sizeToFit"
    else:
        return Close_del,  "sizeToFit"


## Modal Category management button ---------------------
@callback(
    Output("modal-body-scroll", "is_open"),
    Input("open-body-scroll", "n_clicks"),
    Input("close-body-scroll", "n_clicks"),
    State("modal-body-scroll", "is_open"),
    Input("User_ids", "data")
)
def toggle_modal2(n1, n2, is_open, ids):
    if n1 or n2:
        return not is_open
    return is_open



### download manager -------------------------------------
@callback(
    Output("download-df", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download(*args):
    if ctx.triggered_id == "download-btn":
        data = Download()
        return dcc.send_data_frame(data.to_csv, "YourExpence.csv", index=False)

### Upload manager -------------------------------------
@callback(
    Output("modal1", "is_open"),
    [Input("upload-btn", "n_clicks"), 
     Input("close1", "n_clicks")],
    [State("modal1", "is_open")],
    prevent_initial_call=True
)
def toggle_modal3(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output("Status", "children"),
    Output("url", "href"),
    Input("uploadnow", "contents"),
    prevent_initial_call=True
)
def handling_upload(data):
    if not data:
        return "", dash.no_update
    content_type, content_string = data.split(',')
    out = Upload(content_string)
    if out == "Success":
        return out, "/"
    return out, no_update





### DARK MODE -------------------------------------------------

@callback(
    Output("List", "className"),
    Output("Main-background", "className"),
    Output("name", "className"),
    Output("expence", "className"),
    Output("category", "className"),
    Output("timeline", "className"),
    Output("open-body-scroll", "className"),
    Output("open_del", "className"),
    Output("graph_cable", "children"),
    Output("Dark_mode", "children"),
    Output("offcanvas-backdrop", "className"),
    Output("Balance-input", "className"),
    Output("Balance-grid", "className"),
    Output("category", "style"),
    Output("timeline", "style"),
    Input("Dark_state", "children"),
    Input("User_ids", "data")
)
def dark_mode(data, ids):
    dropdown_dark = {
        "--Dash-Fill-Inverse-Strong": "#353b41",
        "--Dash-Stroke-Strong": "#2b2a33",
        "--Dash-Text-Primary": "#ffffff",
        "--Dash-Fill-Interactive-Strong": "#ffffff",
    }
    Category_dropdown = {"minWidth":"251px","height":"38px", "marginRight":"2px"}

    if data == "dark":
        return "my-grid-Dark", "my-custom-style", "input-style", "input-style",\
              "my-dropdown", "my-dropdown", "input-style", "input-style", \
              "plotly_dark|white", "Light Mode Here", "my-custom-style", "input-style", "my-grid-Dark", \
              Category_dropdown | dropdown_dark, {"padding": "8px"} | dropdown_dark
    else: 
        return None, None, None, None, None, None, None, None, "plotly_white|#212529", f"Dark Mode Here", None, None, None, Category_dropdown , {"padding": "8px"}

@callback(
    Output("Dark_state", "children"),
    Input("Dark_mode", "n_clicks"),
    Input("User_ids", "data")
)
def state_dark(n_clicks, ids):
    if ctx.triggered_id == "Dark_mode":
        value_return = state(1)
    else:
        value_return = state()
    
    if value_return%2 == 0:
        return "dark"
    else:
        return "light"

#offcanvas
@callback(
    Output("offcanvas-backdrop", "is_open"),
    Input("add-balance", "n_clicks"),
    State("offcanvas-backdrop", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


## inside the offcanvas
@callback(
    Output("Balance-grid", "rowData"),
    Output("invis-trigger", "children"),
    Output("total-added-balance", "children"),
    Output("total-expense", "children"),
    Output("current-balance", "children"),
    Input("Balance-btn", "n_clicks"),
    Input("refresher", "children"),
    Input("User_ids", "data"),
    Input("List", "rowData"),
    State("input-format", "data")
)
def manage_income(click, ref, ids, tick, values):
    if ids:
        if ctx.triggered_id == "Balance-btn" and values:
            Add_balance(values)
            sum = sumALL()
            return Load_balance(), click, *[f"Rp.{val:,}" for val in sum]
        sum = sumALL()
        return Load_balance(), no_update, *[f"Rp.{val:,}" for val in sum]
    return no_update, no_update, no_update, no_update, no_update


### converter input
@callback(
    Output("Balance-input", "value"), 
    Output("input-format", "data"),
    Input("Balance-input", "value"), 
    Input("invis-trigger", "children"),
    Input("User_ids", "data"),
)
def format_balance(value, delete, ids):
    if ctx.triggered_id == "invis-trigger":
        return "", None
    if not value:
        return "", None
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return "", None
    number = int(digits)
    return f"{number:,}", number


## balance deleter
@callback(
    Output("refresher", "children"),
    Input("Balance-grid", "cellRendererData"),
    Input("User_ids", "data"),
    prevent_initial_call=True
)
def balance_deleter(inputs, ids):

    if inputs and ctx.triggered_id == "Balance-grid":
        Delete_balance(inputs['value']['id'])
        inputs = None

    return ""