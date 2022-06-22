from tenacity import retry_base


def change_in_palce_sn():
    from heapq import merge
    from tracemalloc import start
    from unittest import result
    import pandas as pd
    from scipy.misc import face
    import  streamlit as st
    import plotly.express as px

    #libs for scraper
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import lxml


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
        fig.update_layout(yaxis={'categoryorder':'total ascending'},showlegend=False,title_text='Season total: Change in grid placement - Race start to finish', title_x=0.5,yaxis_title=None,xaxis_title=None)
        fig.update_traces(width=1)
        st.plotly_chart(fig, use_container_width=True)


    st.markdown("<h1 style='text-align: center; color: white;'>F1 2022 - Custom Metrics</h1>", unsafe_allow_html=True)

    get_driver_change(season_pos_changes,driver_team_link)
    

change_in_palce_sn()