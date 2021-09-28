######################################
# Functions to ingest player data ####
######################################

import time
import nba_api as nba
import pandas as pd 
import numpy as np 

from nba_api.stats.endpoints import playercareerstats # Career Data
from nba_api.stats.endpoints import playergamelog # Game data
from nba_api.stats.endpoints import playerprofilev2 
from nba_api.stats.endpoints import playbyplayv2


from nba_api.stats.static import players, teams 

import bs4 as bs
import urllib.request

from os import path

# Function to get player ID

def get_playerID(name, verbose=False):

    """Get the playerID for a given player's full-name"""
    if verbose == True:
        print(f"Getting ID for {name}...")

    out_id = players.find_players_by_full_name(name)[0]
    if verbose == True:
        print(f"{out_id['full_name']} ID: {out_id['id']}")

    return out_id

# Function to get player's game by game for a given season and player

def get_gamebygame(player_id, season):

    games = playergamelog.PlayerGameLog(player_id=player_id, season=season)

    game_df = games.get_data_frames()[0]

    return game_df 

def get_player_gamebygame(playerName):

    """Given a string for a player, get all game by game data"""

    ID = get_playerID(playerName)

    name = ID['full_name']

    career_df = get_player_career(player_id=ID['id'])

    seasons = career_df['SEASON_ID'].unique()
    #print(seasons)
    output_df = pd.DataFrame()

    for season in seasons:
        print(f"Getting Data for {ID['full_name']}, Season: {season}")
        time.sleep(3)
        game = playergamelog.PlayerGameLog(player_id=ID['id'], season=season)

        df = game.get_data_frames()[0]

        output_df = output_df.append(df)

    output_df['player_name'] = name

    output_df['TM'] = output_df['MATCHUP'].apply(lambda x: x[0:3])
    output_df['OPP'] = output_df['MATCHUP'].apply(lambda x: x[-3:])
    output_df['HOME_AWAY'] = np.where(output_df['MATCHUP'].str.contains("@"), "AWAY", "HOME")

    output_df['MONTH'] = output_df['GAME_DATE'].apply(lambda x: x[0:3])
    output_df['YEAR'] = output_df['GAME_DATE'].apply(lambda x: x[-4:])
    output_df['DAY'] = output_df['GAME_DATE'].apply(lambda x: x[4:6])

    output_df = output_df.drop(columns=['SEASON_ID', 'Player_ID', 'Game_ID', 'MATCHUP', 'VIDEO_AVAILABLE', 'GAME_DATE'])

    return output_df

def get_player_career(player_id):

    career = playercareerstats.PlayerCareerStats(player_id=player_id)

    career_df = career.get_data_frames()[0]

    return career_df

def get_player_career_byname(player_name):

    ID = get_playerID(player_name)

    career_df = get_player_career(player_id=ID['id'])

    career_df['player_name'] = ID['full_name']

    return career_df

def get_playbyplay(game_id):

    """Get play by play data given a specific game ID """

    pbp = playbyplayv2.PlayByPlayV2(game_id = game_id, end_period=0)

    playbyplay_df = pbp.get_data_frames()[0]

    return playbyplay_df



def get_player_pic(player_name):

    full_name = str(player_name)
    fname = player_name.split()[0]
    lname = player_name.split()[1:]    
    lname = ' '.join(lname)

    url = "https://www.basketball-reference.com/players/"

    player_url = url + lname[0] + '/' + lname[:5]+fname[:2]+'01.html'

    try: 

        req = urllib.request.urlopen(player_url)
        soup = bs.BeautifulSoup(req)

        link = soup.find_all('img')[1].get('src')

    except:

        try:

            player_url = url + lname[0] + '/' + lname[:5]+fname[:2]+'02.html'

            req = urllib.request.urlopen(player_url)
            soup = bs.BeautifulSoup(req)

            link = soup.find_all('img')[1].get('src')

        except:

            return None

    return link

def calc_player_df_metrics(df):

    df['season'] = df['season_id'].apply(lambda x: int(str(x)[1:5]))

    df['game_date'] = pd.to_datetime(df['game_date'], format="%b %d, %Y")

    df['true_shooting'] = round(100*(df['pts'] / (2 * df['fga'] + (0.44 * df['fta']))))
    df['tov_perc'] = round(100*df['tov'] / df['fga'] + (0.44*df['fga']) + df['tov'])
    df['eff_fg_perc'] = round(100*(df['fgm'] + 0.5*df['fg3m']) / df['fga'])
    df['ast_tov_ratio'] = round(df['ast'] / df['tov'])

    return df


def get_save_player_pic(player_name):

    f_link = "assets/players/"+'-'.join(player_name.split())+'-pic.jpg'

    if path.exists(f_link):
        print(f"skipping: {f_link}")

        return f_link
    else:
        try:
            link = get_player_pic(player_name)

    # Save the image link to the assets folder
            urllib.request.urlretrieve(link, f_link)

        except:
            return "/assets/players/giannis-antetokoumpo-pic.jpg"

    if path.exists(f_link):

        return f_link

    else:

        return "/assets/players/giannis-antetokoumpo-pic.jpg"