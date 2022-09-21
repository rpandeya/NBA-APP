import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from Functions import *



    
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

archetype = player_offence['Archetype'].values[0]




row0_spacer1, row0_1, row0_spacer2 = st.columns((.5, 3.2, .5))

with row0_1:
    
    st.title(f'{player}\'s Offensive Game')

row1_spacer1, row1_1, row1_spacer2 = st.columns((.5, 3.2, .5))



#Get Offensive Data#


row2_spacer1, row2_1, row2_spacer2 = st.columns((.5, 3.2, .5))

with row2_1:
    st.header(f'Analysis of {player}\'s Offensive Game ')
    
row3_spacer1, row3_1, row3_spacer2 = st.columns(3)

with row3_1:
    st.subheader(f'{player}\'s Archetype is: ')
    st.subheader(archetype)
    
    
    

row4_spacer1, row4_1, row2_spacer2 = st.columns((.5, 3.2, .5))

with row4_1:
    
    st.subheader(f'{player}\'s Offensive Playtype Frequency Compared to the League and their Archetype')
    league = st.checkbox('Show League Averages', value= True)
    dtype = st.checkbox('Show Percentiles')
    helper = st.expander('What do these mean?')
    with helper:
        st.write('Showing league averages shows the average frequencies of the playtypes across all players.')
        st.write('Showing Percentiles will show the percentile ranking of the selected player within their archetype and the league.')
    
    
    with st.form('Select Categories to be Plotted'):
        
        offence_cats = st.multiselect("Offence Categories to be Plotted (There are more than the default categories!!)", offence_freq, default = offence_freq[-7:])
        enter = st.form_submit_button('Enter')
        
    title_41 = f'How {player}\'s game compares to league average and their archetype\'s average'

    form_offence_freq_perc = [s + ' Rank' for s in offence_cats]
    st.write(draw_bar(player_offence, clust_off, league_avg_off,offence_cats,form_offence_freq_perc, player,off_percentile, total_offence_cluster, league, dtype, title= title_41))
    
    
row5_1, row5_2 = st.columns(2)

with row5_1:
    
    st.subheader(f'{player}\'s Offensive Playtpe Breakdown')
    st.write(draw_pie(player_offence,playtypes_freq[:-1],player ))
    
with row5_2:
    
    
    st.subheader(f'{player}\'s Offensive Shot-Area Breakdown')
    st.write(draw_pie(player_offence,shot_spectrum,player ))
    
row5_spacer1, row5_1, row5_spacer2 = st.columns((.5, 3.2, .5))

with row5_1:
    
    st.subheader(f' How {player}\'s game compares to league average and their archetype\'s average')
    league_ppp = st.checkbox('Show League Average PPP', value = True)
    dtype_ppp = st.checkbox('Show PPP Percentiles')
    helper_ppp = st.expander('What do these mean?')
    with helper_ppp:
        st.write('Showing league averages shows the average PPP of the playtypes across all players.')
        st.write('Showing Percentiles will show the PPP percentile ranking of the selected player within their archetype and the league.')
     
    with st.form('Select Offence PPP Categories to be Plotted'):
        offence_ppp_cats = st.multiselect("Offence PPP Categories to be Plotted", offence_ppp, default = offence_ppp)
        enter = st.form_submit_button('Enter')
         
    title_51 = f' How {player}\'s game compares to league average and their archetype\'s average'

    form_offence_ppp_perc = [s + ' Rank' for s in offence_ppp_cats]
    
    st.write(draw_bar(player_offence, clust_off, league_avg_off,offence_ppp_cats,form_offence_ppp_perc, player,off_percentile, total_offence_cluster, league_ppp, dtype_ppp, title = title_51))
    
