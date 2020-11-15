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
app.config['suppress_callback_exceptions'] = True
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
styling = {
    'textAlign': 'center',
    'color': colors['text']
}

raw_us_df_data = requests.get("https://api.covidtracking.com/v1/us/daily.json").json()
us_historical_df = pd.DataFrame(raw_us_df_data)
us_historical_df['date'] = pd.to_datetime(us_historical_df['date'], format='%Y%m%d')

raw_state_df_data = requests.get("https://api.covidtracking.com/v1/states/daily.json").json()
states_daily_df = pd.DataFrame(raw_state_df_data)
states_daily_df['date'] = pd.to_datetime(states_daily_df['date'], format='%Y%m%d')
states_daily_df = states_daily_df.sort_values('date').groupby('state', as_index=False).last()

df_overall_states = states_daily_df[['state', 'date', 'positive', 'death', 'recovered']].copy()
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
    text=df_overall_states['text'],  # hover text
    colorbar={'title': 'Positive Cases'},
))

config = dict({'scrollZoom': False, 'displayModeBar': False})
fig1.update_layout(
    title_text='USA COVID Tracking Map (Hover for breakdown)<br>Last Updated: ' + str(last_updated_date),
    # Create a Title
    font=dict(size=10),
    geo_scope='usa',
    template="plotly_dark",
    margin=dict(l=5, r=5, t=30, b=10),
    dragmode=False
)

fig2 = px.bar(us_historical_df, y='positiveIncrease', x='date', text='positiveIncrease',
              labels={'positiveIncrease': 'New Positive Cases', 'date': 'Date'})
fig2.update_traces(hovertemplate='%{x}<br>New Positive Cases: %{y}<br>')
fig2.update_layout(
    title_text='Daily Trends in Number of COVID-19 Positive Cases in the United States (Hover for each day)',
    # Create a Title
    font=dict(size=14),
    template="plotly_dark",
    margin=dict(l=5, r=5, t=30, b=10),
    dragmode=False,
    uniformtext_minsize=12,
    uniformtext_mode='hide'
)

fig3 = px.bar(us_historical_df, y='deathIncrease', x='date', text='deathIncrease',
              labels={'deathIncrease': 'New Death Cases', 'date': 'Date'})
fig3.update_traces(hovertemplate='%{x}<br>New Death Cases: %{y}<br>', marker_color='brown')
fig3.update_layout(
    title_text='Daily Trends in Number of COVID-19 Deaths in the United States (Hover for each day)',  # Create a Title
    font=dict(size=14),
    template="plotly_dark",
    margin=dict(l=5, r=5, t=30, b=10),
    dragmode=False,
    uniformtext_minsize=12,
    uniformtext_mode='hide'
)

fig4 = px.bar(us_historical_df, y='hospitalizedIncrease', x='date', text='hospitalizedIncrease',
              labels={'hospitalizedIncrease': 'New Total Hospitalizations', 'date': 'Date'})
fig4.update_traces(hovertemplate='%{x}<br>New Total Hospitalizations: %{y}<br>', marker_color='green')
fig4.update_layout(
    title_text='Daily Increase in Number of Total Hospitalizations in the United States (Hover for each day)',
    # Create a Title
    font=dict(size=14),
    template="plotly_dark",
    margin=dict(l=5, r=5, t=30, b=10),
    dragmode=False,
    uniformtext_minsize=12,
    uniformtext_mode='hide'
)

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(html.H5("COVID Tracker"), active=True, href="/cov-1", id="page-1-link")),
        dbc.NavItem(dbc.NavLink(html.H5("COVID Pre-Scanner"), disabled=False, href="/cov-2", id="page-2-link")),
        dbc.NavItem(
            dbc.NavLink(html.H5("COVID Survival Rate Calculator"), disabled=False, href="/cov-3", id="page-3-link")),
        dbc.NavItem(
            dbc.NavLink(html.H5("Frontline Responder Appreciation"), disabled=False, href="/cov-4", id="page-4-link")),
        dbc.NavItem(dbc.NavLink(html.H5("Coronavirus Information"), disabled=False, href="/cov-5", id="page-5-link")),
    ],
    pills=True, horizontal='center', fill=True,
)

