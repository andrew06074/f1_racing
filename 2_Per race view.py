def get_changeinplaces():
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
    def get_selected_race():
        f1_links = pd.read_csv('F1_Links.csv')
        return f1_links

    #call function to get link data
    f1_links = get_selected_race()

    #create list of avl races
    races = f1_links['Race']

    def write_driver_report():
          #create function to get link for avl data
        def get_selected_race():
            f1_links = pd.read_csv('F1_Links.csv')
            return f1_links

        #call function to get link data
        f1_links = get_selected_race()

        #create list of avl races
        races = f1_links['Race']

        #return dataframe of selection
        race_df = f1_links.loc[f1_links['Race']==selected_race]

        #return selected url to scrape data from
        selected_start = race_df['Race Start - HTML'].values[0]
        selected_result = race_df['Race Results - HTML'].values[0]

        def scrape_selection(selected_start,selected_result):
            #get data for start
            start_url = selected_start
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


            #get data for results
            #get data for start
            result_url = selected_result
            # Request content from web page
            result = requests.get(result_url)
            c = result.content

            # Set as Beautiful Soup Object
            soup = BeautifulSoup(c,'html.parser')
            tbl= soup.find("table",{'class':'resultsarchive-table'})
            result_df = pd.read_html(str(tbl))[0]
            #cleaning data
            result_df = result_df[['Driver','Pos']]
            result_df.columns = ['Driver','Results Position']

            #merge dataframes
            merged = pd.merge(start_df,result_df,how='left',on='Driver')
            
            #repalce nc's with 20
            merged = merged.replace('NC','20')
            
            #change datatypes
            merged['Start Position'] = merged['Start Position'].astype(int)
            merged['Results Position'] = merged['Results Position'].astype(int)
            
            #create position changed
            merged['Change in position'] = (merged['Start Position'] - merged['Results Position'])

            merged = merged[['Driver','Results Position','Start Position','Change in position','Car']]
            merged = merged.sort_values('Results Position')

            colors = pd.read_csv('f1_colors.csv')
            merged = pd.merge(merged,colors,how='left',on='Car')
            merged['Driver'] = merged['Driver'].str[:-4]
            return merged

        scraped_df = scrape_selection(selected_start,selected_result)
        
        top_5_changes = scraped_df.sort_values(by='Change in position',ascending=False)
        top_5_changes = top_5_changes.head(5)

        bottom_5_changes = scraped_df.sort_values(by='Change in position',ascending=True)
        bottom_5_changes = bottom_5_changes.head(5)
        
        
        st.markdown("<h2 style='text-align: center; color: white;'>Most positions gained - Top 5</h2>", unsafe_allow_html=True)
        st.markdown(f"""<h6 style='text-align: center; color: white;'>{selected_race}</h6>""", unsafe_allow_html=True)
        for index, row in top_5_changes.iterrows():
            st.markdown(f"""<h3 style='text-align: center; color: {row['Color']};'> {row['Driver']} </h3>""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Result position",row['Results Position'])
            col2.metric("Starting position",row['Start Position'])
            col3.metric("Change in positions ",row['Change in position'])

        st.write('--------------------------')


        st.markdown("<h2 style='text-align: center; color: white;'>Most positions lost - Bottom 5</h2>", unsafe_allow_html=True)
        st.markdown(f"""<h6 style='text-align: center; color: white;'>{selected_race}</h6>""", unsafe_allow_html=True)
        for index, row in bottom_5_changes.iterrows():
            st.markdown(f"""<h3 style='text-align: center; color: {row['Color']};'> {row['Driver']} </h3>""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Result position",row['Results Position'])
            col2.metric("Starting position",row['Start Position'])
            col3.metric("Change in positions ",row['Change in position'])


     #title
    st.markdown("<h1 style='text-align: center; color: white;'>Formula 1 - 2022</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Race placement changes</h2>", unsafe_allow_html=True)
    st.write('-------------')

    #make and display select box for avl races
    selected_race = st.selectbox('Select a race: ',races)

    #make radio buttons
    report_scope = st.radio("Select a report:",('Driver','Team'))
    st.write('---------------')
    if report_scope == 'Driver':
        write_driver_report()

get_changeinplaces()