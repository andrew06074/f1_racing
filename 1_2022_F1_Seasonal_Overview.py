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
    data_frame['Winner'] = data_frame['Winner'].str[:-3]
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
    data_frame['Driver'] = data_frame['Driver'].str[:-3]
    return data_frame

def load_fast_lap_data():
    url = 'https://www.formula1.com/en/results.html/2022/fastest-laps.html'
    # Request content from web page
    result = requests.get(url)
    c = result.content

    # Set as Beautiful Soup Object
    soup = BeautifulSoup(c,'html.parser')
    tbl= soup.find("table",{'class':'resultsarchive-table'})
    data_frame1 = pd.read_html(str(tbl))[0]
    data_frame = pd.merge(data_frame1,colors,how='left',on='Car')
    #drop unnameds
    data_frame = data_frame[['Driver','Car']]
    return data_frame

def load_team_pts():
    url = 'https://www.formula1.com/en/results.html/2022/team.html'
    # Request content from web page
    result = requests.get(url)
    c = result.content
    # Set as Beautiful Soup Object
    soup = BeautifulSoup(c,'html.parser')
    tbl= soup.find("table",{'class':'resultsarchive-table'})
    #rename colors for connection
    colors.columns = ['Team','Color']
    data_frame1 = pd.read_html(str(tbl))[0]
    data_frame = pd.merge(data_frame1,colors,how='left',on='Team')
    #drop unnameds
    data_frame = data_frame[['Team','PTS']]
    return data_frame

#call load data 
data_frame = load_data()
#call to load pts df
pts_df = load_pts_data() 
#call fastlap df
fastlap_df = load_fast_lap_data()
#call team pts df
team_pts = load_team_pts()

