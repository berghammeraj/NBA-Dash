############################################
# Dash to view player stats --sandbox
############################################

#Libraries
import time
import json
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

#from static import team_colors, team_dict, player_color_dict
from utility import get_playerdata as bb_get

from os import path 
import urllib

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

####################################################
# Start App
####################################################
app = dash.Dash(__name__, suppress_callback_exceptions=True)

###################### LAYOUT ######################

#define layout
app.layout = html.Div([
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
    

#############################################
# clean data callbacks
#############################################

# @app.callback(Output("dataframes", 'data'),
#               Input('xaxis-column', 'value'),
#               Input('yaxis-column', 'value'),
#               Input("player-input", "value"),
#               Input("slider", 'value'))
# def clean_data(xcol, ycol, player, seas_vals):

#     # make player df for overall career
#     player_df = df[df['full_name'] == player]

#     try:
#         graph_df_seas = df[(df['full_name'] == player) & (df['season'] >= seas_vals[0]) & (df['season'] <= seas_vals[1])]
#         ovall_df_seas = df[(df['season'] >= seas_vals[0]) & (df['season'] <= seas_vals[1])]
    
#     except:
#         graph_df_seas = df[(df['full_name'] == player)]
#         ovall_df_seas = df.copy()

#     ovall_df = ovall_df_seas.groupby('full_name').agg({
#         xcol:np.median,
#         ycol:np.median
#     })

#     ovall_df['player_color'] = df.groupby('full_name')['tm_colors'].agg(pd.Series.mode)
#     ovall_df['team'] = df.groupby('full_name')['player_tm'].agg(pd.Series.mode)
#     ovall_df['team'] = ovall_df['team'].apply(lambda x: x if isinstance(x, str) else x[0])

#     ovall_df.reset_index(inplace=True)

#     datasets = {
#          'player_df': player_df.to_json(orient='split', date_format='iso'),
#          'graph_df_seas': graph_df_seas.to_json(orient='split', date_format='iso'),
#          'ovall_df_seas': ovall_df_seas.to_json(orient='split', date_format='iso'),
#          'ovall_df':ovall_df.to_json(orient='split', date_format='iso')
#      }

#     return json.dumps(datasets)

#############################################
# slider callbacks
#############################################

#slider minimum
@app.callback(Output("slider", 'min'),
              Input("player-input", "value"))
def generate_slider_min(player):

    slider_df = df[df['full_name'] == player]

    #max_seas=slider_df['season'].max()
    min_seas=slider_df['season'].min()

    return min_seas

#slider minimum
@app.callback(Output("slider", 'max'),
              Input("player-input", "value"))
def generate_slider_max(player):

    slider_df = df[df['full_name'] == player]

    max_seas=slider_df['season'].max()
    #min_seas=slider_df['season'].min()

    return max_seas

#slider marks
@app.callback(Output("slider", 'marks'),
              Input("player-input", "value"))
def generate_slider_marks(player):

    slider_df = df[df['full_name'] == player]

    max_seas=slider_df['season'].max()
    min_seas=slider_df['season'].min()

    if max_seas - min_seas >= 8:
        return {int(x):{'label':str(str(x) +'-' + str(str(int(x)+1))[-2:]),'style':{'transform':'rotate(-90deg)', 'font-size':'8px'}} for x in range(min_seas, max_seas+1) if int(x)%2==0}
    else:
        return {int(x):{'label':str(str(x) +'-' + str(str(int(x)+1))[-2:]),'style':{'transform':'rotate(-45deg)', 'font-size':'10px'}} for x in range(min_seas, max_seas+1)}

#slider values
@app.callback(Output("slider", 'value'),
              Input("player-input", "value"))
def generate_slider_values(player):

    slider_df = df[df['full_name'] == player]

    max_seas=slider_df['season'].max()
    min_seas=slider_df['season'].min()

    return [min_seas, max_seas]

#Make scatterplot
@app.callback(Output("histogram-output-container", 'figure'),
              Input('xaxis-column', 'value'),
              Input('yaxis-column', 'value'),
              Input("player-input", "value"),
              Input("slider", 'value'))
def generate_scatterplot(xcol, ycol, player, seas_vals):

    try:
        #graph_df_seas = df[(df['full_name'] == player) & (df['season'] >= seas_vals[0]) & (df['season'] <= seas_vals[1])]
        ovall_df = df[(df['season'] >= seas_vals[0]) & (df['season'] <= seas_vals[1])]
    
    except:
        #graph_df_seas = df[(df['full_name'] == player)]
        ovall_df = df.copy()

    ovall_df = ovall_df.groupby('full_name').agg({
        xcol:np.median,
        ycol:np.median
    })

    ovall_df['player_color'] = df.groupby('full_name')['tm_colors'].agg(pd.Series.mode)
    ovall_df['team'] = df.groupby('full_name')['player_tm'].agg(pd.Series.mode)
    ovall_df['team'] = ovall_df['team'].apply(lambda x: x if isinstance(x, str) else x[0])

    ovall_df.reset_index(inplace=True)

    player_df = ovall_df[ovall_df['full_name'] == player]
    #seas = str(graph_df['season'].min()) + " to " + str(int(graph_df['season'].max()) + 1)

    fig = px.scatter(ovall_df, x=xcol, y=ycol, color='team', hover_name="full_name", template='plotly_white',
        color_discrete_map=team_primary_colors, opacity=0.3, labels={
            "pts":"Points",
            "plus_minus":"Plus Minus",
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
            "blk":"Blocks",
            "wl":"Wins & Losses",
            "team":"Team"
    })


    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=player_df[xcol],
            y=player_df[ycol],
            marker=dict(
                color=team_primary_colors[player_df['team'].iloc[0]],
                size=10,
                line=dict(
                    color='black',
                    width=2
                )
            ),
            hovertemplate =f"<b>{player}</b><br>"+
            '<br>'+
        f"{col_dict_labels[xcol]}"+': %{x}'+
        f"<br>{col_dict_labels[ycol]}"+': %{y}',
        name=""
        )
    )

    return fig

