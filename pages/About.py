# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 21:41:17 2022

@author: rpand
"""

import streamlit as st

st.title('About')


exp1 = st.expander('What is the point of this app?')

with exp1:
    st.write('The point of this app is to help understand an NBA player\'s game in the context of the league.')
    st.write('An archetype for their offensive and defensive styles will be given, but this should be taken within context, as not every player in an archetype is the same.')
    st.write('For that reason, the selected player\'s stats will be presented with the context of the league as a whole, and their peers within their specific archetype.' )
    st.write('This way, we can hopefully get a broad archetypal classification of a player and then use nuance to see their more specific style ')

exp2 = st.expander('What should I expect?')

with exp2:
    st.write('There will be a classification of this player, both for their offensive and defensive games.')
    
    st.write('This App will show statistics relevant to a player the user selects for offence and defence.')
    
    
    st.write('There will be graphs showing how this player stacks up to the rest of the league, and their specific archetype.')