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



controls = dbc.Row(
    [
        dbc.Col(html.Div(
            [
                dbc.Label("Player Selection"),
                dcc.Dropdown(id="player-input", 
                            placeholder="Player Full Name",
                            options=[
                                {'label':name, 'value':name} for name in df['full_name'].unique() #labels in dropdown
                                    ],
                            value='Giannis Antetokounmpo'
                    )
            ])
        ),
        dbc.Col(html.Div(
            [
                dbc.Label("X-Axis Selection"),
                dcc.Dropdown(
                    id='xaxis-column', #ID
                    options = col_dict,
                    value='pts'
                    )
            ])
        ),
        dbc.Col(html.Div(
            [
                dbc.Label("Y-Axis Selection"),
                dcc.Dropdown(
                    id='yaxis-column', #ID
                    options = col_dict,
                    value='true_shooting'
                )
            ])
        ),
        dbc.Col(html.Div(
            [
                dbc.Label("Season Selector"),
                dcc.RangeSlider(
                        id='slider', #ID
                        min=1998, #marks defined below with defaults
                        max=2020,
                        step=2
                    )
            ])
        )
    ]
)


player_layout = dbc.Container(
    [ 
        html.H1("Player Dashboard"),
        html.Hr(),
        controls,
        html.Hr(),
        dbc.Row([
                    dbc.Col([html.H3("Player Comparison"),
                        html.P("This graph shows how the selected player performed against other playeres during that timeframe based on a game-over-game average",
                        style={'font-style':'italic'}),
                        dcc.Graph(id = "histogram-output-container"),
                        dbc.Col([html.H3("Game by Game Against League Average"),
                                html.P("These graphs show how each game played by the selected player compared to the league average over the specified time",
                                style={'font-style':'italic'}),
                                dcc.Graph(id='linechart1-output-container')]),
                        dbc.Col(dcc.Graph(id='linechart2-output-container'))
                    ])
                
            ]
        )
    ], fluid=True
)