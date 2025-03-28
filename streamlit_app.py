##This is a streamlit application to show an outlook on API ingestion and data visualization. 
##There is a small data analysis using pandas as a main library for data analysis
##Summary: This is a example page for data display and deployment on streamlit. It shows 3 pages and performs an API call from ERCOT API
##There could be better performance optimization and better modularity in code practices. This is just a representation on potential work samples
##Contact: Paolo Poemape


##Export python libraries
import streamlit as st
##Geopandas for geolocation data and display houston map
import geopandas as gpd
import folium
import requests
import json
import pandas as pd 
import plotly.graph_objects as go
import plotly.express as px
from folium import plugins
from streamlit_folium import st_folium
##Static representation for a map using folium_static function
from streamlit_folium import folium_static
from datetime import datetime
from io import StringIO

##Data reading from public csv file
def csv_energy_consumption():
    url = 'https://raw.githubusercontent.com/paolopoemape/data/refs/heads/main/APUS37B72610.csv'
    response = requests.get(url, verify=False)
    data = StringIO(response.text)
    print(data)
    df = pd.read_csv(data)
    print(df)
    average_price = df['APUS37B72610'].mean()
    fig = go.Figure([go.Scatter(x=df['observation_date'], y=df['APUS37B72610'])])

    fig.add_trace(go.Scatter(x=df['observation_date'], 
                             y=[average_price] * len(df['observation_date']),
                             mode='lines', name=f'Average Price: {average_price:.2f}',
                             line=dict(color='red', dash='dash', width=2)))

    fig.update_layout(
        title="Energy Prices with Average Price",
        xaxis_title="Date",
        yaxis_title="$ Dollar Price per Killowatt Hour",
        showlegend=True,
        template="plotly_dark"
    )

##Create a DataFrame from public csv and ingest geojson data 
    url_houston = "https://raw.githubusercontent.com/paolopoemape/data/refs/heads/main/houston%202024-01-01%20to%202025-01-01.csv"
    response_houston = requests.get(url_houston, verify=False)
    data_houston = StringIO(response_houston.text)
    df_houston = pd.read_csv(data_houston)

    fig_houston = go.Figure()
    fig_houston.add_trace(go.Scatter(
        x=df_houston['datetime'],
        y=df_houston['tempmax'],
        fill='tonexty', 
        mode='none',  
        name='tempmax'
    ))
    fig_houston.add_trace(go.Scatter(
        x=df_houston['datetime'],
        y=df_houston['tempmin'],
        fill='tonexty',
        mode='none',
        name='tempmin'
    ))
    fig_houston.add_trace(go.Scatter(
        x=df_houston['datetime'],
        y=df_houston['temp'],
        fill='tonexty',
        mode='none',
        name='temp'
    ))

    fig_houston.update_layout(
        title="Weather Data - Houston 2024 - Represented in Celsius",
        xaxis_title="Date",
        yaxis_title="Temp in C",
        showlegend=True,
        template="plotly_dark"
    )
    ##Show three columns to display
    col1, col2, col3 = st.columns([1,1,1], gap="large")
    with col1:
        st.title("Electricity Pricing")
        st.write(f"The average price of energy consumption in 2024 is **${average_price:.2f}** per kilowatt hour.")
        st.plotly_chart(fig)
    with col2:
        st.title("Weather Trends Houston 2024")
        st.plotly_chart(fig_houston)
    with col3:
        st.subheader("Brief Analysis")
        st.markdown("My initial attempt in representing this two datasets and graphs was to show a correlation, while doing a seasonality analysis, in electricity pricing and season patterns")
        st.markdown("However, I failed on providing a correct analysis due to the following factors")
        st.markdown("""
        - First, the electricity pricing contains missing values, which could impact the analysis on seasonality. Also, I need more than one-year dataset to provide a correct forecast on seasonility using the electrical prices
        - Second, the electrical pricing doesn't seem to have a strong deviation across its time-series, which could be due to consumers having year-long contracts. This helps end-consumers in getting a stable eletricity price across a year regardless on changes in demand
        """)
        st.markdown("Finally, this cursory analysis was just an attempt to provide a brief introduction on a potential correlation between two factors: weather and electrical pricing. This analysis could be expanded with a bigger dataset and a longer timeframe" )

today_date = datetime.today().strftime('%Y-%m-%d')
print(today_date)


##Authentication
auth_url = 'https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token'
##payload has to be filled with API authentication from user
payload = {
    'username': ##username from ERCOT API
    'password': ##password set up 
    'scope': ##scope
    'grant_type': 'password',
    'client_id': ##clientID can be obtained from GET response
    'response_type': 'id_token'
}
response = requests.post(auth_url, data=payload)
## Check if request is completed
if response.status_code == 200:
    # Extract the Bearer token from the response
    token_data = response.json()
    bearer_token = token_data['access_token']
    print("Bearer token received:", bearer_token)
else:
    print("Failed to authenticate:", response.status_code, response.text)

