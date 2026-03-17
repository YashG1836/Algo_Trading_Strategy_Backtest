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