#Make 1st line chart
@app.callback(Output("linechart1-output-container", 'figure'),
              Input('xaxis-column', 'value'),
              Input('yaxis-column', 'value'),
              Input("player-input", "value"),
              Input("slider", 'value'))
def generate_linechart_1(xcol, ycol, player, seas_vals):

    lc_df = df[df['full_name'] == player].copy()
    lc_df['Game Number'] = [f"Game {x+1}" for x in range(lc_df.shape[0])]
    lc_df['season'] = lc_df['season'].apply(lambda x: str(x)+"-"+str(x+1)[-2:])

    player_df= df.copy()
    player_df['game_num'] = player_df.groupby('full_name').cumcount()+1
    player_df['Game Number'] = player_df['game_num'].apply(lambda x: f"Game {x}")
    player_df = player_df.groupby('Game Number')[xcol].mean().reset_index()
    player_df.rename(columns={xcol:str(xcol)+"_league"}, inplace=True)

    lc_df = lc_df.merge(player_df, how='inner', on='Game Number')
    lc_df[str(xcol)+"_relative"] = lc_df[xcol] - lc_df[str(xcol)+"_league"]

    fig = px.bar(lc_df, x="Game Number", y=str(xcol)+'_relative', template="plotly_white", color_discrete_map={'W':"#17408B",
                                                                                                           'L':'#C9082A'}, color='wl',
            category_orders={'Game Number':[f"Game {str(x+1)}" for x in range(lc_df.shape[0])]},
            labels={
            "pts":"Points",
            "pts_relative":"Points",
            "plus_minus":"Plus Minus",
            "plus_minus_relative":"Plus Minus",
            "fg_pct":"FG%",
            "fg_pct_relative":"FG%",
            "reb":"Rebounds",
            "reb_relative":"Rebounds",
            "oreb":"Offensive Rebounds",
            "oreb_relative":"Offensive Rebounds",
            "dreb":"Defensive Rebounds",
            "dreb_relative":"Defensive Rebounds",
            "ast":"Assists",
            "ast_relative":"Assists",
            "fg3a":"3pt Attempts",
            "fg3a_relative":"3pt Attempts",
            "fg3m":"3pt Makes",
            "fg3m_relative":"3pt Makes",
            "fg3_pct":"3pt %",
            "fg3_pct_relative":"3pt %",
            "true_shooting":"True Shooting %",
            "true_shooting_relative":"True Shooting %",
            "tov_perc":"Turnover %",
            "tov_perc_relative":"Turnover %",
            "eff_fg_perc":"Effective FG%",
            "eff_fg_perc_relative":"Effective FG%",
            "stl":"Steals",
            "stl_relative":"Steals",
            "blk":"Blocks",
            "blk_relative":"Blocks",
            "wl":"Wins & Losses",
            "team":"Team"
    }, hover_name = 'Game Number')

    fig.update_xaxes(showticklabels=False)

    return fig

#Make 1st line chart
@app.callback(Output("linechart2-output-container", 'figure'),
              Input('xaxis-column', 'value'),
              Input('yaxis-column', 'value'),
              Input("player-input", "value"),
              Input("slider", 'value'))
