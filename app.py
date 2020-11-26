import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from plotly.graph_objs import *
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

external_stylesheets = [dbc.themes.CYBORG]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Coronavirus Tracker App "
app.config['suppress_callback_exceptions'] = True
server = app.server

colors = {
    'background': '#111111', #dark gray &'#000000' black
    'text': '#00bfff'  #'#7FDBFF'
}
styling = {
    'textAlign': 'center',
    'color': colors['text']
}

age_sex_state_df = pd.read_csv('Covid_Age_Sex_State_Data.csv')
age_sex_state_df['COVID-19 Deaths'] = age_sex_state_df['COVID-19 Deaths'].fillna(0)

underlying_conditions_df = pd.read_csv('Covid_Underlying_Conditions_Data.csv')
underlying_conditions_df['Number of COVID-19 Deaths'] = underlying_conditions_df['Number of COVID-19 Deaths'].fillna(0)

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
        dbc.NavItem(dbc.NavLink(html.H5("COVID Tracker"), active=True, href="/covidtracker", id="page-1-link")),
        dbc.NavItem(dbc.NavLink(html.H5("COVID Pre-Scanner"), disabled=False, href="/covidprescanner", id="page-2-link")),
        dbc.NavItem(
            dbc.NavLink(html.H5("COVID Survival Rate Calculator"), disabled=False, href="/survivalratecalc", id="page-3-link")),
        dbc.NavItem(
            dbc.NavLink(html.H5("Frontline Responder Appreciation"), disabled=False, href="/responderappreciation", id="page-4-link")),
        dbc.NavItem(dbc.NavLink(html.H5("Coronavirus Information"), disabled=False, href="/covidinfo", id="page-5-link")),
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

# Referenced from https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/page-1
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 6)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/" or pathname == "/covidtracker":
        # Treat page 1 as the homepage / index
        return True, False, False, False, False
    elif pathname == "/covidprescanner":
        return False, True, False, False, False
    elif pathname == "/survivalratecalc":
        return False, False, True, False, False
    elif pathname == "/responderappreciation":
        return False, False, False, True, False
    elif pathname == "/covidinfo":
        return False, False, False, False, True


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
        html.P("***The data source is updated each day between about 5:30 PM and 7 PM Eastern Time***")
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
        html.P("***Please note this is just an estimation. In case of emergency, please call 911 or go to your "
               "nearest emergency room.***")
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
        html.Br(),
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
        html.P("***Please note this is just an estimation, and not an absolute assessment of the effects covid-19 "
               "might have on you.***")
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


# fundraising_quote = html.Div(
#     [
#         html.Blockquote(
#             [
#                 html.P(
#                     "Alone we can do so little; together we can do so much",
#                 ),
#                 html.Footer(
#                     html.Small("Helen Keller", className="text-muted")
#                 ),
#             ],
#             className="blockquote",
#         )
#     ]
# )

fundraising_quote_badge = html.Span(
    [
        dbc.Badge("Alone we can do so little; together we can do so much - Helen Keller", pill=True, color="secondary",
                  className="mr-1", style={'display': 'flex', 'flex-flow': 'column', 'font-size': 'small'})
        # style={'font': '10px'},)
    ], style={'display': 'flex', 'flex-flow': 'column'}
)


frontline_fund_card_content = [
    dbc.CardImg(src="/static/images/flrf.PNG", top=True),
    dbc.CardBody(
        [
            html.H5("Frontline Responders Fund", className="card-frontline-title"),
            html.H6(
                "This fundraiser focuses on getting critical supplies to frontline responders combating COVID-19.",
                className="card-frontline-text",
            ),
            dbc.Button("Click me!", size="lg", color="warning", href='https://www.gofundme.com/f/frontlinerespondersfund/', target="_blank"),
        ]
    ),
]

who_fund_card_content = [
    dbc.CardImg(src="/static/images/who.PNG", top=True),
    dbc.CardBody(
        [
            html.H5("COVID-19 Solidarity Response Fund for WHO", className="card-frontline-title"),
            html.H6(
                "Donations support WHO’s work, including with partners, to track and understand the spread of the "
                "virus; to ensure patients get the care they need and frontline workers get essential supplies and "
                "information; and to accelerate research and development of a vaccine and treatments for all who need "
                "them.",
                className="card-frontline-text",
            ),
            dbc.Button("Click me!", size="lg", color="warning", href='https://covid19responsefund.org/en/',
                       target="_blank"),
        ]
    ),
]

