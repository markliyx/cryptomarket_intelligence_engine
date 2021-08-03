import streamlit as st
import altair as alt
from streamlit_echarts import st_echarts
from streamlit_vega_lite import vega_lite_component, altair_component
from annotated_text import annotated_text
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
Built by MTX Group Strategy Team 
''')
#------------------ about -------------------#
expander_bar = st.beta_expander("About", expanded=True)
expander_bar.markdown("""
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* A simple webapp that retrieves most updated cryptocurrencies/ exchanges information and generates the most 
relevant graphical illustrations at your fingertip.
""")
#------------------ *about -------------------#
# sidebar widgets 
menu_selectbox = st.sidebar.selectbox(
    "Menu",
    ("Exchanges", "Currencies"), 
    index=1
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
    marketShare = []
    takerFee = []
    makerFee = []

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
      marketShare.append(i.get('marketSharePct', 0))
      takerFee.append(i.get('takerFee', 0))
      makerFee.append(i.get('makerFee', 0))

    df = pd.DataFrame()
    df['Exchange Name'] = exchange_name
    df['Score'] = score
    df['Transaction Volume 24 Hours'] = volume_24h
    df['% Transaction Change 7 Days'] = percent_volume_change_7d
    df['Average Liquidity'] = average_liquidity
    df['Weekly Visits'] = weekly_visits
    df['Markets'] = markets
    df['Number of Coins'] = number_of_coins
    df['Number of Fiats Supported'] = number_of_fiats_supported
    df['Market Share Prediction'] = marketShare
    df['Maker Fee'] = makerFee
    df['Taker Fee'] = takerFee
    return df

# build charts using echarts library
def build_pie_charts(df, title, name, no_of_items):
    sorted_df = df.sort_values(title, ascending=False)[:no_of_items]
    sorted_df = sorted_df[[name, title]]
    other_df = pd.DataFrame(columns=[title],data=df[[title]].sort_values(title, ascending=False)[no_of_items:].sum())
    other_df[name] = 'other'
    sorted_df = sorted_df.append(other_df, ignore_index=True).sort_values(title, ascending=False)

    # input data in options
    data = pd.DataFrame()
    data[['value', 'name']] = sorted_df[[title, name]]
    data = list(data.T.to_dict().values())
    options = {
        "title": {
            "text": title, 
            "textStyle": {
                "fontWeight": 'normal',             
                "color":'#FFFFFF'
                },
            "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left",
                "textStyle": {
                "fontWeight": 'normal',             
                "color":'#FFFFFF'
                }},
            "series": [
        {
            "name": name,
            "type": "pie",
            "radius": "50%",
            "data": data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
    }
    st_echarts(options=options, height="600px")

# build frequency distribution using streamlit vega lite
def build_frequency_distribution(df, title, name, sort):
    #hist_data = pd.DataFrame(np.random.normal(42, 10, (200, 1)), columns=["x"])
    col1, col2, col3 = st.beta_columns([5, 3, 2])
    hist_data = df[[title, name, sort]]
    @st.cache
    def altair_histogram():
        brushed = alt.selection_interval(encodings=['x'], name="brushed")

        return (
            alt.Chart(hist_data)
            .mark_bar()
            .encode(alt.X(title, bin=alt.Bin(maxbins=50)), y="count()")
            .add_selection(brushed)
            .configure_mark(
                opacity=0.4,
                color='red'
            )
        )
    
    event_dict = altair_component(altair_chart=altair_histogram())

    r = event_dict.get(title)
    if r:
        with col1: 
            filtered = hist_data[(hist_data[title] >= r[0]) & (hist_data[title] < r[1])]
            st.write(filtered)
        with col2: 
            #towrite = "*There are a total of* " + str(len(filtered.index)) + " *items*"
            #st.header(towrite)
            annotated_text("There are a total of ",  (str(len(filtered.index)), "how many items", "#8ef"), " items")

# build currency pie charts 
def build_currency_pie_charts(cols, df_currency):
    fig, axes = plt.subplots(ncols=len(cols), figsize=(35, 10))
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

# build exchanges pie charts 
def build_exchange_pie_charts(cols, exchange_df):
    fig, axes = plt.subplots(ncols=len(cols), figsize=(35,10))
    cols = cols
    n = 0
    for ax in axes:
        i = cols[n]
        ax.title.set_text(i)
        sorted_df = exchange_df.sort_values(i, ascending=False)[:10]
        if n < 2:
            other_df = pd.DataFrame(columns=[i],data=exchange_df[[i]].sort_values(i, ascending=False)[10:].sum())
            other_df['Exchange Name'] = 'other'
            sorted_df = pd.concat([sorted_df, other_df]).sort_values(i, ascending=False)
        df_pie_plot = ax.pie(sorted_df[i], labels=sorted_df['Exchange Name'], autopct='%.2f')
        #ax.axis('equal')
        n += 1
    st.write(fig)

# exchange page 
def build_exchange_page():
    # loading data 
    exchange_df = load_data_exchange()

    # building sidebar 
    exchange_pie_charts_multiselect = st.sidebar.multiselect(
        "Exchange Pie Charts",
        ['Transaction Volume 24 Hours', 'Weekly Visits', 'Market Share Prediction'], 
        default= ['Weekly Visits']
    )

    frequency_distribution_multiselect = st.sidebar.multiselect(
        "Frequency Distribution Features",
        ['Transaction Volume 24 Hours', 'Weekly Visits', 'Market Share Prediction', 
        '% Transaction Change 7 Days', 'Average Liquidity', 'Markets', 'Number of Coins', 
        'Number of Fiats Supported', 'Market Share Prediction', 'Taker Fee', 'Maker Fee'], 
        default= ['Weekly Visits', 'Average Liquidity', 'Number of Coins']
    )

    number_of_item_slider = st.sidebar.slider(
        "Number of Items (Ordered by Score)",
        min_value=5,
        max_value=len(exchange_df.index),
        value=len(exchange_df.index)
    )

    top_items_slider = st.sidebar.slider(
        "Top n Items For Charts",
        min_value=1,
        max_value=len(exchange_df.index),
        value=10
    )

    
    # in left column
    with col1: 
        # build basic info and table 
        exchange_df = exchange_df.sort_values(by="Score", ascending=False).head(n=number_of_item_slider)
        st.header("Exchanges")
        st.write(exchange_df)
    
    #------------------ section: pie charts -------------------#
    expander_bar = st.beta_expander("Exchange Pie Charts")
    expander_bar.markdown("""
    * **Library Source:** [Streamlit ECharts](https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py).
    * Market Intellignece presented using pie charts
    """)
    #------------------ *section: pie charts -------------------#
    # build charts from multiselect box
    with st.beta_container():
        for title in exchange_pie_charts_multiselect:
            build_pie_charts(exchange_df, title, 'Exchange Name', top_items_slider)
    
    #------------------ section: distributions -------------------#
    expander_bar = st.beta_expander("Exchange Frequency Distributions")
    expander_bar.markdown("""
    * **Library Source:** [Streamlit Vega Lite](https://github.com/domoritz/streamlit-vega-lite).
    * Market Intellignece presented using Frequency Distributions
    """)
    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(exchange_df, title=title, name='Exchange Name', sort='Score')

# currency page
def build_currency_page():
    # loading data 
    if currency_selectbox == 'USD':
        currency_df = load_data_currency(2)
    elif currency_selectbox == 'BTC': 
        currency_df = load_data_currency(0)
    elif currency_selectbox == 'ETH':
        currency_df = load_data_currency(1)
    
    # building sidebar 
    currency_pie_charts_multiselect = st.sidebar.multiselect(
        "Currency Pie Charts",
        ['Market Cap', 'Volume 24 Hours', 'Volume 7 Days', 'Volume 30 Days'], 
        default= ['Market Cap', 'Volume 30 Days']
    )

    frequency_distribution_multiselect = st.sidebar.multiselect(
        "Frequency Distribution Features",
        ['Price', 'Market Cap', '% Change 24 Hours', '% Change 7 Days', 'Volume 24 Hours', 
        'Volume 7 Days', 'Volume 30 Days'], 
        default= ['% Change 24 Hours', '% Change 7 Days', 'Price']
    )

    number_of_item_slider = st.sidebar.slider(
        "Number of Items (Ordered by MarketCap)",
        min_value=5,
        max_value=len(currency_df.index), 
        value=len(currency_df.index)
    )

    top_items_slider = st.sidebar.slider(
        "Top n Items For Charts",
        min_value=1,
        max_value=len(currency_df.index),
        value=10
    )

    # in left column
    with col1: 
        currency_df = currency_df.sort_values(by="Market Cap", ascending=False).head(n=number_of_item_slider)
        st.header("Currencies")
        st.write(currency_df)

    #------------------ section: pie charts -------------------#
    expander_bar = st.beta_expander("Currency Pie Charts")
    expander_bar.markdown("""
    * **:Library Source:** [Streamlit ECharts](https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py).
    * Market Intellignece presented using pie charts
    """)
    #------------------ *section: pie charts -------------------#
    # build charts multiselect box 
    with st.beta_container():
        for title in currency_pie_charts_multiselect:
            build_pie_charts(currency_df, title, 'Coin Name', top_items_slider)

    #------------------ section: distributions -------------------#
    expander_bar = st.beta_expander("Currency Frequency Distributions")
    expander_bar.markdown("""
    * **Library Source:** [Streamlit Vega Lite](https://github.com/domoritz/streamlit-vega-lite).
    * Market Intellignece presented using Frequency Distributions
    """)
    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(currency_df, title=title, name='Coin Name', sort='Market Cap')
    
        


#--------- *functions --------#
#--------- column 2 ----------#
with col2:
    st.header("Top 10 Priced Coins")
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
