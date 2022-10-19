# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 14:48:48 2022

@author: rpand
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



st.set_page_config(layout='wide')

st.title('NBA Player Analysis')

st.markdown('Welcome! This app is designed to show detailed information about an NBA player of your choice from 2021-2022.')

st.markdown('Navigate to either Offence or Defence and select an NBA player to begin!')

st.markdown('For a description of an archetype, go to the page entitled \'Archetypes\'')

st.markdown('Check out the \'About\' page for details of this App and its functionalities.')

        


# Get Offence Data








