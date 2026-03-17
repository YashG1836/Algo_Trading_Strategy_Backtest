import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')

def get_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    
    # FIX for multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True)
    return df

# Stragtegy Implementation : 
# 1) Moving Average Crossover
# 2) Momentum Strategy (RSI-based)
# 3) Mean Reversion (Z-score)
# 4) Breakout Strategy 



def moving_average_strategy(df, short=50, long=200):
    df = df.copy()
    
    df['MA_short'] = df['Close'].rolling(short).mean()
    df['MA_long'] = df['Close'].rolling(long).mean()
    
    df['Signal'] = 0
    df.loc[df['MA_short'] > df['MA_long'], 'Signal'] = 1
    
    df['Position'] = df['Signal'].diff()
    
    return df


def compute_rsi(df, window=14):
    delta = df['Close'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
def momentum_strategy(df):
    df = df.copy()
    
    df['RSI'] = compute_rsi(df)
    
    df['Signal'] = 0
    df.loc[df['RSI'] < 30, 'Signal'] = 1
    df.loc[df['RSI'] > 70, 'Signal'] = -1
    
    return df


def mean_reversion_strategy(df, window=20):
    df = df.copy()
    
    df['Mean'] = df['Close'].rolling(window).mean()
    df['Std'] = df['Close'].rolling(window).std()
    
    df['Z'] = (df['Close'] - df['Mean']) / df['Std']
    
    df['Signal'] = 0
    df.loc[df['Z'] < -1, 'Signal'] = 1
    df.loc[df['Z'] > 1, 'Signal'] = -1
    
    return df

def breakout_strategy(df, window=20):
    df = df.copy()
    
    df['High_roll'] = df['High'].rolling(window).max()
    df['Low_roll'] = df['Low'].rolling(window).min()
    
    df['Signal'] = 0
    df.loc[df['Close'] > df['High_roll'].shift(1), 'Signal'] = 1
    df.loc[df['Close'] < df['Low_roll'].shift(1), 'Signal'] = -1
    
    return df


# Backtesting using the actual market data 


def backtest(df):
    df = df.copy()
    
    df['Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Returns'] * df['Signal'].shift(1)
    
    df['Cumulative_Market'] = (1 + df['Returns']).cumprod()
    df['Cumulative_Strategy'] = (1 + df['Strategy_Returns']).cumprod()
    
    return df


#  Performance Check

def performance_metrics(df):
    total_return = df['Cumulative_Strategy'].iloc[-1] - 1
    
    daily_returns = df['Strategy_Returns'].dropna()
    
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    
    drawdown = df['Cumulative_Strategy'] / df['Cumulative_Strategy'].cummax() - 1
    max_dd = drawdown.min()
    
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.2%}")
    


def plot_results(df, title):
    plt.figure(figsize=(12,6))
    
    plt.plot(df['Cumulative_Market'], label='Market')
    plt.plot(df['Cumulative_Strategy'], label='Strategy')
    
    plt.title(title)
    plt.legend()
    plt.show()
    
    
symbol = "AAPL"   # change to anything (TCS.NS, INFY.NS etc.)
start = "2020-01-01"
end = "2024-01-01"

df = get_data(symbol, start, end)

df_strategy = moving_average_strategy(df)
# df_strategy = momentum_strategy(df)
# df_strategy = mean_reversion_strategy(df)
# df_strategy = breakout_strategy(df)

df_bt = backtest(df_strategy)

performance_metrics(df_bt)

plot_results(df_bt, "Strategy vs Market")

def evaluate_strategy(df):
    total_return = df['Cumulative_Strategy'].iloc[-1] - 1
    
    daily_returns = df['Strategy_Returns'].dropna()
    
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    
    drawdown = df['Cumulative_Strategy'] / df['Cumulative_Strategy'].cummax() - 1
    max_dd = drawdown.min()
    
    return total_return, sharpe, max_dd

strategies = {
    "Moving Average": moving_average_strategy,
    "Momentum (RSI)": momentum_strategy,
    "Mean Reversion": mean_reversion_strategy,
    "Breakout": breakout_strategy
}

results = []

for name, func in strategies.items():
    temp = func(df)
    temp = backtest(temp)
    
    total_return, sharpe, max_dd = evaluate_strategy(temp)
    
    results.append({
        "Strategy": name,
        "Return (%)": total_return * 100,
        "Sharpe Ratio": sharpe,
        "Max Drawdown (%)": max_dd * 100
    })

results_df = pd.DataFrame(results)
print(results_df)

def interpret_results(total_return, sharpe, max_dd):
    
    # --- Return Interpretation ---
    if total_return > 0.25:
        ret_msg = " Excellent Return"
    elif total_return > 0.10:
        ret_msg = " Good Return"
    elif total_return > 0:
        ret_msg = " Low Return"
    else:
        ret_msg = " Negative Return"
    
    
    # --- Sharpe Ratio Interpretation ---
    if sharpe > 2:
        sharpe_msg = " Excellent (Very Stable)"
    elif sharpe > 1:
        sharpe_msg = " Good (Acceptable Risk)"
    elif sharpe > 0:
        sharpe_msg = " Low (Risky)"
    else:
        sharpe_msg = " Bad (Very Risky)"
    
    
    # --- Max Drawdown Interpretation ---
    if max_dd > -0.1:
        dd_msg = " Very Low Risk"
    elif max_dd > -0.2:
        dd_msg = " Acceptable Risk"
    elif max_dd > -0.4:
        dd_msg = " High Risk"
    else:
        dd_msg = " Very High Risk"
    
    
    # --- Print nicely ---
    print("\nPERFORMANCE SUMMARY\n")
    
    print(f"Return: {total_return*100:.2f}% → {ret_msg}")
    print(f"Sharpe Ratio: {sharpe:.2f} → {sharpe_msg}")
    print(f"Max Drawdown: {max_dd*100:.2f}% → {dd_msg}")
    
    
total_return, sharpe, max_dd = evaluate_strategy(df_bt)

interpret_results(total_return, sharpe, max_dd)