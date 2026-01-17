import yfinance as yf
import pandas as pd
import json
import os
import logging
import vsa_utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKER_FILE = 'tickers.txt'
OUTPUT_FILE = 'filtered_tickers.json'

def load_tickers(filename):
    if not os.path.exists(filename):
        logging.error(f"Ticker file {filename} not found.")
        return []
    with open(filename, 'r') as f:
        return [line.strip().upper() for line in f if line.strip()]

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Weekly Data
        df_weekly = stock.history(period="2y", interval="1wk")
        # Monthly Data
        df_monthly = stock.history(period="5y", interval="1mo") 
        
        if df_weekly.empty or df_monthly.empty:
            logging.warning(f"No data found for {ticker}")
            return None, None

        # Clean empty rows
        df_weekly = df_weekly.dropna()
        df_monthly = df_monthly.dropna()

        return df_weekly, df_monthly
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None, None

def analyze_timeframe(df, timeframe_name):
    """
    Applies VSA logic to a dataframe. 
    Returns a list of detected patterns (strings) for the latest bar.
    """
    if len(df) < 25:
        return []

    # Calculate VSA features
    df = vsa_utils.prepare_vsa_features(df)
    
    # Get the last completed bar (or current bar if evaluating live)
    # Assuming the last row is the one we want to check
    latest = df.iloc[-1]
    prev_close = df['Close'].iloc[-2]
    
    patterns = []
    
    # Check VSA Patterns
    if vsa_utils.check_no_supply(latest, prev_close):
        patterns.append(f"{timeframe_name}_No_Supply")
    
    if vsa_utils.check_stopping_volume(latest, prev_close):
        patterns.append(f"{timeframe_name}_Stopping_Volume")
        
    if vsa_utils.check_test_rising(latest, prev_close):
        patterns.append(f"{timeframe_name}_Test_Observed")
        
    # Effort vs Result (Simplified: High Vol, Small move)
    # if latest['RelVol'] > 1.5 and abs(latest['CLV']) < 0.5:
    #     patterns.append(f"{timeframe_name}_Effort_vs_Result")

    return patterns

def process_tickers():
    tickers = load_tickers(TICKER_FILE)
    logging.info(f"Loaded {len(tickers)} tickers.")
    
    filtered_results = {}
    
    for ticker in tickers:
        try:
            df_weekly, df_monthly = get_data(ticker)
            
            if df_weekly is None or df_monthly is None:
                continue
                
            # Analyze Timeframes
            weekly_patterns = analyze_timeframe(df_weekly, "Weekly")
            monthly_patterns = analyze_timeframe(df_monthly, "Monthly")
            
            all_patterns = weekly_patterns + monthly_patterns
            
            if all_patterns:
                logging.info(f"MATCH: {ticker} | Patterns: {all_patterns}")
                
                # Setup serialization
                def serialize_df(df, n=25):
                    subset = df.tail(n).copy()
                    subset.index = subset.index.strftime('%Y-%m-%d')
                    # Include calculated features in the dump for the LLM
                    feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Spread', 'CLV', 'RelVol']
                    # Ensure columns exist (they should, from analyze_timeframe -> prepare_vsa_features)
                    # Note: We modified the DFs in place in analyze_timeframe, so they have the cols.
                    available_cols = [c for c in feature_cols if c in df.columns]
                    return subset[available_cols].to_dict(orient='index')

                # Fetch Daily Data for context (last 60 days)
                stock_daily = yf.Ticker(ticker)
                df_daily = stock_daily.history(period="6mo", interval="1d")
                # We should calculate features for daily too, to help the LLM
                df_daily = vsa_utils.prepare_vsa_features(df_daily)

                filtered_results[ticker] = {
                    'reason': ", ".join(all_patterns),
                    'patterns': all_patterns, # Keep structural data separate
                    'weekly_data': serialize_df(df_weekly),
                    'monthly_data': serialize_df(df_monthly),
                    'daily_data': serialize_df(df_daily, n=60)
                }

        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")
            continue

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(filtered_results, f, indent=4)
        
    logging.info(f"Saved {len(filtered_results)} filtered tickers to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_tickers()
