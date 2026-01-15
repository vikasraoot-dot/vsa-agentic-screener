import json
import os
import logging
from google import genai
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_FILE = 'filtered_tickers.json'
OUTPUT_FILE = 'vsa_results.json'

def load_filtered_tickers():
    if not os.path.exists(INPUT_FILE):
        return {}
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def analyze_ticker(client, ticker, data):
    # Construct prompt
    system_instruction = """
    Act as a Master Volume Spread Analysis (VSA) Expert. Analyze the provided multi-timeframe data (Monthly, Weekly, Daily).
    The data provided is a JSON object with OHLCV data for specific timeframes.
    
    You must output your analysis in valid JSON format ONLY, with no markdown formatting. The JSON should have the following keys:
    - "vsa_status": string (e.g., "Mark-up", "Absorption", "Stopping Volume", "No Supply", "Test", "Jumping the Creek", etc.)
    - "verdict": string (e.g., "BULLISH", "BEARISH", "NEUTRAL")
    - "correlation_analysis": string (How Monthly/Weekly structure influences Daily setup)
    - "smart_money_logic": string (Intent behind volume spikes)
    - "key_levels": list of strings (e.g. ["Support at 150", "Resistance at 180"])
    - "setup_stage": string (e.g. "Ready for Entry", "Ready for Exit", "Monitoring")
    - "entry_trigger": string (Specific price/volume condition to wait for)
    - "exit_trigger": string
    - "volume_requirement": string
    - "invalidation_level": string
    """
    
    user_prompt = f"""
    Analyze the following data for {ticker}:
    
    Trigger Reason: {data.get('reason')}
    
    Monthly Data (Last 25 bars):
    {json.dumps(data.get('monthly_data', {}), indent=2)}
    
    Weekly Data (Last 25 bars):
    {json.dumps(data.get('weekly_data', {}), indent=2)}
    
    Daily Data (Last 60 bars):
    {json.dumps(data.get('daily_data', {}), indent=2)}
    """
    
    model_id = 'gemini-1.5-flash' # Default
    
    # Dynamic model selection
    try:
        found_model = False
        for m in client.models.list():
            name = m.name.replace('models/', '')
            if 'gemini' in name and 'flash' in name and 'audio' not in name:
                model_id = name
                found_model = True
                break
        
        if not found_model:
            # Fallback to pro if flash not found
             for m in client.models.list():
                name = m.name.replace('models/', '')
                if 'gemini' in name and 'pro' in name:
                    model_id = name
                    break
                    
        logging.info(f"Selected model: {model_id}")
    except Exception as e:
        logging.warning(f"Model listing failed, using default: {e}")

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=system_instruction + "\n\n" + user_prompt
        )
        text = response.text
        # Clean up code blocks if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        logging.error(f"Error analyzing {ticker}: {e}")
        # Try to list models to help debug
        try:
            logging.info("Attempting to list available models for debugging...")
            for m in client.models.list():
                logging.info(f"Available model: {m.name}")
        except Exception as list_e:
            logging.error(f"Could not list models: {list_e}")
            
        return {
            "error": str(e),
            "verdict": "ERROR"
        }

def run_analysis():
    tickers_data = load_filtered_tickers()
    if not tickers_data:
        logging.info("No tickers to analyze.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set")
        return

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        logging.error(f"Configuration failed: {e}")
        return

    results = {}
    
    for ticker, data in tickers_data.items():
        logging.info(f"Analyzing {ticker}...")
        analysis = analyze_ticker(client, ticker, data)
        results[ticker] = analysis
        logging.info(f"Completed {ticker} - Verdict: {analysis.get('verdict')}")
        time.sleep(4) # Rate limiting buffer

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Analysis complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_analysis()
