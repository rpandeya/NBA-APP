# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 21:51:20 2022

@author: rpand
"""

import streamlit as st
import numpy as np
import pandas as pd


offence_archetypes = pd.read_csv('Offence Archetypes.csv')
defence_archetypes = pd.read_csv('Defensive Archetypes.csv')

st.title('Archetypes')

st.markdown('Here you can find a description of each archetype. Remember, these archetypes are broad, so the descriptions are based on the average player in each archetype.')


st.header('Offence')

with st.form('Please Choose an Offensive Archetype'):
    offence_archetype = st.selectbox('Offensive Archetypes', offence_archetypes.Archetype.values)
    enter = st.form_submit_button('Enter')
    
    
off_expander = st.expander('View Description')
    
with off_expander:
    st.header(offence_archetype)
    st.write(offence_archetypes[offence_archetypes['Archetype']== offence_archetype]['Description'].values[0])
    
    
st.header('Defence')

with st.form('Please Choose a Defensive Archetype'):
    defence_archetype = st.selectbox('Defensive Archetypes', defence_archetypes.Archetype.values)
    enter = st.form_submit_button('Enter')
    
    
def_expander = st.expander('View Description')
    
with def_expander:
    st.header(defence_archetype)
    st.write(defence_archetypes[defence_archetypes['Archetype']== defence_archetype]['Description'].values[0])