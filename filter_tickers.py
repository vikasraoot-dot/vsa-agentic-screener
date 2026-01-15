import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKER_FILE = 'tickers.txt'
OUTPUT_FILE = 'filtered_tickers.json'
SMA_PERIOD = 20

def load_tickers(filename):
    if not os.path.exists(filename):
        logging.error(f"Ticker file {filename} not found.")
        return []
    with open(filename, 'r') as f:
        return [line.strip().upper() for line in f if line.strip()]

def get_data(ticker):
    try:
        # Fetching enough data for Monthly SMA(20) - 2 years is usually sufficient
        stock = yf.Ticker(ticker)
        
        # We need Weekly and Monthly data
        # yfinance doesn't always give perfect weekly/monthly agg via 'interval' without some quirks, 
        # but '1wk' and '1mo' are generally supported.
        
        # Weekly Data
        df_weekly = stock.history(period="2y", interval="1wk")
        # Monthly Data
        df_monthly = stock.history(period="5y", interval="1mo") # 5y to be safe for monthly 20 SMA
        
        if df_weekly.empty or df_monthly.empty:
            logging.warning(f"No data found for {ticker}")
            return None, None

        return df_weekly, df_monthly
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None, None

def check_volume_condition(df, timeframe_name):
    if len(df) < SMA_PERIOD:
        return False, 0, 0

    # Calculate SMA 20 of Volume
    # Note: Volume in yfinance is 'Volume' column
    df['VolSMA20'] = df['Volume'].rolling(window=SMA_PERIOD).mean()
    
    # Check latest completed bar. 
    # yfinance 'latest' bar might be incomplete if market is open. 
    # For weekly/monthly, the last row is often the current incomplete period.
    # The prompt implies "latest weekly and monthly timeframes".
    # If we run this daily, the "latest" weekly/monthly bar is the one currently forming or just finished.
    # Let's assess the *last closed* bar AND the *current* bar to be generous, 
    # or just the last row provided it has significant volume.
    # Let's stick to the last available row for "latest condition".
    
    latest_vol = df['Volume'].iloc[-1]
    latest_sma = df['VolSMA20'].iloc[-1]
    
    # Condition: Volume > SMA(20) * 1.0 (some margin?) Prompt says "> last 20 bars", likely meaning SMA or max? 
    # Prompt says: "volume on latest weekly and monthly timeframes is > last 20 bars"
    # This might mean Volume > Max(Volume of last 20 bars) OR Volume > Average(last 20 bars).
    # The prompt later says "Current bar volume > SMA(Volume, 20)". I will stick to SMA requirement from the plan.
    
    condition_met = latest_vol > latest_sma
    
    return condition_met, latest_vol, latest_sma

def process_tickers():
    tickers = load_tickers(TICKER_FILE)
    logging.info(f"Loaded {len(tickers)} tickers.")
    
    filtered_results = {}
    
    for ticker in tickers:
        logging.info(f"Processing {ticker}...")
        df_weekly, df_monthly = get_data(ticker)
        
        if df_weekly is None or df_monthly is None:
            continue
            
        # Check conditions
        weekly_met, w_vol, w_sma = check_volume_condition(df_weekly, "Weekly")
        monthly_met, m_vol, m_sma = check_volume_condition(df_monthly, "Monthly")
        
        if weekly_met or monthly_met:
            logging.info(f"MATCH: {ticker} | Weekly: {weekly_met} | Monthly: {monthly_met}")
            
            # Serialize data for Gemini
            # We want to pass the last few bars (e.g., 25) of OHLCV to the agent
            
            def serialize_df(df, n=25):
                # Get last n rows, reverse to newest first (optional, but chronological is usually better for sequence models)
                # LLMs handle chronological lists well.
                subset = df.tail(n).copy()
                # Convert index to string date
                subset.index = subset.index.strftime('%Y-%m-%d')
                return subset[['Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='index')

            filtered_results[ticker] = {
                'reason': f"Weekly_Vol_vs_SMA: {weekly_met} ({w_vol:.0f} vs {w_sma:.0f}), Monthly_Vol_vs_SMA: {monthly_met} ({m_vol:.0f} vs {m_sma:.0f})",
                'weekly_data': serialize_df(df_weekly),
                'monthly_data': serialize_df(df_monthly),
                # We also need Daily data for the detailed entry/exit triggers mentioned in prompt
                # Fetch daily data now if matched
            }
            
            # Fetch Daily Data for matched ticker
            try:
                stock_daily = yf.Ticker(ticker)
                df_daily = stock_daily.history(period="6mo", interval="1d")
                filtered_results[ticker]['daily_data'] = serialize_df(df_daily, n=60) # Last 60 days
            except Exception as e:
                logging.error(f"Error fetching daily data for {ticker}: {e}")

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(filtered_results, f, indent=4)
        
    logging.info(f"Saved {len(filtered_results)} filtered tickers to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_tickers()
