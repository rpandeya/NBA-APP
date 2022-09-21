# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 22:08:03 2022

@author: rpand
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#Read in Data

@st.cache
def load_data():
    player_data = pd.read_csv('Player Data.csv')
    
    offence_data = pd.read_csv('Offence Data.csv').drop_duplicates('PLAYER_NAME')
    
    defence_data = pd.read_csv('Defence Data.csv').drop_duplicates('PLAYER_NAME')
    
    off_percentile = pd.read_csv('off_percentiles.csv')
    def_percentile = pd.read_csv('def_percentiles.csv')
    
    off_percentile = off_percentile.drop(['Misc PPP Rank', 'Misc FREQ Rank', "Total Poss Rank", 'POTENTIAL_AST Rank','PULL_UP_FG3_PCT Rank', 'CATCH_SHOOT_FG_PCT Rank' ], axis='columns')
    
    
    def_cluster_data = pd.read_csv('Defence Cluster Data.csv')
    
    off_cluster_data = pd.read_csv('Offence Cluster Data.csv')
    
    league_avg_off = pd.read_csv('Offence League Average.csv')
    
    league_avg_def = pd.read_csv('Defence League Average.csv')
    
    return(player_data, offence_data, off_percentile, def_percentile, off_cluster_data, league_avg_off, defence_data,def_cluster_data, league_avg_def)

player_data, offence_data, off_percentile, def_percentile, off_cluster_data, league_avg_off, defence_data,def_cluster_data, league_avg_def = load_data()
#Some important lists

playtypes = ['Cut',
	'Handoff',
	'Isolation',
 	'OffScreen',
 	'Postup',
	'PRBallHandler',
 	'PRRollman',
 	'OffRebound',
 	'Spotup',
 	'Transition']

def_freq = [col for col in defence_data.columns if 'FREQ' in col]

def_stats = [col for col in defence_data.columns if 'PPP' in col]

def_stats = def_stats + ['PLUSMINUS Less Than 6Ft','PLUSMINUS Less Than 10Ft', 'PCT_LOOSE_BALLS_RECOVERED_DEF',
'REB_CONTEST_PCT', 'AVG_REB_DIST', 'DIST_MILES_DEF', 'AVG_SPEED_DEF',
'DEFLECTIONS Per36']

offence_freq = [col for col in offence_data.columns if "FREQ" in col]

offence_ppp =  [col for col in offence_data.columns if "PPP" in col]

offence_freq_perc = [col for col in off_percentile.columns if "FREQ" in col]

offence_ppp_perc = [col for col in off_percentile.columns if "PPP" in col]

defence_freq_perc = [col for col in def_percentile.columns if "FREQ" in col]

defence_stat_perc = [col for col in def_percentile.columns if "PPP" in col]

defence_stat_perc = defence_stat_perc + ['PLUSMINUS 3 Pointers Rank','PLUSMINUS Less Than 6Ft Rank', 'PLUSMINUS Less Than 10Ft Rank','PCT_LOOSE_BALLS_RECOVERED_DEF Rank', 'REB_CONTEST_PCT Rank',
'AVG_REB_DIST Rank', 'DIST_MILES_DEF Rank', 'AVG_SPEED_DEF Rank',
'DEFLECTIONS Per36 Rank']



playtypes_freq = [x + ' FREQ' for x in playtypes]

playtypes_freq.append('USG_PCT')

offence_freq.append('USG_PCT')

players = player_data.PLAYER_NAME.values.tolist()

shot_spectrum = ['Restricted Area FREQ','In The Paint (Non-RA) FREQ', 'Mid-Range FREQ', '3P FREQ']



players = list(set(players))

default_idx = players.index('Jimmy Butler')
#Defining the Functions for the App



def cluster_percentiles(df, player):
    
   percentiles = df.copy()




   for i in df.columns[2:]:
       percentiles[i + ' Rank'] = percentiles[i].rank(pct=True)
    
   percentiles = percentiles.drop(df.columns[2:], axis=1)
   percentiles = percentiles[percentiles['PLAYER_NAME']==player]
   
   return percentiles





def slice_data(player):
    
    
    player_offence = offence_data[offence_data['PLAYER_NAME']==player]
        
    player_defence = defence_data[defence_data['PLAYER_NAME']==player]
    
    off_cluster  = player_offence['Cluster'].values[0]
    
    def_cluster = player_defence['Cluster'].values[0]
    
    offence_cluster = off_cluster_data[off_cluster_data['Clusters']==off_cluster]
    
    total_offence_cluster = offence_data[offence_data['Cluster']==off_cluster]
    
    defence_cluster = def_cluster_data[def_cluster_data['Cluster']==def_cluster]
    
    total_defence_cluster = defence_data[defence_data['Cluster']==def_cluster]
    
    return(player_offence, offence_cluster, total_offence_cluster, player_defence, defence_cluster, total_defence_cluster)



def draw_bar(player_data,cluster_data,league_data, col_list,perc_col_list, player,league_percentile= None,total_cluster=None, league = True, perc= False, title = ''):
    
    
        
   
    
    
    cluster_data_plt = cluster_data[col_list].values.tolist()[0]
    league_data_plt = league_data[col_list].values.tolist()[0]
    player_data_plt = player_data[col_list].values.tolist()[0]
    
    
    if perc:
        
        clust_percentile = cluster_percentiles(total_cluster, player)
        
        league_perc_plt = league_percentile[perc_col_list].values.tolist()[0]
        clust_perc_plt = clust_percentile[perc_col_list].values.tolist()[0]
        
        
       
        fig = go.Figure(data=[
        
        go.Bar(name='Archetype Percentile', x=col_list,
               y=clust_perc_plt),
         
               go.Bar(name= 'League Percentile', x=col_list,
               y=league_perc_plt)
             ])
        fig.update_yaxes(title_text = 'Percentile', showticklabels=False)
        
            
    else:
        
        if league:
            fig = go.Figure(data=[
            
            go.Bar(name='Archetype', x=col_list,
                   y=cluster_data_plt),
                go.Bar (name=player , x=col_list,
                   y=player_data_plt),
                   go.Bar(name= 'League', x=col_list,
                   y=league_data_plt)
                 ])
        
            
            
        
        else:
            
            fig = go.Figure(data=[
            
            go.Bar(name='Archetype', x=col_list,
                   y=cluster_data_plt),
            
                   go.Bar(name=player , x=col_list,
                   y=player_data_plt)
                   
            ])
            # Change the bar mode
            fig.update_layout(barmode='group')
        
       
        fig.update_yaxes(title_text = 'Value', showticklabels=False)
    
        
    # Change the bar mode
    fig.update_layout(barmode='group',
                      legend=dict(
                          x = -0.004,
                          y=1,
                          
                    
            
            
        ))
    if title != '':
        fig.update_layout(title = dict(text = title))
        
    return fig

                    
       




def draw_pie(df, col_list, player):
    fig= go.Figure(data=[go.Pie(labels=col_list, values= df[col_list].values.tolist()[0], textinfo='label+percent',
                             
                            )])
    fig.update_traces(hoverinfo = 'skip')
    
    fig.update_layout(showlegend=False)
    return fig




  





    
