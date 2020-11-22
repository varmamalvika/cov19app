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

age_sex_state_df = pd.read_csv('Covid_Age_Sex_State_Data.csv')
age_sex_state_df['COVID-19 Deaths'] = age_sex_state_df['COVID-19 Deaths'].fillna(0)
print(age_sex_state_df["State"].unique())

underlying_conditions_df = pd.read_csv('Covid_Underlying_Conditions_Data.csv')
underlying_conditions_df['Number of COVID-19 Deaths'] = underlying_conditions_df['Number of COVID-19 Deaths'].fillna(0)

print(underlying_conditions_df["State"].unique())
print(underlying_conditions_df["Condition Group"].unique())

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
                'color': '#00CED1',  # DarkTurquoise
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


style_calc_row_label = {
    'textAlign': 'left',
    'color': 'Gold',
    'display': 'inline',
    'width': 'auto',
    'font-size': '20px',
    'line-height': '1.2',
    # 'padding': '2px 100px',
    'padding-left': '15%',
    'zoom': '1.1',
    'float': 'left'
}

style_calc_items = {
    'textAlign': 'left',
    'color': '#FF6347',  # Tomato
    'display': 'block',
    'width': 'auto',
    'font-size': '19.5px',
    'line-height': '1.1',
    'zoom': '1.1'
}

age_map_multiple_dfs = {
    '0-24 years': '0-24', '25-34 years': '25-34', '35-44 years': '35-44', '45-54 years': '45-54',
    '55-64 years': '55-64', '65-74 years': '65-74', '75-84 years': '75-84',
    '85 years and over': '85+'
}

unique_age_groups = ['0-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84',
                     '85+']

age_group_options = []
for age_group in unique_age_groups:
    if age_group == '85+':
        age_group_options.append({"label": age_group, "value": "85 years and over"})
    else:
        age_group_options.append({"label": age_group, "value": age_group + " years"})


age_group_radioitems = dbc.FormGroup(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Label("Age Group", style=style_calc_row_label, ), width=2),
                dbc.Col(dbc.RadioItems(
                    options=age_group_options,
                    value='0-24 years',
                    inline=True,
                    id="age-group-radioitems-input",
                    style=style_calc_items,
                ), width=10),
            ]
        )
    ]
)


unique_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
                 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida',
                 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
                 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
                 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
                 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
                 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
                 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah',
                 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
                 'Puerto Rico']

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

state_options = []
for state in unique_states:
    state_options.append({"label": state, "value": state})

state_dropdown = dbc.FormGroup(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Label("State", style=style_calc_row_label, ), width=2),
                dbc.Col(dbc.Select(
                    options=state_options,
                    value=unique_states[0],
                    id="state-dropdown-input",
                    style=style_calc_items,
                ), width=10),
            ]
        )
    ]
)

gender_radioitems = dbc.FormGroup(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Label("Gender", style=style_calc_row_label, ), width=2),
                dbc.Col(dbc.RadioItems(
                    options=[
                        {"label": "Male", "value": "Male"},
                        {"label": "Female", "value": "Female"},
                        {"label": "Other", "value": "Unknown"},
                    ],
                    value="Male",
                    inline=True,
                    id="gender-radioitems-input",
                    style=style_calc_items,
                ), width=10),
            ]
        )
    ]
)

unique_diseases = ['Respiratory diseases', 'Circulatory diseases', 'Sepsis',
                   'Malignant neoplasms', 'Diabetes', 'Obesity', 'Alzheimer disease',
                   'Vascular and unspecified dementia', 'Renal failure',
                   'Intentional and unintentional injury, poisoning, and other adverse events',
                   'All other conditions and causes (residual)']

diseases_options = []
for disease in unique_diseases:
    diseases_options.append({"label": disease, "value": disease})

health_cond_checkbox = dbc.FormGroup(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Label("Underlying Health Conditions", style=style_calc_row_label, ), width=2),
                dbc.Col(dbc.Checklist(
                    options=diseases_options,
                    value=[],
                    id="health-cond-checkbox-input",
                    style=style_calc_items,
                    inline=False
                ), width=10),
            ]
        )
    ]
)

