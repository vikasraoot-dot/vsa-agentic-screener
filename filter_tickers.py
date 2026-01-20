import yfinance as yf
import pandas as pd
import json
import os
import logging
import vsa_utils
import time
import requests_cache

# Enable caching to avoid hitting API repeatedly for same data
requests_cache.install_cache('yfinance_cache', expire_after=3600) # Cache for 1 hour

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import sys

def get_ticker_file():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return 'tickers.txt'

TICKER_FILE = get_ticker_file()
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



def process_tickers():
    tickers = load_tickers(TICKER_FILE)
    logging.info(f"Loaded {len(tickers)} tickers.")
    
    filtered_results = {}
    
    for ticker in tickers:
        try:
            df_weekly, df_monthly = get_data(ticker)
            
            if df_weekly is None or df_monthly is None:
                continue
                
            # Rate limit respect
            time.sleep(0.1) # Small delay to be nice to API
                
            # Prepare VSA Features (Calculate RelVol, CLV, Spread)
            df_weekly = vsa_utils.prepare_vsa_features(df_weekly)
            df_monthly = vsa_utils.prepare_vsa_features(df_monthly)
            
            # 1. Quarterly Context (Resample Monthly)
            df_quarterly = df_monthly.resample('3ME').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
            
            # Simple Trend Logic for Quarterly
            q_context = "NEUTRAL"
            if len(df_quarterly) >= 2:
                last_q = df_quarterly.iloc[-1]
                prev_q = df_quarterly.iloc[-2]
                if last_q['Close'] > prev_q['Close']:
                    q_context = "BULLISH_TREND"
                else:
                    q_context = "BEARISH_TREND"

            # 2. Run Sequence Logic
            weekly_seq = vsa_utils.check_vsa_sequence(df_weekly)
            monthly_seq = vsa_utils.check_vsa_sequence(df_monthly)
            
            # Filter Logic: Keep if ANY sequence detected OR Monthly Context is strong
            has_signal = (weekly_seq['signal'] != 'NONE') or (monthly_seq['signal'] != 'NONE')
            
            if has_signal:
                logging.info(f"MATCH: {ticker} | W:{weekly_seq.get('status')} M:{monthly_seq.get('status')}")
                
                # Setup serialization
                def serialize_df(df, n=25):
                    subset = df.tail(n).copy()
                    subset.index = subset.index.strftime('%Y-%m-%d')
                    feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Spread', 'CLV', 'RelVol']
                    available_cols = [c for c in feature_cols if c in df.columns]
                    return subset[available_cols].to_dict(orient='index')

                # Calculate Trend Helper
                def get_trend(df):
                    if len(df) < 20: return "NEUTRAL"
                    sma20 = df['Close'].rolling(20).mean().iloc[-1]
                    close = df['Close'].iloc[-1]
                    return "BULLISH_TREND" if close > sma20 else "BEARISH_TREND"

                w_trend = get_trend(df_weekly)
                m_trend = get_trend(df_monthly)

                # Fetch Daily Data for context (last 60 days)
                stock_daily = yf.Ticker(ticker)
                df_daily = stock_daily.history(period="6mo", interval="1d")
                df_daily = vsa_utils.prepare_vsa_features(df_daily)
                
                # Check Daily Confirmation (Micro-Test)
                daily_conf = "NONE"
                if len(df_daily) > 5:
                    last_5_daily = df_daily.iloc[-5:]
                    # Simple check: Any test/no supply bar in last 3 days?
                    for i in range(-3, 0):
                        row = last_5_daily.iloc[i]
                        prev = last_5_daily.iloc[i-1]['Close']
                        type_target = 'BULLISH' if "STOPPING" in weekly_seq.get('type', '') else 'BEARISH'
                        if vsa_utils.identify_test_bar(row, prev, type=type_target):
                            daily_conf = "TEST_OBSERVED"
                            break

                current_price = df_daily['Close'].iloc[-1]
                
                # Determine Priority
                priority = "LOW"
                w_status = weekly_seq.get('status', 'NONE') # CONFIRMED_STRONG/EARLY/WATCH
                m_status = monthly_seq.get('status', 'NONE')
                
                is_w_confirmed = "CONFIRMED" in w_status
                is_m_confirmed = "CONFIRMED" in m_status
                
                # Logic per Plan
                if is_m_confirmed and is_w_confirmed:
                    priority = "VERY_HIGH"
                elif (is_m_confirmed and "WATCH" in w_status) or (is_m_confirmed and not is_w_confirmed):
                    # Monthly confirmed but weekly just watching or none
                     priority = "MEDIUM" # Downgraded slightly as we want weekly trigger
                elif "BULLISH" in q_context and is_w_confirmed:
                     priority = "HIGH"
                elif is_w_confirmed:
                     priority = "MEDIUM"
                elif "WATCH" in w_status:
                     priority = "LOW"

                filtered_results[ticker] = {
                    'reason': f"Weekly:{weekly_seq.get('type')} status:{w_status}",
                    'ticker': ticker,
                    
                    # Context & Signals
                    'quarterly_context': q_context,
                    'monthly_context': m_trend,
                    'weekly_context': w_trend,
                    'monthly_signal': monthly_seq,
                    'weekly_signal': weekly_seq,
                    'daily_confirmation': daily_conf,
                    'priority': priority,
                    
                    # Raw data for LLM
                    'weekly_data': serialize_df(df_weekly),
                    'monthly_data': serialize_df(df_monthly),
                    'daily_data': serialize_df(df_daily, n=60),
                    
                    # For CSV direct output (Latest bar stats)
                    'latest_weekly_clv': round(df_weekly['CLV'].iloc[-1], 2),
                    'latest_weekly_relvol': round(df_weekly['RelVol'].iloc[-1], 2),
                    'current_price': round(current_price, 2)
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