home_page = html.Div(
    [
        html.H1("USA COVID-19 Pandemic Tracker App", style=styling),
        html.Br(),
        html.Div(nav, style=styling),
    ], style=styling)

content = html.Div(id="page-content", style=styling)

app_page = html.Div([dcc.Location(id="url"), home_page, content], style=styling)

app.layout = dbc.Container(
    children=[app_page], fluid=True
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


us_map = html.Div(
    [
        html.Br(),
        dcc.Graph(style={'width': '100%', 'height': '70vh', 'display': 'flex', 'flex-flow': 'column'},
                  id='cov-1-graph',
                  figure=fig1,
                  config={
                      'displayModeBar': False,
                      'scrollZoom': False
                  }
                  )
    ])

positive_summary = [
    dbc.CardHeader([html.H6("Positive Cases", className="positive-card")]),
    dbc.CardBody(
        [
            html.H4(f"{df_overall_states['positive'].sum():,}", className="card-title1"),
        ]
    ),
]

recovered_summary = [
    dbc.CardHeader([html.H6("Recovered Cases", className="recovered-card")]),
    dbc.CardBody(
        [
            html.H4(f"{df_overall_states['recovered'].sum():,}", className="card-title2"),
        ]
    ),
]

death_summary = [
    dbc.CardHeader([html.H6("Death Cases", className="death-card")]),
    dbc.CardBody(
        [
            html.H4(f"{df_overall_states['death'].sum():,}", className="card-title3"),
        ]
    ),
]

summary_visualization = html.Div(
    [
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dbc.Card(positive_summary, color="warning", inverse=True, outline=True), "auto"),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dbc.Card(recovered_summary, color="success", inverse=True, outline=True), "auto"),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dbc.Card(death_summary, color="danger", inverse=True, outline=True), "auto"),
            ]
        ),
    ])

pos_increase_visualization = html.Div(
    [
        html.Hr(),
        dcc.Graph(style={'width': '100%', 'height': '50vh', 'display': 'flex', 'flex-flow': 'column'},
                  id='cov-2-graph',
                  figure=fig2,
                  config={
                      'displayModeBar': False,
                      'scrollZoom': False
                  }
                  ),
        html.Hr(),
    ]
)

death_increase_visualization = html.Div(
    [
        html.Hr(),
        dcc.Graph(style={'width': '100%', 'height': '50vh', 'display': 'flex', 'flex-flow': 'column'},
                  id='cov-3-graph',
                  figure=fig3,
                  config={
                      'displayModeBar': False,
                      'scrollZoom': False
                  }
                  ),
        html.Hr(),
    ]
)

hosp_increase_visualization = html.Div(
    [
        html.Hr(),
        dcc.Graph(style={'width': '100%', 'height': '50vh', 'display': 'flex', 'flex-flow': 'column'},
                  id='cov-4-graph',
                  figure=fig4,
                  config={
                      'displayModeBar': False,
                      'scrollZoom': False
                  }
                  ),
        html.Hr(),
    ]
)

pg1_content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(summary_visualization, width=2),
                dbc.Col(us_map, width=10),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(pos_increase_visualization, width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(death_increase_visualization, width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(hosp_increase_visualization, width=12),
            ]
        ),
    ]
)

