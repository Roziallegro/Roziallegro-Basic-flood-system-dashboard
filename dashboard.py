import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials


# authentication to firebase
try:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred, {"databaseURL": "DATABASE_URL_HERE"})
    main_status = "online"
except:
    # if there is error
    main_status = "offline"
    


# helper functions
def get_day():
    time = datetime.now()
    return(time.strftime("%A"))

def get_date():
    time = datetime.now()
    return(time.strftime("%d %B"))

def get_query(node):
    try:
        return db.reference('/'+node).get()
    except:
        # in case of no connection
        return 0 


def listen_device_status():
    admin = get_query("admin/sensor_status") 
    if admin == "online":
        return update_status("online")
    else:
        return update_status("offline")


def update_status(status):
    if status == "online":
        return html.P("Online", style={"font-family": "Calibri", "color": "#01877E", "font-size": 18, "margin": 0})
    else:
        return html.P("Offline", style={"font-family": "Calibri", "color": "#FFB0A9", "font-size": 18, "margin": 0})
    

def warning_level():
    change_in_water_level = get_query("change_in_level")

    if change_in_water_level == 0:
        return html.P("-", style={"font-family": "Calibri", "color": "#000000", "font-size": 18, "margin": 0})
    elif 0 < change_in_water_level <= 50:
        return html.P("Low flood risk", style={"font-family": "Calibri", "color": "#01877E", "font-size": 18, "margin": 0})
    elif 50 <= change_in_water_level <= 200:
        return html.P("Medium flood risk", style={"font-family": "Calibri", "color": "#F9D678", "font-size": 18, "margin": 0})
    else:
        return html.P("High flood risk", style={"font-family": "Calibri", "color": "#FFB0A9", "font-size": 18, "margin": 0})


# app initialisation
def main() -> None:
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
    app.title = "Flood System"
    app.layout = create_layout(app)
    
    @app.callback([Output(component_id="water_level", component_property="figure"),
                   Output(component_id="water_status", component_property="children")], 
                  [Input('interval-component', 'n_intervals')])
    def gauge_graph(n):
        fig = go.Figure(go.Indicator(
            #mode = "gauge+number+delta",
            mode = "gauge+number",
            value = get_query("change_in_level"), # to change according to db + calibration
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Water level increase", 'font': {'size': 18}},
            #delta = {'reference': 0, 'increasing': {'color': "#FFB284"}, 'decreasing':{'color': "#849D8A"}},
            gauge = {
                'axis': {'range': [None, 1000], 'tickwidth': 1, 'tickcolor': "#13313D"},
                'bar': {'color': "#13313D"},
                'bgcolor': "#FFB0A9",
                'borderwidth': 2,
                'bordercolor': "#FFFFFF",
                'steps': [
                    {'range': [0, 50], 'color': '#01877E'},
                    {'range': [50, 200], 'color': '#F9D678'}],}
        ))

        fig.update_layout(font = {'color': "#13313D", 'family': "Calibri"})

        return fig, warning_level()
    
    app.run_server(debug=True, port=8051)


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.Br(),
            dbc.Row(
                [dbc.Col(left_content(app)),
                dbc.Col(right_content(app), width={"offset": 2}),]
            )
        ],
    )


def left_content(app: Dash) -> html.Div:  
    return html.Div(
        children=[
            html.P("Today", style={"font-family": "Calibri", "font-size": 16, "margin": 0}),
            html.P(get_day(), style={"font-family": "Calibri", "font-size": 25, "font-weight": "bold", "margin": 0}),
            html.P(get_date(), style={"font-family": "Calibri", "font-size": 25, "margin": 0}),
            html.Br(),
            html.P("Location:  Area 1", style={"font-family": "Calibri", "font-size": 18, "margin": 0}),
            html.Div(id="water_status", children=[]),
            html.Div([               
                dcc.Graph(id='water_level', figure={}),
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
            ]),
        ],
    )


def right_content(app: Dash) -> html.Div:
    return html.Div(
        children = [
            html.P("Current database status", style={"font-family": "Calibri", "font-size": 18, "font-weight": "bold", "margin": 0}),
            update_status(main_status),
            html.Br(),
            html.P("Device status", style={"font-family": "Calibri", "font-size": 18, "font-weight": "bold", "margin": 0}),
            listen_device_status(),
        ],
    )


if __name__ == '__main__':
    main()

# running on local host: http://127.0.0.1:8051/