#COVID-19 Solidarity Response Fund for WHO

#html.Div(
pg4_content = dbc.Container(
    [
        #html.Br(),
        dbc.Label(html.H4("Help Fight COVID-19", className="tab4-title", style={'color': '#DB7093'})),
        dbc.Row(
            [
                dbc.Col(fundraising_quote_badge, width={"size": 6, "offset": 3})
                #dbc.Col(dbc.Card(fundraising_quote, body=True, color="light"), width={"size": 6, "offset": 3}),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dbc.Card(frontline_fund_card_content, color="info", inverse=True), width=6),
                dbc.Col(dbc.Card(who_fund_card_content, color="info", inverse=True), width=6),
            ]
        ),
        html.Br()
    ],
    style={'display': 'flex', 'flex-flow': 'column'}
)

style_para = {'font-size': '20px', 'color': 'white'}

about_covid_jumbotron = dbc.Jumbotron(
    [
        html.Div([
            html.Img(src="/static/images/covid.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ),
            html.H5(" About COVID-19 ", className="display-4",
                    style={'color': 'black', 'display': 'inline'}),
            html.Img(src="/static/images/covid.ico", style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ), ],
            style={'textAlign': 'center'}),
        html.H4("What is COVID-19?",
                # className="lead",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P(
            "Coronavirus (COVID-19) is an illness caused by a virus that can spread from person to person. COVID-19 "
            "symptoms can range from mild (or no symptoms) to severe illness. ", style=style_para
        ),
        # html.Br(),
        html.H4("Why is it called COVID-19?",
                # className="lead",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P("On February 11, 2020 the World Health Organization announced an official name for the disease that is "
               "causing the 2019 novel coronavirus outbreak, first identified in Wuhan China. The new name of this "
               "disease is coronavirus disease 2019, abbreviated as COVID-19. In COVID-19, ‘CO’ stands for ‘corona,"
               "’ ‘VI’ for ‘virus,’ and ‘D’ for disease. Formerly, this disease was referred to as “2019 novel "
               "coronavirus” or “2019-nCoV”. ", style=style_para
               ),
        html.P("There are many types of human coronaviruses including some that commonly cause mild upper-respiratory "
               "tract illnesses. COVID-19 is a new disease, caused by a novel (or new) coronavirus that has not "
               "previously been seen in humans. ", style=style_para
               ),
    ], style={'background-color': 'SlateBlue', 'text-align': 'left', 'font-family': 'sans-serif', 'padding-top': '2px',
              'padding-bottom': '2px'}
)

covid_spread_jumbotron = dbc.Jumbotron(
    [
        html.Div([
            html.Img(src="/static/images/covidspread.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ),
            html.H5(" COVID-19 Spread ", className="display-4", style={'color': 'black', 'display': 'inline'}),
            html.Img(src="/static/images/covidspread.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}), ], style={'textAlign': 'center'}),
        html.H4("How does COVID-19 spread?",
                # className="lead",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P(
            "You can become infected by coming into close contact (about 6 feet or two arm lengths) with a person who "
            "has COVID-19. COVID-19 is primarily spread from person to person.",
            style=style_para
        ),
        html.P("You can become infected from respiratory droplets when an infected person coughs, sneezes, or talks.",
               style=style_para),
        html.P(
            "You may also be able to get it by touching a surface or object that has the virus on it, and then by "
            "touching your mouth, nose, or eyes.",
            style=style_para),
    ], style={'background-color': '#ac3973', 'text-align': 'left', 'font-family': 'sans-serif', 'padding-top': '2px',
              'padding-bottom': '2px'} #'#800080'
)

covid_prevention_jumbotron = dbc.Jumbotron(
    [
        html.Div([
            html.Img(src="/static/images/covidprevention.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ),
            html.H5(" COVID-19 Prevention ", className="display-4", style={'color': 'black', 'display': 'inline'}),
            html.Img(src="/static/images/covidprevention.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}), ], style={'textAlign': 'center'}),
        html.H4("How to protect myself & others?",
                # className="lead",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P(
            "Stay home as much as possible and avoid close contact with others.",
            style=style_para
        ),
        html.P("Wear a mask that covers your nose and mouth in public settings.",
               style=style_para),
        html.P("Clean and disinfect frequently touched surfaces.",
               style=style_para),
        html.P("Wash your hands often with soap and water for at least 20 seconds, or use an alcohol-based hand "
               "sanitizer that contains at least 60% alcohol.", style=style_para),
        html.P("Monitor your health daily by staying alert for symptoms and by taking your temperature if symptoms "
               "develop", style=style_para),
        html.H4("What should I do if I had a close contact with someone who has COVID-19?",
                # className="lead",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P("Stay home for 14 days after your last contact with a person who has COVID-19.",
               style=style_para),
        html.P("Be alert for symptoms. Watch for fever, cough, shortness of breath, or other symptoms of COVID-19.",
               style=style_para),
        html.P("If possible, stay away from others, especially people who are at higher risk for getting very sick "
               "from COVID-19.", style=style_para),


    ], style={'background-color': 'SlateBlue', 'text-align': 'left', 'font-family': 'sans-serif', 'padding-top': '2px',
              'padding-bottom': '2px'}
)

covid_emergency_jumbotron = dbc.Jumbotron(
    [
        html.Div([
            html.Img(src="/static/images/covidemergency.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ),
            html.H5(" COVID-19 Emergency Warning Signs ", className="display-4",
                    style={'color': 'black', 'display': 'inline'}),
            html.Img(src="/static/images/covidemergency.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}), ], style={'textAlign': 'center'}),
        html.H4("When should I seek emergency care if I have COVID-19?",
                style={'font-weight': 'bold', 'color': '#ffa500'}
                ),
        html.Hr(className="my-2"),
        html.P(
            "Look for emergency warning signs* for COVID-19. If someone is showing any of these signs, seek emergency "
            "medical care immediately",
            style=style_para
        ),
        html.Ul([
            html.Li("Trouble breathing", style=style_para),
            html.Li("Persistent pain or pressure in the chest", style=style_para),
            html.Li("New confusion", style=style_para),
            html.Li("Inability to wake or stay awake", style=style_para),
            html.Li("Bluish lips or face", style=style_para), ]),
        html.P("*This list is not all possible symptoms. Please call your medical provider for any other symptoms "
               "that are severe or concerning to you. Call 911 or call ahead to your local emergency facility: "
               "Notify the operator that you are seeking care for someone who has or may have COVID-19.",
               style=style_para),
    ], style={'background-color': '#ac3973', 'text-align': 'left', 'font-family': 'sans-serif', 'padding-top': '2px',
              'padding-bottom': '2px'}
)

covid_advice_jumbotron = dbc.Jumbotron(
    [
        html.Div([
            html.Img(src="/static/images/covidadvice.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}, ),
            html.H5(" COVID-19 Advice for the public ", className="display-4",
                    style={'color': 'black', 'display': 'inline'}),
            html.Img(src="/static/images/covidadvice.ico",
                     style={'display': 'inline', 'width': '6%', 'height': 'auto'}), ], style={'textAlign': 'center'}),
        html.P("Stay aware of the latest COVID-19 information, by regularly checking updates from WHO (World Health "
               "Organization) and your national and local public health authorities.",
               style=style_para),
        html.Div([
            dbc.Button("Click me to check out WHO's advice for the public", size="lg", color="success",
                       href='https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public',
                       target="_blank"), ], style={'textAlign': 'center'}),
        html.Br(),
    ], style={'background-color': 'SlateBlue', 'text-align': 'left', 'font-family': 'sans-serif', 'padding-top': '2px',
              'padding-bottom': '2px'}
)

pg5_content = html.Div(
    [
        html.Hr(),
        # dbc.Label(html.H6("Select the symptoms you or someone else is experiencing", className="tab2-title")),
        about_covid_jumbotron, covid_spread_jumbotron, covid_prevention_jumbotron, covid_emergency_jumbotron,
        covid_advice_jumbotron,
        html.P("***The source for this information is Centers for Disease Control and Prevention (CDC)***")
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/covidtracker"]:
        return pg1_content
    elif pathname == "/covidprescanner":
        return pg2_content
    elif pathname == "/survivalratecalc":
        return pg3_content
    elif pathname == "/responderappreciation":
        return pg4_content
    elif pathname == "/covidinfo":
        return pg5_content
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=False)
