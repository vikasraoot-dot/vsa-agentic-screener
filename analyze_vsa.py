import json
import os
import logging
import google.generativeai as genai
import time
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_FILE = 'filtered_tickers.json'
OUTPUT_FILE = 'vsa_results.json'

def load_filtered_tickers():
    if not os.path.exists(INPUT_FILE):
        return {}
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def get_market_context():
    """Calculates SPY context: Trend (SMA20 vs SMA50) and Last Bar VSA."""
    try:
        spy = yf.Ticker("SPY")
        history = spy.history(period="1y", interval="1d")
        if len(history) < 50:
             return "Market Context: Data Unavailable"
        
        # Calculate Trend
        sma20 = history['Close'].rolling(20).mean().iloc[-1]
        sma50 = history['Close'].rolling(50).mean().iloc[-1]
        
        trend = "BULLISH" if sma20 > sma50 else "BEARISH"
        if abs(sma20 - sma50) / sma50 < 0.01:
            trend = "SIDEWAYS/CHOPPY"
            
        # Analysis of last bar
        last_close = history['Close'].iloc[-1]
        prev_close = history['Close'].iloc[-2]
        move = "UP" if last_close > prev_close else "DOWN"
        
        return f"General Market (SPY) Trend: {trend}. Last Day Move: {move}."
    except Exception as e:
        logging.warning(f"Failed to fetch market context: {e}")
        return "Market Context: Data Unavailable"

def analyze_batch(model_id, batch_data, market_context):
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    # Construct prompt for multiple tickers
    system_instruction = """
    Act as a Master Volume Spread Analysis (VSA) Expert. 
    Analyze the provided data for multiple tickers. 
    
    For EACH ticker, you must output a JSON object with the following keys:
    - "ticker": string
    - "vsa_status": string (e.g., "No Supply", "Stopping Volume", "Test", "Effort No Result")
    - "verdict": string (e.g., "BULLISH", "BEARISH", "NEUTRAL")
    - "smart_money_logic": string (Explain volume/price behavior)
    - "key_levels": list of strings
    - "setup_stage": string (e.g. "Ready for Entry", "Monitoring")
    - "entry_trigger": string
    - "invalidation_level": string

    Output must be a JSON LIST of objects, e.g. [{...}, {...}]. 
    Do NOT use markdown code blocks. Just valid JSON.
    """
    
    # Minimize data to fit context and save tokens
    # specific_data will be a compact string representation
    batch_prompt_content = f"Context: {market_context}\n\nAnalyze these tickers:\n"
    
    for ticker, data in batch_data.items():
        batch_prompt_content += f"\n--- Ticker: {ticker} ---\n"
        batch_prompt_content += f"Algo Detection: {data.get('reason')}\n"
        batch_prompt_content += f"Quarterly Context: {data.get('quarterly_context', 'N/A')}\n"
        
        w_sig = data.get('weekly_signal', {})
        m_sig = data.get('monthly_signal', {})
        batch_prompt_content += f"Weekly Sequence: {w_sig.get('type')} ({w_sig.get('status')})\n"
        batch_prompt_content += f"Monthly Sequence: {m_sig.get('type')} ({m_sig.get('status')})\n"
        
        # Only take last 5 weekly and 3 monthly to save tokens, focusing on recent behavior
        weekly_subset = dict(list(data.get('weekly_data', {}).items())[-5:])
        monthly_subset = dict(list(data.get('monthly_data', {}).items())[-3:])
        batch_prompt_content += f"Weekly (last 5): {json.dumps(weekly_subset)}\n"
        batch_prompt_content += f"Monthly (last 3): {json.dumps(monthly_subset)}\n"

    max_retries = 5
    base_delay = 30
    
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content(
                system_instruction + "\n\n" + batch_prompt_content
            )
            text = response.text
            text = text.replace("```json", "").replace("```", "").strip()
            
            # Ensure it's a list
            if text.startswith('{'):
                text = f"[{text}]"
                
            return json.loads(text)
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = base_delay * (attempt + 1) + 10
                logging.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            logging.error(f"Error analyzing batch: {e}")
            return []

    return []

def run_analysis():
    tickers_data = load_filtered_tickers()
    if not tickers_data:
        logging.info("No tickers to analyze.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Passthrough Mode if API Key is missing
    if not api_key:
        logging.warning("GEMINI_API_KEY not set. Running in PASSTHROUGH MODE (Algo signals only).")
        results = {}
        for ticker, data in tickers_data.items():
            # Copy all data
            res = data.copy()
            # Determine Verdict based on signal type
            w_type = data.get('weekly_signal', {}).get('type', 'NONE')
            if 'STOPPING' in w_type or 'TEST' in w_type:
                res['verdict'] = "BULLISH_SETUP"
            elif 'CLIMAX' in w_type or 'DOMINANCE' in w_type:
                res['verdict'] = "BEARISH_SETUP"
            else:
                res['verdict'] = "NEUTRAL"
                
            res['vsa_status'] = data.get('reason', 'Signal Detected')
            results[ticker] = res
            
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(results, f, indent=4)
        logging.info(f"Passthrough complete. Saved {len(results)} results to {OUTPUT_FILE}")
        return

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        logging.error(f"Configuration failed: {e}")
        return

    # Fetch Market Context
    logging.info("Fetching Market Context (SPY)...")
    market_context = get_market_context()
    logging.info(f"Context: {market_context}")

    # Batching config
    BATCH_SIZE = 50
    model_id = 'gemini-flash-latest' # Maps to 1.5 Flash usually
    
    results = {}
    ticker_list = list(tickers_data.keys())
    
    for i in range(0, len(ticker_list), BATCH_SIZE):
        batch_keys = ticker_list[i:i + BATCH_SIZE]
        batch_data = {k: tickers_data[k] for k in batch_keys}
        
        logging.info(f"Processing batch {i//BATCH_SIZE + 1}: {batch_keys}")
        
        batch_results = analyze_batch(model_id, batch_data, market_context)
        
        # Merge results
        if isinstance(batch_results, list):
            for res in batch_results:
                ticker = res.get('ticker')
                if ticker:
                    if ticker not in batch_keys: 
                        logging.warning(f"LLM hallucinated ticker {ticker} not in batch {batch_keys}")
                    else:
                        # Merge LLM results with Algorithmic data
                        # We prioritize Algo data for 'Priority' and 'Signals', LLM for 'Verdict' and 'Logic'
                        combined = tickers_data[ticker].copy()
                        combined.update(res)
                        
                        # Explicitly keep Algo Priority if it exists (LLM doesn't calculate it)
                        if 'priority' in tickers_data[ticker]:
                             combined['priority'] = tickers_data[ticker]['priority']
                             
                        results[ticker] = combined
        
        time.sleep(15) # Buffer between batches
        
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Analysis complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_analysis()