pg3_content = html.Div(
    [
        html.Hr(),
        # dbc.Label(html.H6("Select the symptoms you or someone else is experiencing", className="tab2-title")),
        dbc.Row(
            [
                dbc.Col(dbc.Form([age_group_radioitems, state_dropdown, gender_radioitems, health_cond_checkbox]),
                        width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(id="switches-calc-checklist-output", width=12),
            ]
        ),
    ]
)


def calc_death_rate_demographics(age_group_value, state_value, gender_value):
    if age_group_value == '0-24 years':
        deaths_under1_query_result = age_sex_state_df.loc[
            (age_sex_state_df['Age group'] == "Under 1 year") & (age_sex_state_df['State'] == state_value) & (
                    age_sex_state_df['Sex'] == gender_value), ['COVID-19 Deaths']].values[0].flat[0]
        deaths_1to4_query_result = age_sex_state_df.loc[
            (age_sex_state_df['Age group'] == "1-4 years") & (age_sex_state_df['State'] == state_value) & (
                    age_sex_state_df['Sex'] == gender_value), ['COVID-19 Deaths']].values[0].flat[0]
        deaths_5to14_query_result = age_sex_state_df.loc[
            (age_sex_state_df['Age group'] == "5-14 years") & (age_sex_state_df['State'] == state_value) & (
                    age_sex_state_df['Sex'] == gender_value), ['COVID-19 Deaths']].values[0].flat[0]
        deaths_15to24_query_result = age_sex_state_df.loc[
            (age_sex_state_df['Age group'] == "15-24 years") & (age_sex_state_df['State'] == state_value) & (
                    age_sex_state_df['Sex'] == gender_value), ['COVID-19 Deaths']].values[0].flat[0]
        deaths_query_result = deaths_under1_query_result + deaths_1to4_query_result + deaths_5to14_query_result + deaths_15to24_query_result
    else:
        deaths_query_result = age_sex_state_df.loc[
            (age_sex_state_df['Age group'] == age_group_value) & (age_sex_state_df['State'] == state_value) & (
                    age_sex_state_df['Sex'] == gender_value), ['COVID-19 Deaths']].values[0].flat[0]
    total_us_deaths_query_result = age_sex_state_df.loc[
        (age_sex_state_df['Age group'] == "All Ages") & (age_sex_state_df['State'] == "United States") & (
                age_sex_state_df['Sex'] == "All Sexes"), ['COVID-19 Deaths']].values[0].flat[0]
    death_rate_demographics = (deaths_query_result/total_us_deaths_query_result)*100
    return death_rate_demographics


def calc_death_rate_diseases(age_group_value, state_value, health_conditions_values):
    state_code = us_state_abbrev[state_value]
    age_group = age_map_multiple_dfs[age_group_value]
    death_rate_all_conditions = 0
    for condition in health_conditions_values:
        condition_total_deaths = underlying_conditions_df.loc[
            (underlying_conditions_df['Age Group'] == "All Ages") & (underlying_conditions_df['State'] == "US") & (
                    underlying_conditions_df['Condition Group'] == condition), ['Number of COVID-19 Deaths']].values.sum()
        deaths_query_result = underlying_conditions_df.loc[
            (underlying_conditions_df['Age Group'] == age_group) & (
                        underlying_conditions_df['State'] == state_code) & (
                    underlying_conditions_df['Condition Group'] == condition), ['Number of COVID-19 Deaths']].values.sum()
        conditional_death_rate = (deaths_query_result / condition_total_deaths) * 100
        death_rate_all_conditions += conditional_death_rate
    return death_rate_all_conditions


@app.callback(Output("switches-calc-checklist-output", "children"),
              [Input("age-group-radioitems-input", "value"), Input("state-dropdown-input", "value"),
               Input("gender-radioitems-input", "value"), Input("health-cond-checkbox-input", "value"), ], )
def on_form_change(age_group_value, state_value, gender_value, health_conditions_values):
    death_rate_demographics = calc_death_rate_demographics(age_group_value, state_value, gender_value)
    if len(health_conditions_values) > 0:
        death_rate_diseases = calc_death_rate_diseases(age_group_value, state_value, health_conditions_values)
        final_surv_rate = 100 - (death_rate_demographics + death_rate_diseases)
    else:
        final_surv_rate = 100 - death_rate_demographics

    estimation_message = "Your estimated survival rate is " + str(round(final_surv_rate, 2)) + "%"
    template = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(html.H4(estimation_message),
                                     color="success", inverse=True),
                            "auto")
                ]
            ),
        ], style={
            'textAlign': 'center',
            'width': 'auto',
            'line-height': '1.2',
            'padding-top': '1%',
            'padding-left': '30%',
            'padding-right': '30%',
            'padding-bottom': '1%',
            'font-size': '22px',
        })
    return template


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/cov-1"]:
        return pg1_content
    elif pathname == "/cov-2":
        return pg2_content
    elif pathname == "/cov-3":
        return pg3_content
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
