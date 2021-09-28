import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from layouts import player_layout
from layouts import df, team_primary_colors, col_dict_labels, col_dict
from app import app
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go


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