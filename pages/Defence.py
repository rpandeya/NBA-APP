# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 14:42:22 2022

@author: rpand
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from Functions import *




st.title('Defence')


st.header( 'Let\'s Get Started! ')

st.write('If any plots are cut-off, try closing the sidebar by clicking the \'x\' in the top right corner of the page menu.')

st.write('All plots can be expanded to full screen by selecting the arrows in the top-right corner of that plot.')
with st.form("NBA Player Select"):
    st.write("Please Select an NBA player!")
    player = st.selectbox('Player List',  players, default_idx)
    enter = st.form_submit_button('Enter')
    if enter :
        st.markdown(f'Analyzing: **{player}**')
        
    else:
        st.write('')
    st.write('')
    st.write('')


player_offence, clust_off, total_offence_cluster, player_defence, defence_cluster, total_defence_cluster = slice_data(player)

archetype = player_defence['Archetype'].values[0]




row0_spacer1, row0_1, row0_spacer2 = st.columns((.5, 3.2, .5))

with row0_1:
    
    st.title(f'{player}\'s Defensive Game')

row1_spacer1, row1_1, row1_spacer2 = st.columns((.5, 3.2, .5))



#Get Offensive Data#


row2_spacer1, row2_1, row2_spacer2 = st.columns((.5, 3.2, .5))

with row2_1:
    st.header(f'Analysis of {player}\'s Defensive Game ')
    
row3_spacer1, row3_1, row3_spacer2 = st.columns(3)

with row3_1:
    st.subheader(f'{player}\'s Archetype is: ')
    st.subheader(archetype)
    
    
    

row4_spacer1, row4_1, row2_spacer2 = st.columns((.5, 3.2, .5))

with row4_1:
    
    st.subheader(f'{player}\'s Defensive Playtype Frequency Compared to the League and their Archetype')
    league = st.checkbox('Show League Averages')
    dtype = st.checkbox('Show Percentiles')
    helper = st.expander('What do these mean?')
    with helper:
        st.write('Showing league averages shows the average frequencies of the defensive playtypes across all players.')
        st.write('Showing Percentiles will show the percentile ranking of the selected player within their archetype and the league.')
    st.write(draw_bar(player_defence, defence_cluster, league_avg_def,def_freq,defence_freq_perc, player,def_percentile, total_defence_cluster, league, dtype))
    
    


    
row5_spacer1, row5_1, row5_spacer2 = st.columns((.5, 3.2, .5))

with row5_1:
    
    st.subheader(f' How {player}\'s game compares to league average and their archetype\'s average')
    league_ppp = st.checkbox('Show League Average Defence Stats')
    dtype_ppp = st.checkbox('Show Defence Stats Percentiles')
    helper_ppp = st.expander('What do these mean?')
    with helper_ppp:
        st.write('Showing league averages shows the average stats of the playtypes across all players.')
        st.write('Showing Percentiles will show the percentile ranking of the selected player within their archetype and the league.')
    st.write(draw_bar(player_defence, defence_cluster, league_avg_def,def_stats,defence_stat_perc, player,def_percentile, total_defence_cluster, league_ppp, dtype_ppp))
    
