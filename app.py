import datetime as dt

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="FinMod Strategy Dashboard", layout="wide")

# Small logo/tag requested by user.
st.markdown(
    """
    <style>
    .yg-logo {
        position: fixed;
        top: 12px;
        right: 16px;
        font-size: 12px;
        font-weight: 600;
        color: #0f172a;
        background: #e2e8f0;
        border: 1px solid #cbd5e1;
        border-radius: 999px;
        padding: 4px 10px;
        z-index: 1000;
    }
    .main-title {
        margin-top: 0.2rem;
    }
    </style>
    <div class="yg-logo">Me yash Goyal YG</div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 class='main-title'>Stock Strategy Evaluation Dashboard</h2>", unsafe_allow_html=True)
st.caption("Simple strategy tester using Yahoo Finance data and the same 4 strategies as main.py")

TICKERS = {
    "Nifty 50": "^NSEI",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "NVIDIA": "NVDA",
    "Meta": "META",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Intel": "INTC",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan": "JPM",
    "Visa": "V",
    "Mastercard": "MA",
    "Walmart": "WMT",
    "Coca-Cola": "KO",
    "Pepsi": "PEP",
    "Johnson & Johnson": "JNJ",
    "Exxon Mobil": "XOM",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Larsen & Toubro": "LT.NS",
    "ITC": "ITC.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
}


@st.cache_data(show_spinner=False)
def get_data(symbol: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna().copy()
    return df


def moving_average_strategy(df: pd.DataFrame, short: int = 50, long: int = 200) -> pd.DataFrame:
    out = df.copy()
    out["MA_short"] = out["Close"].rolling(short).mean()
    out["MA_long"] = out["Close"].rolling(long).mean()
    out["Signal"] = 0
    out.loc[out["MA_short"] > out["MA_long"], "Signal"] = 1
    out["Position"] = out["Signal"].diff()
    return out


def compute_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def momentum_strategy(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["RSI"] = compute_rsi(out)
    out["Signal"] = 0
    out.loc[out["RSI"] < 30, "Signal"] = 1
    out.loc[out["RSI"] > 70, "Signal"] = -1
    return out


def mean_reversion_strategy(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    out = df.copy()
    out["Mean"] = out["Close"].rolling(window).mean()
    out["Std"] = out["Close"].rolling(window).std()
    out["Z"] = (out["Close"] - out["Mean"]) / out["Std"]
    out["Signal"] = 0
    out.loc[out["Z"] < -1, "Signal"] = 1
    out.loc[out["Z"] > 1, "Signal"] = -1
    return out


def breakout_strategy(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    out = df.copy()
    out["High_roll"] = out["High"].rolling(window).max()
    out["Low_roll"] = out["Low"].rolling(window).min()
    out["Signal"] = 0
    out.loc[out["Close"] > out["High_roll"].shift(1), "Signal"] = 1
    out.loc[out["Close"] < out["Low_roll"].shift(1), "Signal"] = -1
    return out


def backtest(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Returns"] = out["Close"].pct_change()
    out["Strategy_Returns"] = out["Returns"] * out["Signal"].shift(1)
    out["Cumulative_Market"] = (1 + out["Returns"]).cumprod()
    out["Cumulative_Strategy"] = (1 + out["Strategy_Returns"]).cumprod()
    return out


def evaluate_strategy(df: pd.DataFrame) -> tuple[float, float, float]:
    total_return = float(df["Cumulative_Strategy"].iloc[-1] - 1)
    daily_returns = df["Strategy_Returns"].dropna()
    vol = daily_returns.std()
    sharpe = float((daily_returns.mean() / vol) * np.sqrt(252)) if vol and not np.isnan(vol) else 0.0
    drawdown = df["Cumulative_Strategy"] / df["Cumulative_Strategy"].cummax() - 1
    max_dd = float(drawdown.min())
    return total_return, sharpe, max_dd


STRATEGIES = {
    "Moving Average": moving_average_strategy,
    "Momentum (RSI)": momentum_strategy,
    "Mean Reversion": mean_reversion_strategy,
    "Breakout": breakout_strategy,
}


def interpret(total_return: float, sharpe: float, max_dd: float) -> str:
    if total_return > 0.25:
        ret_msg = "Excellent Return"
    elif total_return > 0.10:
        ret_msg = "Good Return"
    elif total_return > 0:
        ret_msg = "Low Return"
    else:
        ret_msg = "Negative Return"

    if sharpe > 2:
        sharpe_msg = "Excellent Stability"
    elif sharpe > 1:
        sharpe_msg = "Good Risk Balance"
    elif sharpe > 0:
        sharpe_msg = "Risky"
    else:
        sharpe_msg = "Very Risky"

    if max_dd > -0.1:
        dd_msg = "Very Low Drawdown"
    elif max_dd > -0.2:
        dd_msg = "Acceptable Drawdown"
    elif max_dd > -0.4:
        dd_msg = "High Drawdown"
    else:
        dd_msg = "Very High Drawdown"

    return f"Return: {ret_msg} | Sharpe: {sharpe_msg} | Drawdown: {dd_msg}"


left, right = st.columns([1, 2])

with left:
    stock_name = st.selectbox("Choose Stock", list(TICKERS.keys()), index=0)
    ticker = TICKERS[stock_name]

    timeframe = st.selectbox("Choose Timeframe", ["6M", "1Y", "3Y", "5Y", "Custom"], index=1)

    today = dt.date.today()
    if timeframe == "6M":
        start_date = today - dt.timedelta(days=183)
        end_date = today
    elif timeframe == "1Y":
        start_date = today - dt.timedelta(days=365)
        end_date = today
    elif timeframe == "3Y":
        start_date = today - dt.timedelta(days=365 * 3)
        end_date = today
    elif timeframe == "5Y":
        start_date = today - dt.timedelta(days=365 * 5)
        end_date = today
    else:
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Start Date", value=today - dt.timedelta(days=365 * 2))
        with c2:
            end_date = st.date_input("End Date", value=today)

    compare_all = st.checkbox("Compare multiple strategies", value=False)

    if compare_all:
        selected_strategies = st.multiselect(
            "Select/Unselect Strategies",
            options=list(STRATEGIES.keys()),
            default=list(STRATEGIES.keys()),
        )
    else:
        selected = st.selectbox("Select Strategy", list(STRATEGIES.keys()), index=0)
        selected_strategies = [selected]

    run_btn = st.button("Run Evaluation", type="primary", use_container_width=True)

with right:
    st.info("Select stock, timeframe, and strategy settings, then click Run Evaluation.")

if run_btn:
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    if not selected_strategies:
        st.error("Please select at least one strategy.")
        st.stop()

    with st.spinner("Downloading data and running backtests..."):
        price_df = get_data(ticker, start_date, end_date)

    if price_df.empty:
        st.error("No data found for the selected stock/timeframe.")
        st.stop()

    st.subheader(f"Results for {stock_name} ({ticker})")

    price_fig = go.Figure()
    price_fig.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df["Close"],
            name="Close Price",
            mode="lines",
        )
    )
    price_fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10), title="Price Trend")
    st.plotly_chart(price_fig, use_container_width=True)

    comparison_fig = go.Figure()
    comparison_fig.add_trace(
        go.Scatter(
            x=price_df.index,
            y=(1 + price_df["Close"].pct_change()).cumprod(),
            name="Market",
            mode="lines",
            line=dict(width=2, dash="dash"),
        )
    )

    drawdown_fig = go.Figure()

    rows = []
    best_sharpe = -1e9
    best_name = ""

    for name in selected_strategies:
        strat_df = STRATEGIES[name](price_df)
        bt_df = backtest(strat_df)
        total_return, sharpe, max_dd = evaluate_strategy(bt_df)

        rows.append(
            {
                "Strategy": name,
                "Return (%)": round(total_return * 100, 2),
                "Sharpe Ratio": round(sharpe, 2),
                "Max Drawdown (%)": round(max_dd * 100, 2),
                "Interpretation": interpret(total_return, sharpe, max_dd),
            }
        )

        comparison_fig.add_trace(
            go.Scatter(
                x=bt_df.index,
                y=bt_df["Cumulative_Strategy"],
                name=name,
                mode="lines",
            )
        )

        dd_series = bt_df["Cumulative_Strategy"] / bt_df["Cumulative_Strategy"].cummax() - 1
        drawdown_fig.add_trace(
            go.Scatter(
                x=bt_df.index,
                y=dd_series,
                name=f"{name} Drawdown",
                mode="lines",
            )
        )

        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_name = name

    results_df = pd.DataFrame(rows).sort_values(by="Sharpe Ratio", ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Stock", f"{stock_name} ({ticker})")
    c2.metric("Strategies Run", str(len(selected_strategies)))
    c3.metric("Top Strategy (Sharpe)", best_name)

    st.dataframe(results_df, use_container_width=True, hide_index=True)

    comparison_fig.update_layout(
        title="Cumulative Returns Comparison",
        height=360,
        margin=dict(l=10, r=10, t=35, b=10),
        yaxis_title="Growth of 1",
    )
    st.plotly_chart(comparison_fig, use_container_width=True)

    drawdown_fig.update_layout(
        title="Drawdown Comparison",
        height=320,
        margin=dict(l=10, r=10, t=35, b=10),
        yaxis_title="Drawdown",
        yaxis_tickformat=".0%",
    )
    st.plotly_chart(drawdown_fig, use_container_width=True)

    st.success("Evaluation completed.")
