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
        fig.update_layout(yaxis={'categoryorder':'total ascending'},showlegend=False,title_text='Season aggrigate change in grid placement race start to finish', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)


    st.markdown("<h1 style='text-align: center; color: white;'>Formula 1 - 2022</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Change in grid placement</h2>", unsafe_allow_html=True)
    st.write('-------------')
    get_driver_change(season_pos_changes,driver_team_link)
    

    def write_driver_report():
          #create function to get link for avl data
        def get_selected_race():
            f1_links = pd.read_csv('F1_Links.csv')
            return f1_links

        #call function to get link data
        f1_links = get_selected_race()

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


    st.markdown("<h4 style='color: white;'>View individual race changes</h4>", unsafe_allow_html=True)
    if st.checkbox('Click here'):
        #make and display select box for avl races
        selected_race = st.selectbox('Select a race: ',races)
        write_driver_report()

change_in_palce_sn()