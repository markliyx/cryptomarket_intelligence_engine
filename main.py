import streamlit as st
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import json

#---------- changing page setting -----------#
st.set_page_config(layout="wide")
#--------------------------------------------#

# adding tittle & markdown 
st.title('Cryptocurrency Market Intelligence')
st.markdown(''' 
A simple webapp that retrieves most updated cryptocurrencies/ exchanges information and generates the most 
relevant graphical illustrations at your fingertip
''')

# sidebar widgets 
menu_selectbox = st.sidebar.selectbox(
    "Menu",
    ("Exchanges", "Currencies")
)

number_of_item_slider = st.sidebar.slider(
    "Number of Items",
    min_value=10,
    max_value=300
)

currency_selectbox = st.sidebar.selectbox(
    "Currency",
    ('USD', 'BTC', 'ETH')
 )


# divide page into columns
col1, col2 = st.beta_columns([3,1])

#--------- functions --------#

# currency scrapper 
currency_price_unit = 'USD'
@st.cache
def load_data_currency(currency):
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []
    volume_7d = []
    volume_30d = []

    for i in listings:
      coin_name.append(i['p_1'])
      coin_symbol.append(i['p_2'])
      #print(i['p_17'][2])
      price.append(i['p_17'][currency]['1'])
      percent_change_24h.append(i['p_17'][currency]['7'])
      percent_change_7d.append(i['p_17'][currency]['8'])
      market_cap.append(i['p_17'][currency]['5'])
      volume_24h.append(i['p_17'][currency]['2'])
      volume_7d.append(i['p_17'][currency]['3'])
      volume_30d.append(i['p_17'][currency]['4'])
    df = pd.DataFrame()
    df['Coin Name'] = coin_name
    df['Coin Symbol'] = coin_symbol
    df['Price'] = price
    df['% Change 24 Hours'] = percent_change_24h
    df['% Change 7 Days'] = percent_change_7d
    df['Market Cap'] = market_cap
    df['Volume 24 Hours'] = volume_24h
    df['Volume 7 Days'] = volume_7d
    df['Volume 30 Days'] = volume_30d
    return df

# exchange scrapper 
@st.cache
def load_data_exchange():
    cmc = requests.get('https://coinmarketcap.com/rankings/exchanges')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    exchange_data = json.loads(data.contents[0])
    listings = exchange_data['props']['initialProps']['pageProps']['exchange']

    exchange_name = []
    score = []
    volume_24h = []
    percent_volume_change_7d = []
    average_liquidity = []
    weekly_visits = []
    markets = []
    number_of_coins = []
    number_of_fiats_supported = []

    for i in listings:
      exchange_name.append(i['name'])
      score.append(i['score'])
      volume_24h.append(i['totalVol24h'])
      percent_volume_change_7d.append(i['totalVolChgPct7d'])
      average_liquidity.append(i['liquidity'])
      weekly_visits.append(i['visits'])
      markets.append(i['numMarkets'])
      number_of_coins.append(i['numCoins'])
      number_of_fiats_supported.append(len(i['fiats']))

    df = pd.DataFrame(columns=['exchange_name', 'score', 'volume_24h', 
    'percent_volume_change_7d', 'average_liquidity', 'weekly_visits',
     'markets','number_of_coins', 'number_of_fiats_supported'])
    df['exchange_name'] = exchange_name
    df['score'] = score
    df['volume_24h'] = volume_24h
    df['percent_volume_change_7d'] = percent_volume_change_7d
    df['average_liquidity'] = average_liquidity
    df['weekly_visits'] = weekly_visits
    df['markets'] = markets
    df['number_of_coins'] = number_of_coins
    df['number_of_fiats_supported'] = number_of_fiats_supported
    return df

# build charts
def build_pie_charts(df, title, name):
    sorted_df = df.sort_values(title, ascending=False)[:10]
    fig, ax = plt.subplots()
    ax.pie(sorted_df[title], labels=sorted_df[name], radius=0.8)
    st.pyplot(fig)

# build currency pie charts 
def build_currency_pie_charts(cols, df_currency):
    fig, axes = plt.subplots(ncols=4, figsize=(35, 10))
    cols = cols
    n = 0
    for ax in axes:
        i = cols[n]
        ax.set_title(i)
        other_df = pd.DataFrame(columns=[i],data=df_currency[[i]].sort_values(i, ascending=False)[10:].sum())
        other_df['Coin Name'] = 'other'
        sorted_df = df_currency.sort_values(i, ascending=False)[:10]
        sorted_df = pd.concat([sorted_df, other_df]).sort_values(i, ascending=False)
        df_pie_plot = ax.pie(sorted_df[i], labels=sorted_df['Coin Name'], autopct='%.2f')
        ax.axis('equal')
        n += 1
    fig
# exchange page 
def build_exchange_page():
    with col1: 
        # build basic info and table 
        exchange_df = load_data_exchange()
        exchange_df = exchange_df.sort_values(by="score", ascending=False).head(n=number_of_item_slider)
        st.header("Exchanges")
        st.write(exchange_df)

        # build charts multiselect box
        with st.beta_container():
            for title in charts_multiselect:
                build_pie_charts(exchange_df, title, "exchange_name")

# currency page
def build_currency_page():
    currency_pie_charts_multiselect = st.sidebar.multiselect(
        "Currency Pie Charts",
        ['Market Cap', 'Volume 24 Hours', 'Volume 7 Days', 'Volume 30 Days']
    )
    with col1: 
        if currency_selectbox == 'USD':
            currency_df = load_data_currency(2)
        elif currency_selectbox == 'BTC': 
            currency_df = load_data_currency(0)
        elif currency_selectbox == 'ETH':
            currency_df = load_data_currency(1)
        currency_df = currency_df.sort_values(by="Market Cap", ascending=False).head(n=number_of_item_slider)
        st.header("Currencies")
        st.write(currency_df)
       
        # build charts multiselect box
        with st.beta_container():
            build_currency_pie_charts(currency_pie_charts_multiselect, currency_df)


#--------- *functions --------#
#--------- column 2 ----------#
with col2:
    st.header("Top 10 Highest Priced Coins")
    if currency_selectbox == 'USD':
        coin_price_df = load_data_currency(2)
    elif currency_selectbox == 'BTC': 
        coin_price_df = load_data_currency(0)
    elif currency_selectbox == 'ETH':
        coin_price_df = load_data_currency(1)
    coin_price_df = coin_price_df[["Coin Name", "Price"]].sort_values(by="Price", ascending=False).head(n=10)
    st.write(coin_price_df)

##################################### runtime logic ###############################

# menu selectbox
if menu_selectbox == "Exchanges":
    build_exchange_page()
elif menu_selectbox == "Currencies":
    build_currency_page()