def generate_linechart_2(xcol, ycol, player, seas_vals):

    lc_df = df[df['full_name'] == player].copy()
    lc_df['Game Number'] = [f"Game {x+1}" for x in range(lc_df.shape[0])]
    lc_df['season'] = lc_df['season'].apply(lambda x: str(x)+"-"+str(x+1)[-2:])

    player_df= df.copy()
    player_df['game_num'] = player_df.groupby('full_name').cumcount()+1
    player_df['Game Number'] = player_df['game_num'].apply(lambda x: f"Game {x}")
    player_df = player_df.groupby('Game Number')[ycol].mean().reset_index()
    player_df.rename(columns={ycol:str(ycol)+"_league"}, inplace=True)

    lc_df = lc_df.merge(player_df, how='inner', on='Game Number')
    lc_df[str(ycol)+"_relative"] = lc_df[ycol] - lc_df[str(ycol)+"_league"]

    fig = px.bar(lc_df, x="Game Number", y=str(ycol)+'_relative', template="plotly_white", color_discrete_map={'W':"#17408B",
                                                                                                           'L':'#C9082A'}, color='wl',
            category_orders={'Game Number':[f"Game {str(x+1)}" for x in range(lc_df.shape[0])]},
            labels={
            "pts":"Points",
            "pts_relative":"Points",
            "plus_minus":"Plus Minus",
            "plus_minus_relative":"Plus Minus",
            "fg_pct":"FG%",
            "fg_pct_relative":"FG%",
            "reb":"Rebounds",
            "reb_relative":"Rebounds",
            "oreb":"Offensive Rebounds",
            "oreb_relative":"Offensive Rebounds",
            "dreb":"Defensive Rebounds",
            "dreb_relative":"Defensive Rebounds",
            "ast":"Assists",
            "ast_relative":"Assists",
            "fg3a":"3pt Attempts",
            "fg3a_relative":"3pt Attempts",
            "fg3m":"3pt Makes",
            "fg3m_relative":"3pt Makes",
            "fg3_pct":"3pt %",
            "fg3_pct_relative":"3pt %",
            "true_shooting":"True Shooting %",
            "true_shooting_relative":"True Shooting %",
            "tov_perc":"Turnover %",
            "tov_perc_relative":"Turnover %",
            "eff_fg_perc":"Effective FG%",
            "eff_fg_perc_relative":"Effective FG%",
            "stl":"Steals",
            "stl_relative":"Steals",
            "blk":"Blocks",
            "blk_relative":"Blocks",
            "wl":"Wins & Losses",
            "team":"Team"
    }, hover_name = 'Game Number')

    fig.update_xaxes(showticklabels=False)

    return fig

#Make histogram
# @app.callback(Output("histogram-output-container", 'figure'),
#               Input('xaxis-column', 'value'),
#               Input("player-input", "value"),
#               Input("slider", 'value'))
# def generate_histogram(col, player, seas_vals):

#     try:
#         graph_df = df[(df['full_name'] == player) & (df['season'] >= seas_vals[0]) & (df['season'] <= seas_vals[1])]
#     except:
#         graph_df = df[(df['full_name'] == player)]

#     color1 = eval(graph_df['tm_colors'].unique()[0])[0]
#     color2 = eval(graph_df['tm_colors'].unique()[0])[1]

#     hist = px.histogram(graph_df, x=col, width = 1000,
#                         color = 'wl', labels={
#             "pts":"Points",
#             "plus_minus":"Plus Minus",
#             "fg_pct":"FG%",
#             "reb":"Rebounds",
#             "oreb":"Offensive Rebounds",
#             "dreb":"Defensive Rebounds",
#             "ast":"Assists",
#             "fg3a":"3pt Attempts",
#             "fg3m":"3pt Makes",
#             "fg3_pct":"3pt %",
#             "true_shooting":"True Shooting %",
#             "tov_perc":"Turnover %",
#             "eff_fg_perc":"Effective FG%",
#             "stl":"Steals",
#             "blk":"Blocks",
#             "wl":"Wins & Losses"
#     },
#     histnorm='percent',
#     color_discrete_map={ # replaces default color mapping by value
#                 "W": color1, "L": color2
#             }
#     )

#     hist.update_layout({
#         'plot_bgcolor':'rgba(0, 0, 0, 0)',
#         'yaxis_title':'Percentage of Games'
#     })

#     return hist

if __name__ == "__main__":
    app.run_server(debug=True, port=8888)