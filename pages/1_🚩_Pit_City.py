from lib2to3.pgen2 import driver
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

    def pit_strategy_vis(links):
        #loop through all race pit stop links to get df and append
        @st.cache(allow_output_mutation=True)
        def get_all_pit_data(links):
            append_pit = pd.DataFrame()
            quals = links[['Race','Pit Stop Summary']]
            for index, row in quals.iterrows():
                #get data for start
                start_url = row['Pit Stop Summary']
                # Request content from web page
                result = requests.get(start_url)
                c = result.content
                # Set as Beautiful Soup Object
                soup = BeautifulSoup(c,'html.parser')
                tbl= soup.find("table",{'class':'resultsarchive-table'})
                pitstop_df = pd.read_html(str(tbl))[0]
                #cleaning data
                pitstop_df = pitstop_df[['Driver','Car','Lap','Time','Total']]
                pitstop_df['Driver'] = pitstop_df['Driver'].str[:-3]
                pitstop_df['Time'] = pitstop_df['Time'].astype(str)
                pitstop_df['Total'] = pitstop_df['Total'].astype(str)
                pitstop_df['Race'] = row['Race']
                pitstop_df['string_for_merge'] = pitstop_df['Race'] + pitstop_df['Driver']
                append_pit = append_pit.append(pitstop_df)
            return append_pit
        pit_data = get_all_pit_data(links)

        pit_data_df = pit_data
        pit_data_df['Time'] = pit_data_df['Time'].astype(str)
        pit_data_df['Time'] = pit_data_df['Time'].str[:-4]

        vc_pits_df = pit_data_df.value_counts(subset=['Race','Lap']).reset_index()
        vc_pits_df.columns = ['Race','Lap','variable']

        col1, col2 = st.columns(2)
        with col1:
            def team_pit_viss(pit_data):
                team_data = pit_data.value_counts(pit_data['Car']).rename_axis('Team').reset_index(name='Total pit stops').head(5)
                team_data = team_data.set_index('Team')
                st.markdown("<h6 style='text-align: center; color: white;'>Team pit standings</h6>", unsafe_allow_html=True)
                st.table(team_data)
            team_pit_viss(pit_data)
        with col2:
            def driver_pit_viss(pit_data):
                driver_data = pit_data.value_counts(pit_data['Driver']).rename_axis('Driver').reset_index(name='Total pit stops').head(5)
                driver_data = driver_data.set_index('Driver')
                st.markdown("<h6 style='text-align: center; color: white;'>Driver pit standings</h6>", unsafe_allow_html=True)
                st.table(driver_data)
            driver_pit_viss(pit_data)

        def pit_count_race_vis(vc_pits_df):

            fig = px.bar(vc_pits_df,x=vc_pits_df['Lap'],y=vc_pits_df['variable'],facet_col=vc_pits_df['Race'],facet_col_wrap=2,labels=dict(variable=''))
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(showlegend=False,title_text='Pit distribution race duration',title_x=0.5)
            st.plotly_chart(fig,use_container_width=True)
        pit_count_race_vis(vc_pits_df)


    pit_strategy_vis(links)
change_in_palce_sn()