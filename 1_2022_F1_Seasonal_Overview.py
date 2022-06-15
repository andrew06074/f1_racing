import pandas as pd
from scipy.misc import face
import  streamlit as st
import plotly.express as px

#libs for scraper
from bs4 import BeautifulSoup
import requests
import pandas as pd
import lxml
import numpy as np

import pages

st.markdown("<h1 style='text-align: center; color: white;'>Welcome!</h1>", unsafe_allow_html=True)
st.write('This site directly queries the [formula 1 website](https://www.formula1.com/en/results.html) and returns the appropiate data for cleaning and visulization.' )
st.write('--------------------------------------')
st.markdown("<h3 style='text-align: center; color: white;'>2022 F1 Seasonal Overview</h3>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: white;'>Race Results</h5>", unsafe_allow_html=True)

#get data from page, clean for export
url = 'https://www.formula1.com/en/results.html/2022/races.html'

# Request content from web page
result = requests.get(url)
c = result.content

# Set as Beautiful Soup Object
soup = BeautifulSoup(c,'html.parser')
tbl= soup.find("table",{'class':'resultsarchive-table'})
data_frame1 = pd.read_html(str(tbl))[0]

#merge color connector
colors = pd.read_csv('f1_colors.csv')
data_frame = pd.merge(data_frame1,colors,how='left',on='Car')
#drop unnameds
data_frame = data_frame.drop(['Unnamed: 0','Unnamed: 7'], 1)

#covert race time to total seconds
data_frame['race_time'] = data_frame['Time'].astype(str).str[:-4]
data_frame[['Hours','Minuets','Secconds']] = data_frame['race_time'].str.split(':',expand=True)
data_frame['total_secconds'] = (((data_frame['Hours'].astype(int) *60) *60) + (data_frame['Minuets'].astype(int)*60) + (data_frame['Secconds'].astype(int)))
#create average laptime for each race
data_frame['average_laptime'] = data_frame['total_secconds'] / data_frame['Laps']
st.write(data_frame)