switches = dbc.FormGroup(
    [
        dbc.Checklist(
            options=[
                {"label": "Fever (above 37.8C/100F in armpit or forehead)", "value": "Fever"},
                {"label": "Cough", "value": "Cough"},
                {"label": "Fatigue", "value": "Fatigue"},
                {"label": "Sputum (saliva and mucus coughed up)", "value": "Sputum"},
                {"label": "Muscle or joint aches", "value": "Muscle"},
                {"label": "Headache or Dizziness", "value": "Headache"},
                {"label": "Sore throat", "value": "Sore"},
                {"label": "Nausea or vomiting", "value": "Nausea"},
                {"label": "Diarrhea", "value": "Diarrhea"},
                {"label": "Trouble breathing", "value": "Breathing"},
                {"label": "Persistent pain or pressure in the chest", "value": "Chest"},
                {"label": "Loss of consciousness or Confusion", "value": "Confusion"},
                {"label": "Bluish lips or face", "value": "Bluish"},
                {"label": "Age above 60 years or below 5 years", "value": "Age"},
                {
                    "label": "Chronic Disease (hypertension, respiratory disease, heart disease, diabetes, or immunocompromised)",
                    "value": "Chronic"},
            ],
            value=[],
            id="switches-input",
            switch=True,
            style={
                'textAlign': 'left',
                'color': '#00CED1', #DarkTurquoise
                'display': 'block',
                'width': 'auto',
                'font-size': '20px',
                'line-height': '1',
                # 'padding': '2px 100px',
                'padding-left': '15%',
                'zoom': '1.1'
            },
        ),
    ]
)

pg2_content = html.Div(
    [
        html.Br(),
        dbc.Label(html.H6("Select the symptoms you or someone else is experiencing", className="tab2-title")),
        dbc.Row(
            [
                dbc.Col(dbc.Form([switches]), width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(id="switches-checklist-output", width=12),
            ]
        ),
    ]
)


def pre_screener_result(switches_value):
    screening_result = ""
    color = "warning"
    symptoms_score_mapping = {
        "Fever": 89,
        "Cough": 68,
        "Fatigue": 30,
        "Sputum": 18,
        "Muscle": 14,
        "Headache": 16,
        "Sore": 16,
        "Nausea": 5,
        "Diarrhea": 5,
        "Breathing": 209,
        "Chest": 209,
        "Confusion": 209,
        "Bluish": 209,
        "Age": 52,
        "Chronic": 52
    }
    emergency_symptom_list = ["Breathing", "Chest", "Confusion", "Bluish"]
    major_symptom_list = ["Fever", "Cough"]
    check_any_emergency_symptoms = any(item in switches_value for item in emergency_symptom_list)
    check_all_major_symptoms = all(item in switches_value for item in major_symptom_list)
    final_score = 0
    for symptom in switches_value:
        final_score += symptoms_score_mapping[symptom]
    if final_score >= 209:
        if check_any_emergency_symptoms:
            color = "danger"
            if check_all_major_symptoms:
                screening_result = "Your symptoms indicate that you should consult a doctor immediately for COVID-19 " \
                                   "testing. "
            else:
                screening_result = "Your symptoms indicate that you should consult a doctor immediately."
        else:
            screening_result = "Your symptoms indicate that you should consult a doctor immediately for COVID-19 " \
                               "testing. "
    else:
        screening_result = "Your symptoms indicate that currently you do not need COVID-19 testing. Please continue " \
                           "to monitor your " \
                           "health and practice social distancing. Avoid leaving the house unnecessarily. If you must " \
                           "leave the " \
                           "house, wear a mask or other face covering and stay at least 6 feet away from others."
        color = "success"
    return screening_result, color


@app.callback(Output("switches-checklist-output", "children"), [Input("switches-input", "value"), ], )
def on_form_change(switches_value):
    template = ""
    n_switches = len(switches_value)
    if n_switches > 0:
        screening_result, color = pre_screener_result(switches_value)
        template = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(html.P(screening_result), color=color, inverse=True),
                                "auto")
                    ]
                ),
            ], style={
                'textAlign': 'center',
                'width': 'auto',
                'line-height': '1.2',
                'padding-top': '1%',
                'padding-left': '15%',
                'padding-right': '15%',
                'padding-bottom': '1%',
                'font-size': '18px',
            })
    return template


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/cov-1"]:
        return pg1_content
    elif pathname == "/cov-2":
        return pg2_content
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
    app.run_server(debug=False)
