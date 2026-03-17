# FinMod Project

This is a simple stock strategy project.

You can:
- choose one stock from dropdown
- choose time period
- choose one strategy or compare all 4 strategies
- see results in table
- see clear plots for comparison

This project uses Yahoo Finance data.

## Files in project
- app.py -> Streamlit frontend
- main.py -> original strategy logic (not changed)
- requirements.txt -> python packages

## 4 Strategies used
1. Moving Average
2. Momentum (RSI)
3. Mean Reversion
4. Breakout

### 1) Moving Average Strategy
This strategy compares 2 averages of price:
- short moving average (fast)
- long moving average (slow)

Rule:
- Buy signal when short average goes above long average (uptrend)
- Exit/Sell signal when short average goes below long average (downtrend)

Best use:
- Works better in trending market
- Can give late signals in sideway market

### 2) Momentum Strategy (RSI Based)
This strategy uses RSI (Relative Strength Index) to check if stock is overbought or oversold.

Rule:
- Buy signal when RSI is below 30 (stock may be oversold)
- Sell signal when RSI is above 70 (stock may be overbought)

Best use:
- Useful when price moves in waves
- Sometimes gives false signals in strong one-side trend

### 3) Mean Reversion Strategy
This strategy assumes price comes back near its average after moving too far.

Rule:
- Calculate rolling mean and standard deviation
- Find Z-score (distance from mean)
- Buy signal when Z-score is very low (price much below mean)
- Sell signal when Z-score is very high (price much above mean)

Best use:
- Works better in range-bound market
- Risky in strong breakout trend

### 4) Breakout Strategy
This strategy checks recent high and low range.

Rule:
- Buy signal when price breaks above previous rolling high
- Sell signal when price breaks below previous rolling low

Best use:
- Works well when new trend starts after consolidation
- Can give fake breakout signals sometimes

## How to run on your laptop
### 1) Install packages
pip install -r requirements.txt

### 2) Run app
streamlit run app.py


## How to use app
1. Select stock (like Nifty, Apple, Tesla, etc.)
2. Select timeframe (6M, 1Y, 3Y, 5Y or custom)
3. Select strategy
4. If you want comparison, tick compare option and select multiple strategies
5. Click Run Evaluation
6. Check table + charts

Made by Yash Goyal (YG)