##ERCOT API, it gets the latest date based off today_date variable
api_url = "https://api.ercot.com/api/public-reports/np4-190-cd/dam_stlmnt_pnt_prices?deliveryDateFrom=" + today_date + "&settlementPoint=LZ_HOUSTON"
print(api_url)
bearer_token = bearer_token
headers = {
    "Authorization": f"Bearer {bearer_token}",
     "Ocp-Apim-Subscription-Key": ##Private subscription key from ERCOT,
    "Content-Type": "application/json"  
}
response = requests.get(api_url, headers=headers)
if response.status_code == 200:
    print("Response data:", response.json())  
    print("Request successful")
else:
    print(f"Error {response.status_code}: {response.text}")

##Didn't have enough time to latest column
df = pd.DataFrame(response.json()['data'])
df.columns = ["Day", "Time", "Zone", "DAM Price", "T/F Will Delete"]

# Load the GeoJSON file for Texas
selection = st.sidebar.selectbox(
    'Choose a selection to view:',
    ['Introduction','Houston', 'Electricity Pricing and Weather Trends']
)   
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/houston.geojson"
response = requests.get(url, verify=False)
geojson_data = response.json() 
for feature in geojson_data['features']:
    for key in ['created_at', 'updated_at']:
        if key in feature['properties']:
            feature['properties'][key] = pd.to_datetime(feature['properties'][key]).isoformat()

houston_map = folium.Map(location=[29.7604, -95.3698], zoom_start=10)
folium.GeoJson(geojson_data).add_to(houston_map)
height = "500px"  
##Custom CSS to change layout across pages
st.markdown(
    """
    <style>
    .st-emotion-cache-mtjnbi {
        width: 70%;
        padding: 6rem 1rem 10rem;
        min-width: auto;
        max-width: initial;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

##Module to display information when the user clicks on the Houston option in the dropdown
def houston_show():
    st.write("This view shows DAM (Day-Ahead Market) Settlement prices in the Load Zone Houston Area")
    st.markdown("""
    The importance of DAM Settlement prices rely on the impact and direct influence it has on pricing and planning of 
    electricity in the wholesale market. That means: <br><br>
        - The DAM settlement prices are used as reflection to supply and demand dynamics in an area. <br>
        - It shows the forward market for electricity where the market participants can submit their bids for the next day <br>
        - It is also used for financial hedging and risk management due to the creation of contracts against price volatility through futures contracts or options <br>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1,1], gap="large")
    ##Created three columns for a better UX experience
    with col1:
        st.subheader("DAM Prices for LZ_Houston")
        table_container = st.container()
        with table_container:
            st.table(df.head(15))
    with col2:
        st.subheader("Houston Geograpic Map")
        map_container = st.container()  # Create a container for the map
        with map_container:
            folium_static(houston_map)
##Module for introduction page
def introduction():
    # Brief Introduction
    st.title("👋 Hello, I'm Paolo Poemape")
    st.write("""
        <h2 style="font-size: 30px;">
        I am passionate about technology, data, and continuous learning. 
        I created this website to showcase my skills using streamlit, matplotlib, and plotly. I also did a small analysis using pandas and numpy
        <br><br>This is not a full-fledged application, but it shows a small sample on my capacities. I have been working at Austin Energy in their data team where I support,
        develop, and train business units to take adavatange in data applications. <br><br>That means sometimes I might need to create an ETL pipeline, or run small-report analysis for our customers,
        or create visualizations using Tableau/PowerBI. 
        <br>However, I take new challenges to learn and I am always willing to put in the work to learn new technologies. 
        <br><br>This small website showcases my capabilities and learning outcomes. I created this website in 5 hours and it includes a post, get request using authetincators to extract ERCOT data api, extraction and analysis from CSV files and the use of geoJSON data
        <br></h2>
    """, unsafe_allow_html=True)

    ##LinkedIn Link
    st.write('<p style="font-size: 25px;">You can connect with me on my <a href="https://www.linkedin.com/in/paolopoemape" target="_blank">LinkedIn profile</a>.</p>', unsafe_allow_html=True)

    ##Attach Resume
    st.write('<p style="font-size: 25px;"> You can view and download my resume here 📄:</p>', unsafe_allow_html=True)
    github_url = "https://raw.githubusercontent.com/paolopoemape/resume/6677f59c5b1bf07e1883d5f0f420bdf6d2692c74/Resume_Paolo_Poemape.pdf"
    ##Option to download my resume
    response = requests.get(github_url)   
    st.download_button(
        label="Download Resume",
        data=response.content,
        file_name='Paolo_Poemape_Resume.pdf',
        mime='application/pdf'
    )
##Dropdown options
if selection == "Electricity Pricing and Weather Trends":
    st.title(selection)
    csv_energy_consumption()
elif selection == "Houston":
    st.title(selection)
    houston_show()
elif selection == "Introduction":
    st.title(selection)
    introduction()

