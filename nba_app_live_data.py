# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 23:51:31 2022

@author: rpand
"""

from nba_api.stats.endpoints import boxscoretraditionalv2 as boxscore, leagueleaders as ll, leaguegamelog, boxscorefourfactorsv2 as ff, playerdashptreb as rebounds
from nba_api.stats.endpoints import playercareerstats as player_career, draftcombinestats as combine, leaguehustlestatsplayer as hustle, commonteamroster as roster
from nba_api.stats.endpoints import synergyplaytypes as synergy_types, playerprofilev2 as player_profile
from nba_api.stats.static import teams, players
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, leaguedashplayershotlocations as shot_chart, leaguedashteamptshot as teamshot, leaguedashptdefend as defence
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc, plot_roc_curve, accuracy_score, recall_score, precision_score, silhouette_samples, silhouette_score
import requests
import warnings
import plotly.express as px
import plotly.graph_objects as go
import itertools
from sklearn.decomposition import PCA
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer
from sklearn.cluster import AgglomerativeClustering, KMeans, dbscan
from sklearn.mixture import GaussianMixture
import os



def get_player_hustle(start_szn = '2022-23', end_szn='2022-23', min_games = 0, min_mins = 0):
    hustle_stats = hustle.LeagueHustleStatsPlayer(per_mode_time='PerGame', season = start_szn, season_type_all_star='Regular Season')
    hustle_df = hustle_stats.get_data_frames()[0]
    hustle_df = hustle_df[(hustle_df['G']>min_games) & (hustle_df['DEFLECTIONS']>0)&(hustle_df['CONTESTED_SHOTS_3PT']>0) & (hustle_df['MIN']>min_mins)]
    start_year = int(start_szn[0:4])
    end_year = int('20'+end_szn[5:])
    

    current_szn = start_szn
    hustle_df['Season'] = [current_szn]*len(hustle_df)
    for i in range(start_year,end_year-1):
        current_szn =  str(int(current_szn[0:4]) +1) +'-'+ str(int(current_szn[5:])+1)
        print(current_szn)
        hustle_stats = hustle.LeagueHustleStatsPlayer(per_mode_time='PerGame', season = current_szn, season_type_all_star='Regular Season')
        temp = hustle_stats.get_data_frames()[0]
        temp = temp[(temp['G']>min_games)& (temp['DEFLECTIONS']>0)&(temp['CONTESTED_SHOTS_3PT']>0) & (temp['MIN']>min_mins)]
        temp['Season'] = [current_szn]*len(temp)
        hustle_df = pd.concat([hustle_df,temp], axis=0, ignore_index=True)
    return hustle_df


def get_defence(shot_type, start_szn = '2022-23', end_szn='2022-23', min_games = 0, min_mins = 0):
    
    defence_df = defence.LeagueDashPtDefend(defense_category=shot_type, league_id='00', season = start_szn, season_type_all_star='Regular Season', per_mode_simple='PerGame').get_data_frames()[0]
    start_year = int(start_szn[0:4])
    end_year = int('20'+end_szn[5:])
   
    current_szn = start_szn
    defence_df['Season'] = [current_szn]*len(defence_df)
    for i in range(start_year,end_year-1):
        current_szn =  str(int(current_szn[0:4]) +1) +'-'+ str(int(current_szn[5:])+1)
        temp = defence.LeagueDashPtDefend(defense_category= shot_type, league_id='00', season = current_szn, season_type_all_star='Regular Season', per_mode_simple='PerGame').get_data_frames()[0]
        temp['Season'] = [current_szn]*len(temp)
        defence_df = pd.concat([defence_df,temp], axis=0, ignore_index=True)
    return defence_df

playtypes = np.array(('Cut',
	'Handoff',
	'Isolation',
	'Misc',
 	'OffScreen',
 	'Postup',
	'PRBallHandler',
 	'PRRollman',
 	'OffRebound',
 	'Spotup',
 	'Transition'))


def synergy_data(playtypes, grouping, szn_year):
    data = {}
    for i in playtypes:
       
        # Under the Header tab, select general and copy the first part of the request URL
        url = 'https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode=PerGame&PlayType='+i+'&PlayerOrTeam=P&SeasonType=Regular Season&SeasonYear='+szn_year+'&TypeGrouping='+grouping
        #Header Tab, under "Query String Parameter" subsection
        
        # Header tab, under “Request Headers” subsection
        header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'Host': 'stats.nba.com',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',

        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true'}
        #Using Request library to get the data
        response = requests.get(url, headers=header)
        response_json = response.json()
        frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
        frame.columns = response_json['resultSets'][0]['headers']
        frame['Season'] = szn_year
        data[i] = frame
        
    for i in data.keys():

        data[i].sort_values(by = 'POSS_PCT', ascending = False)
        data[i] = data[i].rename({'PERCENTILE': 'PPP PERCENTILE'}, axis='columns')
        data[i]['POSS PCT PERCENTILE'] = data[i]['POSS_PCT'].rank(pct = True)

    return data

def basic_stats(szn_year, type='Base'):
    url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2021-22&SeasonSegment=&SeasonType=Regular Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='  
    url = url.replace('2021-22', szn_year)
    url = url.replace('Base', type)
    # Header tab, under “Request Headers” subsection
    header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',

    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'}
    #Using Request library to get the data
    response = requests.get(url, headers=header)
    response_json = response.json()
    frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    frame.columns = response_json['resultSets'][0]['headers']
    frame['Season'] = szn_year
    return frame


def distance(szn_year):
    # Under the Header tab, select general and copy the first part of the request URL
    #Header Tab, under "Query String Parameter" subsection
    url = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=SpeedDistance&Season={szn_year}&SeasonSegment=&SeasonType=Regular Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='   
    # Header tab, under “Request Headers” subsection
    header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',

    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'}
    #Using Request library to get the data
    response = requests.get(url, headers=header)
    response_json = response.json()
    frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    frame.columns = response_json['resultSets'][0]['headers']
    frame['Season'] = szn_year
    return frame

def dreb_tracking(szn_year):
    # Under the Header tab, select general and copy the first part of the request URL
    #Header Tab, under "Query String Parameter" subsection
    url = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Rebounding&Season={szn_year}&SeasonSegment=&SeasonType=Regular Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='   
    # Header tab, under “Request Headers” subsection
    header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',

    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'}
    #Using Request library to get the data
    response = requests.get(url, headers=header)
    response_json = response.json()
    frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    frame.columns = response_json['resultSets'][0]['headers']
    frame['Season'] = szn_year
    return frame



def shot_tracking(szn_year, category):
    
    url = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Drives&Season=2021-22&SeasonSegment=&SeasonType=Regular Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
    
    url = url.replace('2021-22', szn_year)
    url= url.replace('Drives', category)
    # Under the Header tab, select general and copy the first part of the request URL
    
    # Header tab, under “Request Headers” subsection
    header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',

    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'}
    #Using Request library to get the data
    response = requests.get(url, headers=header)
    response_json = response.json()
    frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    frame.columns = response_json['resultSets'][0]['headers']
    frame['Season'] = szn_year
    
        
    

    return frame


hustle_df_current = get_player_hustle('2022-23')

for i in ('DEFLECTIONS', 'CONTESTED_SHOTS_3PT', "CONTESTED_SHOTS_2PT"):
    colname = i + ' '+'Percentile'
    hustle_df_current[colname] = hustle_df_current[i].rank(pct = True)

shot_areas = ( '3 Pointers', 'Less Than 6Ft','Less Than 10Ft')

def get_shot_areas(areas):

    dfs = {}
    for area in areas:
        area_df = get_defence(area, '2022-23')
       
        dfs[area] = area_df
        
        print(f'done {area}')
    return dfs

def_shot_dfs = get_shot_areas(shot_areas)

shots_dfs = {}
for i in shot_areas:
    shots_dfs[i] = def_shot_dfs[i]
    shots_dfs[i] = shots_dfs[i].iloc[:,[1,3,6,7,8,9,10,11,12,13,14]].copy()
    shots_dfs[i] = shots_dfs[i].rename({'FREQ': 'FREQ'+' '+i, 'PLUSMINUS': 'PLUSMINUS' + ' ' + i, 'PLAYER_LAST_TEAM_ABBREVIATION': 'TEAM_ABBREVIATION'}, axis='columns')

full_shot_df = pd.merge(shots_dfs['3 Pointers'], shots_dfs['Less Than 6Ft'], how='inner', on=['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION'])
full_shot_df = pd.merge(full_shot_df, shots_dfs['Less Than 10Ft'], how='inner', on = ['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION'])


drives = shot_tracking('2022-23', 'Drives')

pullup = shot_tracking('2022-23', 'PullUpShot')

passing = shot_tracking('2022-23', 'Passing')

catch_shoot = shot_tracking('2022-23', 'CatchShoot')

full_shot_df_final = full_shot_df[['PLAYER_NAME', 'TEAM_ABBREVIATION','Season', 'FREQ 3 Pointers', 'PLUSMINUS 3 Pointers', 'FREQ Less Than 6Ft','PLUSMINUS Less Than 6Ft',
'FREQ Less Than 10Ft', 'PLUSMINUS Less Than 10Ft']]

drives = shot_tracking('2021-22', 'Drives')

pullup = shot_tracking('2021-22', 'PullUpShot')

passing = shot_tracking('2021-22', 'Passing')

catch_shoot = shot_tracking('2021-22', 'CatchShoot')

passing = passing[['PLAYER_NAME', 'TEAM_ABBREVIATION','POTENTIAL_AST', 'Season']].copy()

pullup = pullup[['PLAYER_NAME', 'TEAM_ABBREVIATION','PULL_UP_FGA', 'PULL_UP_FG3_PCT', 'Season']].copy()

drives = drives[['PLAYER_NAME', 'TEAM_ABBREVIATION','DRIVES', 'DRIVE_PASSES_PCT','Season']].copy()

catch_shoot = catch_shoot[['PLAYER_NAME','TEAM_ABBREVIATION','CATCH_SHOOT_FG_PCT','CATCH_SHOOT_FGA','Season' ]].copy()

player_basic = basic_stats('2022-23')

player_advanced = basic_stats('2021-23', 'Advanced')

player_basic = player_basic[['PLAYER_NAME','TEAM_ABBREVIATION', 'FGA', 'FG3A']]

player_advanced = player_advanced[['PLAYER_NAME','TEAM_ABBREVIATION' ,'USG_PCT']]

shot_data = shot_chart.LeagueDashPlayerShotLocations(distance_range='By Zone', season_type_all_star='Regular Season',per_mode_detailed='PerGame' )
shot_df = shot_data.get_data_frames()[0]

shot_df = shot_df[['','Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range']]
player_names = shot_df[('', 'PLAYER_NAME')].values
team_abb = shot_df[('', 'TEAM_ABBREVIATION')].values

area_fga = {}

for area in ('Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range'):
    
    area_fga[area + ' FGA'] = shot_df[(area, 'FGA')].values
    
twos_breakdown = pd.DataFrame(area_fga)

twos_breakdown['2PA'] = twos_breakdown.sum(axis=1)

twos_breakdown['PLAYER_NAME'] = player_names

twos_breakdown['TEAM_ABBREVIATION'] = team_abb


full_shot_pass = passing

full_shot_pass = passing.drop(['TEAM_ID', 'GP', 'MIN', 'PLAYER_ID', 'W', 'L'], axis=1)

for df in (drives, pullup, catch_shoot):
    full_shot_pass = pd.merge(full_shot_pass, df, how = 'inner', on = ['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION'])
full_shot_pass = pd.merge(full_shot_pass, twos_breakdown, on = ['PLAYER_NAME',  'TEAM_ABBREVIATION'] ,how='inner')
full_shot_pass = pd.merge(full_shot_pass, player_basic, how='inner', on = ['PLAYER_NAME',  'TEAM_ABBREVIATION'])
full_shot_pass = pd.merge(full_shot_pass, player_advanced, how='inner', on = ['PLAYER_NAME',  'TEAM_ABBREVIATION'])



current_offence = synergy_data(playtypes, 'offensive', '2022-23')

for i in current_offence.keys():
    current_offence[i]= current_offence[i].rename({'PPP': i + ' PPP', 'POSS': i + ' POSS', 'POSS_PCT': i+' FREQ'}, axis='columns')
    current_offence[i] = current_offence[i][['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION',i + ' PPP',  i + ' FREQ',i + ' POSS','GP']]
    

all_offence = pd.merge(current_offence['Cut'], current_offence['Handoff'], how = 'outer', on=['PLAYER_NAME', 'Season','GP', 'TEAM_ABBREVIATION'])

for i in range(2, len(current_offence.keys())):
    key = list(current_offence.keys())[i]
    all_offence = pd.merge(all_offence, current_offence[key], how = 'outer', on=['PLAYER_NAME', 'Season', 'GP', 'TEAM_ABBREVIATION'])
    
all_offence = all_offence.drop_duplicates(['PLAYER_NAME', 'Season', 'GP', 'TEAM_ABBREVIATION'])


poss_cols = [i + ' POSS' for i in current_offence.keys()]
all_offence['Total Poss'] = all_offence[poss_cols].sum(axis=1)
all_offence = all_offence.drop(poss_cols, axis='columns')


all_offence = pd.merge(all_offence, hustle_df_current[['PLAYER_NAME',  "MIN", "Season", "TEAM_ABBREVIATION"]], on = ['PLAYER_NAME', 'Season',"TEAM_ABBREVIATION"], how='inner')

all_offence = pd.merge(all_offence, full_shot_pass, on = ['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION'], how='inner')

all_offence = all_offence.fillna(0)

all_offence = all_offence.drop_duplicates(['PLAYER_NAME', 'Season', 'TEAM_ABBREVIATION'])

all_offence['POTENTIAL_AST FREQ'] = all_offence['POTENTIAL_AST']/all_offence['Total Poss']


for area in ('Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range'):
    all_offence[area + ' FREQ'] = all_offence[area+ ' FGA']/all_offence['2PA']
    all_offence = all_offence.drop(area+' FGA', axis=1)


all_offence['3P FREQ'] = all_offence['FG3A']/all_offence['FGA']

all_offence['Drives FREQ'] = all_offence['DRIVES']/all_offence['Total Poss']


for area in ('PULL_UP', 'CATCH_SHOOT'):
    all_offence[area + ' FREQ'] = all_offence[area+ '_FGA']/all_offence['FGA']
    all_offence = all_offence.drop(area+'_FGA', axis=1)

all_offence = all_offence.drop(['DRIVES', '2PA', 'FGA' ], axis=1)


