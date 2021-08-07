from re import search
import streamlit as st
import altair as alt
from streamlit_echarts import st_echarts
from streamlit_vega_lite import vega_lite_component, altair_component
from annotated_text import annotated_text
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
Built by Mark Li 
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

#------defining gloabl color variables ------#
yellow = "#FFFF85"
blue = "#8ef"
green = "#ADF598"
purple = "#F3C4FF"
white = "#FFFFFF"

#-----*defining gloabl color variables ------#

#-------helper functions------#
def is_numeric(s): 
    try: 
        float(s)
        return True
    except ValueError: 
        return False
#------*helper functions------#

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
                "color": white
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
    #st.subheader("Frequency Distribution of - " + title)
    annotated_text("Frequency Distribution of ", (title, "feature", purple))
    event_dict = altair_component(altair_chart=altair_histogram())

    r = event_dict.get(title)
    col1, col2 = st.beta_columns([6,4])
    if r:
        with col1: 
            filtered = hist_data[(hist_data[title] >= r[0]) & (hist_data[title] < r[1])]
            st.write(filtered)
        with col2: 
            #towrite = "*There are a total of* " + str(len(filtered.index)) + " *items*"
            st.subheader(emoji.emojize("Heyy! Here's a little more insight about your selection :stuck_out_tongue_winking_eye:"))
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
def build_pie_expandbar(name):
    expander_bar = st.beta_expander(name + " Pie Charts")
    expander_bar.markdown("""
    * **Library Source:** [Streamlit ECharts](https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py).
    """)
    
# build frequency distribution expandbar
def build_frequency_distribution_expandbar(title):
    distribution_expander_bar = st.beta_expander(title + " Frequency Distributions", expanded=True)
    distribution_expander_bar.markdown("""
    * **Library Source:** [Streamlit Vega Lite](https://github.com/domoritz/streamlit-vega-lite).
    """)
    distribution_expander_bar.markdown(emoji.emojize("* Here's how to use the interactive charts :arrow_down: :"))
    distribution_expander_bar.markdown("![Alt Text](https://media.giphy.com/media/TdZuiBwbLT883TOa2A/giphy.gif)")

# build sidebar items search select 
def items_multiselect(df, name):
    search_select = st.sidebar.multiselect(
        "Search " + name, 
        df[[name]], 
        default=[]
    )
    return search_select

# plotting correlation matrix
def build_correlation_matrix(df, name): 
    # build out multiselect bar
    matrix_select = st.sidebar.multiselect(
        "Select Correlation Features", 
        df.columns.tolist(), 
        default=df.columns.tolist()
    )

    if len(matrix_select) > 0:
        # build out expandbar session 
        expand_bar = st.beta_expander(name + " Correlation Matrix", expanded=True)
        expand_bar.markdown("""
        * **Function:** to visually evaluate how different features relates to one another.
        """)

        # plotting the correlation table
        corr = df.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        f, ax = plt.subplots(figsize=(20, 16))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
        st.pyplot(f)

# build number of items sidebar
def build_number_of_items(df, index):
    # select ordered by
    ordered_by_select= st.sidebar.selectbox(
        label="Ordered By",
        options=df.columns.tolist(), 
        index=index
    )
    # slider
    number_of_item_slider = st.sidebar.slider(
        "Number of Items (ordered by " + ordered_by_select + ")",
        min_value=5,
        max_value=len(df.index),
        value=len(df.index)
    )
    return number_of_item_slider, ordered_by_select

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

    number_of_item_slider, ordered_by_select = build_number_of_items(exchange_df, 1)

    top_items_slider = st.sidebar.slider(
        "Top n Items For Charts",
        min_value=1,
        max_value=len(exchange_df.index),
        value=10
    )
    # in left column
    with col1: 
        # build basic info and table 
        if exchange_df.head(1)[ordered_by_select].dtypes == 'float64': 
            exchange_df = exchange_df.sort_values(by=ordered_by_select, ascending=False).head(n=number_of_item_slider)
        else: 
            exchange_df = exchange_df.sort_values(by=ordered_by_select, ascending=True).head(n=number_of_item_slider)

        st.header("Exchanges")
        st.write(exchange_df)

    # building additional sidebar and poplulating search table
    list_of_search = items_multiselect(exchange_df, "Exchange Name")
    if len(list_of_search) > 0:
        st.header("Search Result")
        st.write(exchange_df[exchange_df["Exchange Name"].isin(list_of_search)])
    #------------------ section: pie charts -------------------#
    if len(exchange_pie_charts_multiselect) > 0:
        build_pie_expandbar("Exchange")
    #------------------ *section: pie charts -------------------#
    # build charts from multiselect box
    with st.beta_container():
        for title in exchange_pie_charts_multiselect:
            build_pie_charts(exchange_df, title, 'Exchange Name', top_items_slider)
    
    #------------------ section: distributions -------------------#
    if len(frequency_distribution_multiselect) > 0:
        build_frequency_distribution_expandbar("Exchange")

    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(exchange_df, title=title, name='Exchange Name', sort='Score', currency="USD")
    
    #------------------ section: correlation matrix ---------------#
    build_correlation_matrix(exchange_df, "Exchange Name")
    #------------------ *section: correlation matrix --------------#
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

    number_of_item_slider, ordered_by_select = build_number_of_items(currency_df, 5)

    top_items_slider = st.sidebar.slider(
        "Top n Items For Charts",
        min_value=1,
        max_value=len(currency_df.index),
        value=10
    )

    # in left column
    with col1: 
        if currency_df.head(1)[ordered_by_select].dtypes == 'float64':
            currency_df = currency_df.sort_values(by=ordered_by_select, ascending=False).head(n=number_of_item_slider)
        else:
            currency_df = currency_df.sort_values(by=ordered_by_select, ascending=True).head(n=number_of_item_slider)
        st.header("Currencies")
        st.write(currency_df)
    
    # building additional sidebar and poplulating search table
    list_of_search = items_multiselect(currency_df, "Coin Name")
    if len(list_of_search) > 0:
        st.subheader("Search Result")
        st.write(currency_df[currency_df["Coin Name"].isin(list_of_search)])

    #------------------ section: pie charts -------------------#
    if len(currency_pie_charts_multiselect) > 0:
        build_pie_expandbar("Currency")
    #------------------ *section: pie charts -------------------#
    # build charts multiselect box 
    with st.beta_container():
        for title in currency_pie_charts_multiselect:
            build_pie_charts(currency_df, title, 'Coin Name', top_items_slider)

    #------------------ section: distributions -------------------#
    if len(frequency_distribution_multiselect) > 0:
        build_frequency_distribution_expandbar("Currency")
    #------------------ *section: distributions -------------------#
        # build charts from multiselect box
    with st.beta_container():
        for title in frequency_distribution_multiselect:
            build_frequency_distribution(currency_df, title=title, name='Coin Name', sort='Market Cap', currency=currency_selectbox)
    
    #------------------ section: correlation matrix ---------------#
    build_correlation_matrix(currency_df, "Coin Name")
    #------------------ *section: correlation matrix --------------#
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
