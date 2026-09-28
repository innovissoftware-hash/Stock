# Stock Technical Analysis Agent

## What it does
- Accepts an NSE/Yahoo-style ticker such as `RELIANCE.NS`
- Downloads historical OHLCV data
- Calculates 50/100/200-day simple moving averages
- Calculates RSI(14) and MACD
- Resamples data to weekly and monthly candles
- Detects basic candle patterns
- Produces a Streamlit dashboard and technical bias

## Run on Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Important
This is an educational technical-analysis system. The bias is a rule-based interpretation of indicators, not a guaranteed prediction. Validate data quality and add a licensed/contracted market-data provider before using it for production trading decisions.

For production, add:
- authenticated market-data API
- database/cache
- scheduled data refresh
- backtesting
- alerting
- authentication/RBAC
- audit logs
- optional LLM explanation layer
