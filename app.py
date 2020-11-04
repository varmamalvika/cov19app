import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
from plotly.graph_objs import *
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
from plotly.subplots import make_subplots
from datetime import datetime

external_stylesheets = [dbc.themes.CYBORG]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
styling = {
    'textAlign': 'center',
    'color': colors['text']
}

raw_df_data = requests.get("https://api.covidtracking.com/v1/states/daily.json").json()
df = pd.DataFrame(raw_df_data)
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
df = df.sort_values('date').groupby('state', as_index=False).last()

df_overall_states = df[['state', 'date', 'positive','death','recovered']].copy()
df_overall_states.loc[:, 'positive'] = df_overall_states['positive'].astype('Int32')
df_overall_states.loc[:, 'death'] = df_overall_states['death'].astype('Int32')
df_overall_states.loc[:, 'recovered'] = df_overall_states['recovered'].fillna(value=0).astype('Int32')

last_updated_date = df_overall_states.date.max().date()

df_overall_states['text'] = df_overall_states['state'] + '<br>' + \
    'Deaths: ' + df_overall_states['death'].astype(str) + '<br>' + \
    'Recovered: ' + df_overall_states['recovered'].astype(str) + '<br>'

fig1 = Figure(data=Choropleth(
    locations=df_overall_states['state'],
    z=df_overall_states['positive'],
    locationmode='USA-states',
    colorscale='Reds',
    autocolorscale=False,
    text=df_overall_states['text'], # hover text
    colorbar={'title':'Positive Cases'},
))


config = dict({'scrollZoom': False, 'displayModeBar': False})
fig1.update_layout(
    title_text='USA COVID Tracking Map (Hover for breakdown)<br>Last Updated: '+ str(last_updated_date), # Create a Title
    geo_scope='usa',
    template="plotly_dark"
)

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("COVID Tracker", active=True, href="/cov-1", id="page-1-link")),
        dbc.NavItem(dbc.NavLink("COVID Pre-Scanner", disabled=False, href="/cov-2", id="page-2-link")),
        dbc.NavItem(dbc.NavLink("COVID Survival Rate Calculator", disabled=False, href="/cov-3", id="page-3-link")),
        dbc.NavItem(dbc.NavLink("Frontline Responder Appreciation", disabled=False, href="/cov-4", id="page-4-link")),
        dbc.NavItem(dbc.NavLink("Coronavirus Information", disabled=False, href="/cov-5", id="page-5-link")),
    ],
    pills=True, horizontal='center', fill=True,
)

home_page = html.Div(
    [
        html.H1("USA COVID-19 Pandemic Tracker App", style=styling),
        html.Div(nav, style=styling),
    ], style=styling)

content = html.Div(id="page-content", style=styling)

app_page = html.Div([dcc.Location(id="url"), home_page, content], style=styling)

app.layout = dbc.Container(
    children=[app_page]
)

# app.layout = html.Div([
#     dbc.Card(
#         dbc.CardBody([
#             html.Br(),
#             dbc.Row([
#                 dbc.Col([
#                     app_page
#                 ], width=12)
#             ], align='center')
#         ])
#     )
# ])


# Referenced from https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/page-1
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 6)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False, False
    return [pathname == f"/cov-{i}" for i in range(1, 6)]


pg1_content = html.Div(
    [
        html.Hr(),
        dcc.Graph(style={'width': '1200px', 'height': '700px'},
            id='cov-1-graph',
            figure=fig1,
            config={
                'displayModeBar': False,
                'scrollZoom': False
            }
        )
    ])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/cov-1"]:
        return pg1_content
    elif pathname == "/cov-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/cov-3":
        return html.P("Oh cool, this is page 3!")
    elif pathname == "/cov-4":
        return html.P("Oh cool, this is page 4!")
    elif pathname == "/cov-5":
        return html.P("Oh cool, this is page 5!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)
