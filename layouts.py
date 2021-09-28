import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from utility import get_playerdata as bb_get
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd


####################################################
# Ingest data
####################################################

#bring in data --player>game w/adv metrics calculated
df = pd.read_csv("data/game_last5yr_min5seas.csv")

#Dictionary used to lablel columns in dropdown selector
col_dict = [{"label":"Plus Minus","value":"plus_minus"},
            {"label":"Points", "value":"pts"},
            {"label":"FG%", "value":"fg_pct"},
            {"label":"Rebounds", "value":"reb"},
            {"label":"Offensive Rebounds", "value": "oreb"},
            {"label":"Defensive Rebounds", "value":"dreb"},
            {"label":"Assists", "value":"ast"},
            {"label":"3pt Attempts", "value":"fg3a"},
            {"label":"3pt Makes", "value":"fg3m"},
            {"label":"3pt %", "value":"fg3_pct"},
            {"label":"True Shooting %", "value":"true_shooting"},
            {"label":"Turnover %", "value":"tov_perc"},
            {"label":"Effective FG%", "value":"eff_fg_perc"},
            {"label":"Steals", "value":"stl"},
            {"label":"Blocks", "value":"blk"}]

#Team Colors
team_primary_colors = {'ATL': '#e03a3e',
 'BOS': '#007A33',
 'BKN': '#000000',
 'CHA': '#1d1160',
 'CHI': '#CE1141',
 'CLE': '#860038',
 'DAL': '#00538C',
 'DEN': '#0E2240',
 'DET': '#C8102E',
 'GSW': '#1D428A',
 'HOU': '#CE1141',
 'IND': '#002D62',
 'LAC': '#c8102E',
 'LAL': '#552583',
 'MEM': '#5D76A9',
 'MIA': '#98002E',
 'MIL': '#00471B',
 'MIN': '#0C2340',
 'NOP': '#001641',
 'NYK': '#006BB6',
 'OKC': '#007ac1',
 'ORL': '#0077c0',
 'PHI': '#006bb6',
 'PHX': '#1D1160',
 'POR': '#E03A3E',
 'SAC': '#5A2D81',
 'SAS': '#c4ced4',
 'TOR': '#ce1141',
 'UTA': '#002B5C',
 'WAS': '#002B5C'}

# Create another dictionary for labels
col_dict_labels = {"plus_minus":"Plus Minus",
    "pts":"Points", 
    "fg_pct":"FG%",
    "reb":"Rebounds",
    "oreb":"Offensive Rebounds",
    "dreb":"Defensive Rebounds",
    "ast":"Assists",
    "fg3a":"3pt Attempts",
    "fg3m":"3pt Makes",
    "fg3_pct":"3pt %",
    "true_shooting":"True Shooting %",
    "tov_perc":"Turnover %",
    "eff_fg_perc":"Effective FG%",
    "stl":"Steals",
    "blk":"Blocks"
}

player_layout = html.Div([
    html.Div([ 
        
        html.Div([ 

            #player dropdown input
            html.Div([
                dcc.Dropdown(id="player-input", placeholder="Player Full Name",
                options=[
                    {'label':name, 'value':name} for name in df['full_name'].unique() #labels in dropdown
                ],
                value='Giannis Antetokounmpo' #Default Value
                )
            ],style={'display': 'inline-block', 'padding-right':'10px', 'width':'30%'}
            ),

            #column dropdown input
            html.Div([
                dcc.Dropdown(
                id='xaxis-column', #ID
                options = col_dict,
                value='pts' #Default Value
            )
            ], style={'width':'15%','display': 'inline-block',
                "margin-left": "15px"
                }
            ),

            #y-axis column dropdown
            html.Div([
                dcc.Dropdown(
                id='yaxis-column', #ID
                options = col_dict,
                value='true_shooting' #Default Value
            )
            ], style={'width':'15%','display': 'inline-block',
                "margin-left": "15px"
                }
            ),
            html.Div(
                children=[
                    dcc.RangeSlider(
                        id='slider', #ID
                        min=1998, #marks defined below with defaults
                        max=2020,
                        step=2
                    )
                ],
                style={'width':'30%','display': 'inline-block', "margin-left": "15px",
                "margin-right":"15px"}
            )
        ], style={'height':100})
    ]),
        # Histogram
        html.Div([ 
            html.Div([
                dcc.Graph(id = "histogram-output-container"),
                dcc.Store(id="dataframes")
            ], style={'display': 'block','width':'49%'})
            ,
            html.Div([
                dcc.Graph(id='linechart1-output-container'),
                dcc.Graph(id='linechart2-output-container')
            ], style={'display': 'inline-block','width':'49%'})
        ], style={'display':'block'})
        
])

controls = dbc.Card(
    [
        dbc.FormGroup(
            [ 
                dbc.Label("Player Selection"),
                dcc.Dropdown(id="player-input", 
                             placeholder="Player Full Name",
                             options=[
                                {'label':name, 'value':name} for name in df['full_name'].unique() #labels in dropdown
                                     ],
                             value='Giannis Antetokounmpo' #Default Value
                )
            ]
        ),
        dbc.FormGroup(
            [ 
                dbc.Label("X-Axis Selection"),
                dcc.Dropdown(
                    id='xaxis-column', #ID
                    options = col_dict,
                    value='pts' #Default Value
                )
            ]
        ),
        dbc.FormGroup(
            [ 
                dbc.Label("Y-Axis Selection"),
                dcc.Dropdown(
                    id='yaxis-column', #ID
                    options = col_dict,
                    value='true_shooting' #Default Value
                )
            ]
        ),
        dbc.FormGroup(
            [ 
                dbc.Label("Season Selector"),
                
            ]
        )
    ]
)


