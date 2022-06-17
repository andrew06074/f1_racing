from xml.dom.xmlbuilder import DOMEntityResolver
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

#gloal color list
colors = pd.read_csv('f1_colors.csv')

#function to load data
def load_data():
    #get data from page, clean for export
    url = 'https://www.formula1.com/en/results.html/2022/races.html'

    # Request content from web page
    result = requests.get(url)
    c = result.content

    # Set as Beautiful Soup Object
    soup = BeautifulSoup(c,'html.parser')
    tbl= soup.find("table",{'class':'resultsarchive-table'})
    data_frame1 = pd.read_html(str(tbl))[0]
    data_frame = pd.merge(data_frame1,colors,how='left',on='Car')
    #drop unnameds
    data_frame = data_frame.drop(['Unnamed: 0','Unnamed: 7'], 1)

    #covert race time to total seconds
    data_frame['race_time'] = data_frame['Time'].astype(str).str[:-4]
    data_frame[['Hours','Minuets','Secconds']] = data_frame['race_time'].str.split(':',expand=True)
    data_frame['total_secconds'] = (((data_frame['Hours'].astype(int) *60) *60) + (data_frame['Minuets'].astype(int)*60) + (data_frame['Secconds'].astype(int)))
    #create average laptime for each race
    data_frame['average_laptime'] = data_frame['total_secconds'] / data_frame['Laps']
    data_frame_for_vis = data_frame[['Grand Prix','Winner','Car','Laps','Time','average_laptime','Color']]
    data_frame_for_vis.columns = ['Grand Prix','Winner','Car','Laps','Time','Average Lap Time','Color']
    return data_frame_for_vis

def load_pts_data():
    url = 'https://www.formula1.com/en/results.html/2022/drivers.html'
     # Request content from web page
    result = requests.get(url)
    c = result.content

    # Set as Beautiful Soup Object
    soup = BeautifulSoup(c,'html.parser')
    tbl= soup.find("table",{'class':'resultsarchive-table'})
    data_frame1 = pd.read_html(str(tbl))[0]
    data_frame = pd.merge(data_frame1,colors,how='left',on='Car')
    #drop unnameds
    data_frame = data_frame.drop(['Unnamed: 0','Unnamed: 6'], 1)
    return data_frame

#call load data 
data_frame = load_data()
#call to load pts df
pts_df = load_pts_data() 

#page title and info
st.markdown("<h1 style='text-align: center; color: white;'>Welcome!</h1>", unsafe_allow_html=True)
st.write('This site directly queries the [formula 1 website](https://www.formula1.com/en/results.html) and returns the appropiate data for cleaning and visulization.' )
st.write('--------------------------------------')
st.markdown("<h3 style='text-align: center; color: white;'>2022 F1 Seasonal Overview</h3>", unsafe_allow_html=True)
options = ['Driver Overview','Team Overview','Race Overview']
select_scope = st.selectbox('Select a scope',options) 

def driver_page(data_frame):
    #create vis for drive and team results
    #get number of wins for each 'Winner'
    driver_df = data_frame['Winner'].value_counts().rename_axis('Winner').reset_index(name='Number of wins')
    #need a color connector
    color_con_df = data_frame[['Winner','Car','Color']].drop_duplicates()
    #merge count frame with color connector
    driver_df = pd.merge(driver_df,color_con_df,how='left',on='Winner')
    
    #create a color list for vis
    colors_list = driver_df['Color']
    #create vis
    fig = px.bar(driver_df, x="Winner", y="Number of wins",color='Winner',color_discrete_sequence=colors_list)
    fig.update_layout(showlegend=False,title_text='2022 Race Winners', title_x=0.5)
    st.plotly_chart(fig,use_container_width=True)

    #create vis for drivers and points
    standings_fig = px.bar(pts_df,x='Driver',y='PTS')
    st.plotly_chart(standings_fig,use_container_width=True)

def team_page(data_frame):
    #team vis
    #get number of wins for each 'Winner'
    team_df = data_frame['Car'].value_counts().rename_axis('Car').reset_index(name='Number of wins')
    #need a color connector
    color_con_df = data_frame[['Car','Color']].drop_duplicates()
    #merge count frame with color connector
    team_df = pd.merge(team_df,color_con_df,how='left',on='Car')
    #create a color list for vis
    colors_list = team_df['Color']
    #create vis
    team_fig = px.bar(team_df, x="Car", y="Number of wins",color='Car',color_discrete_sequence=colors_list)
    team_fig.update_layout(showlegend=False,title_text='2022 Team Wins', title_x=0.5)
    st.plotly_chart(team_fig,use_container_width=True)

def race_page(data_frame):
    #create vis for average laps
    lap_vis_df = data_frame[['Grand Prix','Average Lap Time']]
    lap_vis_df.columns = ['Race','Average laptime (seconds)']
    lap_vis_df = lap_vis_df.sort_values(by='Average laptime (seconds)',ascending=False)
    fig_avg_times = px.bar(lap_vis_df, y='Race', x='Average laptime (seconds)')
    fig_avg_times.update_layout(showlegend=False, title_x=0.5)
    fig_avg_times.update_traces(width=.5)

    total_laps = data_frame[['Grand Prix','Laps']]
    total_laps = total_laps.sort_values(by='Laps',ascending=False)
    total_laps.columns = ['Race','Total number of laps']
    fig_totallaps = px.bar(total_laps,y='Race',x='Total number of laps')
    fig_totallaps.update_traces(width=.5)
    
    time_df_for_fig = data_frame[['Grand Prix','Time']]
    time_df_for_fig.columns = ['Race','Time']
    time_df_for_fig['Time'] = pd.to_datetime(time_df_for_fig['Time'])
    time_df_for_fig = time_df_for_fig.sort_values(by='Time',ascending=True)
    time_fig = px.line(time_df_for_fig,x='Race',y='Time',markers=True)
    time_fig.update_layout(title_text='Race Duration', title_x=0.5)
    st.plotly_chart(time_fig, use_container_width=True)


    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_totallaps, use_container_width=True)
    with col2:
        st.plotly_chart(fig_avg_times, use_container_width=True)

   
    
    
if select_scope == 'Driver Overview':
    driver_page(data_frame)
elif select_scope  == 'Team Overview':
    team_page(data_frame)

elif select_scope == 'Race Overview':
    race_page(data_frame)



