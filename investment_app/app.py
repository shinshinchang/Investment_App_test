import plotly.graph_objects as go
import streamlit as st

try:
    from investment_app.data_fetcher import fetch_price_data
    from investment_app.indicators import add_indicators
    from investment_app.scanner import detect_ma_golden_cross
except ModuleNotFoundError:
    from data_fetcher import fetch_price_data
    from indicators import add_indicators
    from scanner import detect_ma_golden_cross


st.set_page_config(page_title="NCCU Technical Analysis Scanner", layout="wide")
st.title("Technical Analysis Stock Scanner")


ticker = st.sidebar.text_input("Ticker (example: 2330.TW or 0050)", "2330.TW").strip()
period = st.sidebar.selectbox("Period", ["1y", "2y", "5y"], index=0)


@st.cache_data(show_spinner=False)
def load_data(symbol: str, selected_period: str):
    raw = fetch_price_data(symbol=symbol, period=selected_period)
    return add_indicators(raw)


try:
    data = load_data(ticker, period)

    if data is None or data.empty:
        st.error(
            "No data returned from Yahoo Finance. If this is a Taiwan stock, try code like 2330/0050 (auto-add .TW) or 2330.TW directly."
        )
        st.stop()

    st.caption(f"Loaded {len(data)} rows for {ticker} ({period}).")

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Candlestick",
            )
        ]
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA20"],
            name="MA20",
            line=dict(color="orange"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA60"],
            name="MA60",
            line=dict(color="blue"),
        )
    )
    fig.update_layout(xaxis_rangeslider_visible=False)

    st.plotly_chart(fig, width="stretch")

    if detect_ma_golden_cross(data):
        st.success(f"Detected MA20/MA60 golden cross on {ticker}.")
    else:
        st.info("No MA20/MA60 golden cross signal currently.")
except Exception as exc:
    st.error(f"App error: {exc}")
    st.exception(exc)
