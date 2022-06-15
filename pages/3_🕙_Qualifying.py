
def qualifying():
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


    
    st.markdown("<h1 style='text-align: center; color: white;'>Formula 1 - 2022</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Qualifying overview</h2>", unsafe_allow_html=True)


    #create function to get link for avl data
    def get_races():
        f1_links = pd.read_csv('F1_Links.csv')
        return f1_links
    
    links = get_races()
    races = links['Race']

    @st.cache
    def get_all_quals(links):
        append_quals = pd.DataFrame()
        qual_links = links[['Race','Qualifying']]
        for index, row in qual_links.iterrows():
            #get data for start
            qual_url = row['Qualifying']
            # Request content from web page
            result = requests.get(qual_url)
            c = result.content
            # Set as Beautiful Soup Object
            soup = BeautifulSoup(c,'html.parser')
            tbl= soup.find("table",{'class':'resultsarchive-table'})
            qual_df = pd.read_html(str(tbl))[0]
            #cleaning data
            qual_df = qual_df[['Driver','Q1','Q2','Q3']]
            qual_df['Race'] = row['Race']
            #qual_df['string_for_merge'] = qual_df['Race'] + qual_df['Driver']
            append_quals = append_quals.append(qual_df)
            
        return append_quals

    all_qual_data = get_all_quals(links)

    selected_race = st.selectbox('Select a race: ',races)

    links = get_races()

    #return dataframe of selection
    race_df = links.loc[links['Race']==selected_race]
    selected_qual = race_df['Qualifying'].values[0]

    #get data from page, clean for export
    url = selected_qual

    # Request content from web page
    result = requests.get(url)
    c = result.content

    # Set as Beautiful Soup Object
    soup = BeautifulSoup(c,'html.parser')
    tbl= soup.find("table",{'class':'resultsarchive-table'})
    data_frame1 = pd.read_html(str(tbl))[0]

    colors = pd.read_csv('f1_colors.csv')
    data_frame = pd.merge(data_frame1,colors,how='left',on='Car')
    data_frame['Driver'] = data_frame['Driver'].str[:-3]

    #create melted df for facet vis
    df_for_melt = data_frame[['Driver','Q1','Q2','Q3']]
    df_melted = df_for_melt.melt('Driver')
    df_melted = df_melted.sort_values(by='value')

    #create df for melted info
    df_for_melt_info = data_frame[['Driver','Car','Color']]

    df_melt_merged = pd.merge(df_melted,df_for_melt_info,how='left',on='Driver')
    def create_q1_split_fig():
        colors_list = data_frame['Color']
        fig = px.bar(df_melt_merged,x=df_melt_merged['variable'],y=df_melt_merged['value'],facet_col=df_melt_merged['Driver'],facet_col_wrap=5,color='Driver',color_discrete_sequence=colors_list,labels=dict(value='',variable=''))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(showlegend=False)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        return fig
    fig = create_q1_split_fig()
    st.plotly_chart(fig,use_container_width=True)

    input_value = st.selectbox('Select a qualifying round', ('Q1','Q2','Q3'))

    def update_figure(input_value):

        #input and filtered df
        filtered_df = data_frame[['Driver',str(input_value),'Color']]
        filtered_df = filtered_df.replace(['DNF'],np.nan)
        df_for_fig = filtered_df.dropna()
        
        # convert to timedelta...
        df_for_fig[input_value] = (
            df_for_fig[input_value]
            .str.extract(r"(?P<minute>[0-9]+):(?P<sec>[0-9]+).(?P<milli>[0-9]+)")
            .apply(
                lambda r: pd.Timestamp(year=1970,month=1,day=1,
                                    minute=int(r.minute),second=int(r.sec),microsecond=int(r.milli) * 10 ** 3,
                ),
                axis=1,
            )
            - pd.to_datetime("1-jan-1970").replace(hour=0, minute=0, second=0, microsecond=0)
            )

        #normalize string text
        def strfdelta(t, fmt="{minutes:02d}:{seconds:02d}.{milli:03d}"):
            d = {}
            d["minutes"], rem = divmod(t, 10 ** 9 * 60)
            d["seconds"], d["milli"] = divmod(rem, 10 ** 9)
            d["milli"] = d["milli"] // 10**6
            return fmt.format(**d)
        
        #figure
        df_for_fig = df_for_fig.sort_values(by=input_value)
        fig = px.line(df_for_fig,y='Driver',x=input_value,hover_name=df_for_fig[input_value].astype('int64').apply(strfdelta),markers=True,text=df_for_fig[input_value].astype('int64').apply(strfdelta))
        fig.update_traces(textposition = "bottom right")
        # fix up tick labels
        ticks = pd.Series(range(df_for_fig[input_value].astype('int64').min() - 10 ** 10,df_for_fig[input_value].astype('int64').max(),10 ** 10,))
        fig.update_layout(
            xaxis={
                "range": [
                    df_for_fig[input_value].astype('int64').min(),
                    df_for_fig[input_value].astype('int64').max(),
                ],
                "tickmode": "array",
                "tickvals": ticks,
                "ticktext": ticks.apply(strfdelta),
                "side":"top",
                "showgrid":False,
                "showticklabels":False
            },
        yaxis={'categoryorder':'total descending',"showgrid":False},
        autosize=False,
        width=500,
        height= 500,
        plot_bgcolor ='rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)')
        fig.update_layout(xaxis={'title':input_value})
        return fig
    fig = update_figure(input_value)
    st.plotly_chart(fig,use_container_width=True)

qualifying()