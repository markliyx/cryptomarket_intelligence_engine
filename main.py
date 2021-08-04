import streamlit as st
import altair as alt
from streamlit_echarts import st_echarts
from streamlit_vega_lite import vega_lite_component, altair_component
from annotated_text import annotated_text
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import requests
import emoji 
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
      coin_name.append(i['name'])
      coin_symbol.append(i['symbol'])
      #print(i['p_17'][2])
      price.append(i['quotes'][currency]['price'])
      percent_change_24h.append(i['quotes'][currency]['percentChange24h'])
      percent_change_7d.append(i['quotes'][currency]['percentChange7d'])
      market_cap.append(i['quotes'][currency]['fullyDilluttedMarketCap'])
      volume_24h.append(i['quotes'][currency]['volume24h'])
      volume_7d.append(i['quotes'][currency]['volume7d'])
      volume_30d.append(i['quotes'][currency]['volume30d'])
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
def build_frequency_distribution(df, title, name, sort, currency):
    #hist_data = pd.DataFrame(np.random.normal(42, 10, (200, 1)), columns=["x"])
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
    st.header("Frequency Distribution of - " + title)
    event_dict = altair_component(altair_chart=altair_histogram())

    r = event_dict.get(title)
    col1, col2 = st.beta_columns([6,4])
    if r:
        with col1: 
            filtered = hist_data[(hist_data[title] >= r[0]) & (hist_data[title] < r[1])]
            st.write(filtered)
        with col2: 
            # defining local color scheme
            yellow = "#FFFF85"
            blue = "#8ef"
            green = "#ADF598"

            #towrite = "*There are a total of* " + str(len(filtered.index)) + " *items*"
            st.header(emoji.emojize("Heyy! Here's a little more insight about your selection :stuck_out_tongue_winking_eye:"))
            annotated_text("There are a total of ",  (str(len(filtered.index)), "number", blue), 
                " items in this range, and the top ", ("3", "number", blue), " items ranked by ", (sort, "rank method", yellow), " are as following: ") 
            if len(filtered.index) >= 3: 
                annotated_text(
                (filtered.iloc[[0]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[0]][sort], currency, yellow), 
                ", ",
                (filtered.iloc[[1]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[1]][sort], currency, yellow),
                ", ",  
                (filtered.iloc[[2]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[2]][sort], currency, yellow))
            elif len(filtered.index) == 2: 
                annotated_text(
                (filtered.iloc[[0]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[0]][sort], currency, yellow), 
                ", ",  
                (filtered.iloc[[1]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[1]][sort], currency, yellow))
            elif len(filtered.index) == 1:
                annotated_text(
                (filtered.iloc[[0]][name], name, green), " with a ", sort, " of ", (filtered.iloc[[0]][sort], currency, yellow))

# build pie charts expandbar
def build_pie_expandbar(title):
    expander_bar = st.beta_expander(title + " Pie Charts")
    expander_bar.markdown("""
    * **Library Source:** [Streamlit ECharts](https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py).
    * Market Intellignece presented using pie charts
    """)
    
# build frequency distribution expandbar
def build_frequency_distribution_expandbar(title):
    distribution_expander_bar = st.beta_expander(title + " Frequency Distributions", expanded=True)
    distribution_expander_bar.markdown("""
    * **Library Source:** [Streamlit Vega Lite](https://github.com/domoritz/streamlit-vega-lite).
    * Market Intellignece presented using Frequency Distributions
    """)
    distribution_expander_bar.markdown(emoji.emojize("* Here's how to use the interactive charts :arrow_down: :"))
    distribution_expander_bar.markdown("![Alt Text](https://media.giphy.com/media/TdZuiBwbLT883TOa2A/giphy.gif)")
# build exchange page 
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
    build_pie_expandbar("Exchange")
    #------------------ *section: pie charts -------------------#
    # build charts from multiselect box
    with st.beta_container():
        for title in exchange_pie_charts_multiselect:
            build_pie_charts(exchange_df, title, 'Exchange Name', top_items_slider)
    
    #------------------ section: distributions -------------------#
    build_frequency_distribution_expandbar("Exchange")

    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(exchange_df, title=title, name='Exchange Name', sort='Score', currency="USD")

# build currency page
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
    build_pie_expandbar("Currency")
    #------------------ *section: pie charts -------------------#
    # build charts multiselect box 
    with st.beta_container():
        for title in currency_pie_charts_multiselect:
            build_pie_charts(currency_df, title, 'Coin Name', top_items_slider)

    #------------------ section: distributions -------------------#
    build_frequency_distribution_expandbar("Currency")
    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(currency_df, title=title, name='Coin Name', sort='Market Cap', currency=currency_selectbox)

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
