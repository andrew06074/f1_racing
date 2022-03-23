import pandas as pd
from scipy.misc import face
import  streamlit as st
import plotly.express as px

#libs for scraper
from bs4 import BeautifulSoup
import requests
import pandas as pd
import lxml

st.markdown("<h1 style='text-align: center; color: white;'>Formula 1 - Bahrain Qualifier</h1>", unsafe_allow_html=True)

#get data from page, clean for export
url = 'https://www.formula1.com/en/results.html/2022/races/1124/bahrain/qualifying.html'

# Request content from web page
result = requests.get(url)
c = result.content

# Set as Beautiful Soup Object
soup = BeautifulSoup(c,'html.parser')
tbl= soup.find("table",{'class':'resultsarchive-table'})
data_frame1 = pd.read_html(str(tbl))[0]


#cleaning data
data_frame = data_frame1.drop(data_frame1.columns[0], axis=1)
data_frame = data_frame1.drop(data_frame1.columns[8], axis=1)
colors = pd.read_csv('f1_colors.csv')
data_frame = pd.merge(data_frame,colors,how='left',on='Car')
data_frame['Driver'] = data_frame['Driver'].str[:-3]

#create melted df for facet vis
df_for_melt = data_frame[['Driver','Q1','Q2','Q3']]
df_melted = df_for_melt.melt('Driver')
df_melted = df_melted.sort_values(by='value')

#create df for melted info
df_for_melt_info = data_frame[['Driver','Car','Color']]

df_melt_merged = pd.merge(df_melted,df_for_melt_info,how='left',on='Driver')


if st.checkbox('Show notes'):
    #start commentary
    st.header('Scrape and clean data for visuals:')
    st.write('My goal is to build a dashboard to analyze Formula 1 data.')
    st.write('The data I want to analyze can be found a the following link.')
    st.write("[Formula 1 - Bahrain Qualifier](https://www.formula1.com/en/results.html/2022/races/1124/bahrain/qualifying.html)")
    st.write('I am able to identify that the data presented by the F1 site is stored in an html table making it easy to scrape using BeautifulSoup4.')
    st.subheader('The following dataframe object is returned.')
    #stop commentary

    #write dataframe
    st.write(data_frame1)

    #start commentary
    st.subheader('The returned data is great...but we can make it better.')
    st.markdown("""
    Lets make a few changes!
    - Remove excess columns
        - Remove the desired columns by index
    - Change name so only name is shown, not abreviation after name
        - Use string strip method to remove last 4 characters of driver name
    - Add color column to match brand identity for visual
        - Join f1_colors.csv, match brand hex color to 'Car'

    """)
    #end commentary

    st.write(data_frame)
    st.subheader('Looks like a great place to start!')
    st.write('As we continue to expore and develop our dataset we will indevedibly need to add or make changes to our data.')
    st.write('---------------')
    st.header('Notes for visuals:')
    st.subheader('Qualifying overview')
    st.write(df_melt_merged)
    #visual to show all drivers and split times

    
def create_q1_split_fig():
    colors_list = colors['Color']

    fig = px.bar(df_melt_merged,x=df_melt_merged['variable'],y=df_melt_merged['value'],facet_col=df_melt_merged['Driver'],facet_col_wrap=5,color='Car',color_discrete_sequence=colors_list,labels=dict(value='',variable=''))
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