if st.checkbox('Show hows its done: '):
    st.write('This site directly queries the [formula 1 website](https://www.formula1.com/en/results.html) and returns the appropiate data for cleaning and visulization.' )

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
    fig.update_layout(autosize=False,width=400, height=200,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),showlegend=False,title_text='Number of race wins', title_x=0.5,yaxis_title=None,xaxis_title=None)
    fig.update_traces(width=.5)

    #create vis for fastlap
    #preping vis data
    fastlap_df['Driver'] = fastlap_df['Driver'].str[:-3]
    fastlap_df.columns = ['Driver','Team']
    color_con_df = pd.merge(fastlap_df,colors,how='left',on='Team')
    color_con_df = color_con_df.drop_duplicates()
    fl_df = fastlap_df['Driver'].value_counts().rename_axis('Driver').reset_index(name='Number of fastest lap points')
    fl_df = pd.merge(fl_df,color_con_df,how='left',on='Driver')
    #creating fig
    fl_fig = px.bar(fl_df, x="Driver", y="Number of fastest lap points",color='Driver',color_discrete_sequence=fl_df['Color'])
    fl_fig.update_layout(autosize=False,width=400, height=200,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),showlegend=False,title_text='Points for fastest lap', title_x=0.5,yaxis_title=None,xaxis_title=None)
    fl_fig.update_traces(width=.5)

    #create vis for drivers and points
    colors_list = pts_df['Color']
    pts_df_local = pts_df[['Driver','PTS','Color']]
    pts_df_local.columns = ['Driver','Points','Color']
    standings_fig = px.bar(pts_df_local,y='Driver',x='Points',color='Driver',color_discrete_sequence=colors_list)
    standings_fig.update_layout(autosize=False,width=100, height=300,margin=dict(
        l=150,
        r=150,
        b=50,
        t=50,
        pad=4
    ),
    showlegend=False,yaxis_title=None,title_text='Points this season',title_x=0.5,xaxis_title=None)
    standings_fig.update_traces(width=1)
    st.plotly_chart(standings_fig,use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        st.plotly_chart(fl_fig,use_container_width=True)
    
        #create function to get link for avl data
    def get_races():
        f1_links = pd.read_csv('F1_Links.csv')
        return f1_links
    
    links = get_races()
    races = links['Race']

    #loop through all race start links to get df and append
    @st.cache
    def get_all_race_starts(links):
        append_starts = pd.DataFrame()
        quals = links[['Race','Qualifying']]
        for index, row in quals.iterrows():
            #get data for start
            start_url = row['Qualifying']
            # Request content from web page
            result = requests.get(start_url)
            c = result.content
            # Set as Beautiful Soup Object
            soup = BeautifulSoup(c,'html.parser')
            tbl= soup.find("table",{'class':'resultsarchive-table'})
            start_df = pd.read_html(str(tbl))[0]
            #cleaning data
            start_df = start_df[['Driver','Pos','Car']]
            start_df.columns = ['Driver','Start Position','Car']
            start_df['Race'] = row['Race']
            start_df['string_for_merge'] = start_df['Race'] + start_df['Driver']
            append_starts = append_starts.append(start_df)
        return append_starts

    #loop through all race result links to get df's and append
    @st.cache
    def get_all_race_results(links):
        append_results = pd.DataFrame()
        results = links[['Race','Race Results - HTML']]
        for index, row in results.iterrows():
            #get data for start
            results_url = row['Race Results - HTML']
            # Request content from web page
            result = requests.get(results_url)
            c = result.content

            # Set as Beautiful Soup Object
            soup = BeautifulSoup(c,'html.parser')
            tbl= soup.find("table",{'class':'resultsarchive-table'})
            results_df = pd.read_html(str(tbl))[0]
            #cleaning data
            results_df = results_df[['Driver','Pos','Car']]
            results_df.columns = ['Driver','Results Position','Car']
            results_df['Race'] = row['Race']
            results_df['string_for_merge'] = results_df['Race'] + results_df['Driver']
            append_results = append_results.append(results_df)
        return append_results
    
    
    all_starts = get_all_race_starts(links)
    all_results = get_all_race_results(links)
    all_results = all_results[['string_for_merge','Results Position']]
    
    merged = pd.merge(all_starts,all_results,on='string_for_merge',how='left')
    
    #clean merge
    df = merged[['Race','Driver','Car','Start Position','Results Position']]
    df['Driver'] = df['Driver'].str[:-4]
    #repalce nc's with 20
    df = df.replace('NC','20')
    #change datatypes
    df['Start Position'] = df['Start Position'].astype(int)
    df['Results Position'] = df['Results Position'].astype(int)
    #create change in results
    df['Change in position'] = df['Start Position'] - df['Results Position']

    season_pos_changes = df[['Driver','Car','Change in position']]

    driver_team_link = season_pos_changes[['Driver','Car']]
    driver_team_link = driver_team_link.drop_duplicates()

    def get_driver_change(season_pos_changes,driver_team_link):
        sorted_by_driver = season_pos_changes.groupby('Driver').sum()
        sorted_by_driver = sorted_by_driver.sort_values(by='Change in position',ascending=True)
        sorted_by_driver = pd.merge(sorted_by_driver,driver_team_link,how='left',on='Driver')
        colors = pd.read_csv('f1_colors.csv')
        sorted_by_driver = pd.merge(sorted_by_driver,colors,how='left',on='Car')
        import plotly.express as px
        colors_list = sorted_by_driver['Color']
        colors_list = colors_list.iloc[::-1]
        fig = px.bar(sorted_by_driver, x="Change in position", y="Driver", orientation='h',color='Driver',color_discrete_sequence=colors_list)
        fig.update_layout(yaxis={'categoryorder':'total ascending'},showlegend=False,title_text='Change in grid placement - Race start to finish', title_x=0.5,yaxis_title=None,xaxis_title=None)
        fig.update_traces(width=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write('')
    
    get_driver_change(season_pos_changes,driver_team_link)

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
    team_fig.update_layout(autosize=False,width=200, height=200,margin=dict(
        l=250,
        r=250,
        b=0,
        t=50,
        pad=4
    ),showlegend=False,title_text='Team Wins', title_x=0.5,yaxis_title=None,xaxis_title=None)
    team_fig.update_traces(width=.5)
    

    #team pts vis
    team_pts_df = pd.merge(team_pts,colors,how='left',on='Team')
    team_pts_df.columns = ['Team','Points','Color']
    team_pts_fig = px.bar(team_pts_df,y='Team',x='Points',color='Team',color_discrete_sequence=team_pts_df['Color'])
    team_pts_fig.update_layout(autosize=False,width=400, height=200,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),showlegend=False,yaxis_title=None,title_text='Points this season',title_x=0.5,xaxis_title=None)
    
    st.plotly_chart(team_pts_fig,use_container_width=True)
    st.plotly_chart(team_fig,use_container_width=True)

def race_page(data_frame):
    #create vis for average laps
    lap_vis_df = data_frame[['Grand Prix','Average Lap Time']]
    lap_vis_df.columns = ['Race','Average laptime (seconds)']
    lap_vis_df = lap_vis_df.sort_values(by='Average laptime (seconds)')
    fig_avg_times = px.line(lap_vis_df, x='Race', y='Average laptime (seconds)')
    fig_avg_times.update_layout(autosize=False,width=400, height=200,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),showlegend=False, title_x=0.5,xaxis_title=None)
    #fig_avg_times.update_traces(width=.5)

    total_laps = data_frame[['Grand Prix','Laps']]
    total_laps = total_laps.sort_values(by='Laps')
    total_laps.columns = ['Race','Laps']
    fig_totallaps = px.line(total_laps,x='Race',y='Laps')
    fig_totallaps.update_layout(autosize=False,width=400, height=200,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),xaxis_title=None)
    
    time_df_for_fig = data_frame[['Grand Prix','Time']]
    time_df_for_fig.columns = ['Race','Time']
    time_df_for_fig['Time'] = pd.to_datetime(time_df_for_fig['Time'])
    time_df_for_fig = time_df_for_fig.sort_values(by='Time',ascending=True)
    time_fig = px.line(time_df_for_fig,x='Race',y='Time',markers=True)
    time_fig.update_layout(autosize=False,width=400, height=300,margin=dict(
        l=50,
        r=50,
        b=0,
        t=50,
        pad=4
    ),title_text='Race Duration', title_x=0.5,xaxis_title=None,yaxis_title=None)
    st.plotly_chart(time_fig, use_container_width=True)


    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_totallaps, use_container_width=True)
    with col2:
        st.plotly_chart(fig_avg_times, use_container_width=True)

   
#page header
st.markdown("<h3 style='text-align: center; color: white;'>2022 F1 Seasonal Overview</h3>", unsafe_allow_html=True)
options = ['Driver Overview','Team Overview','Race Overview']

with st.sidebar:
    select_scope = st.selectbox('Select a scope',options) 
    
if select_scope == 'Driver Overview':
    driver_page(data_frame)
elif select_scope  == 'Team Overview':
    team_page(data_frame)
elif select_scope == 'Race Overview':
    race_page(data_frame)



