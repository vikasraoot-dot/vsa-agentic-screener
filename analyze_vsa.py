import json
import os
import logging
import anthropic
import time
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_FILE = 'filtered_tickers.json'
OUTPUT_FILE = 'vsa_results.json'

# Claude Opus 4.5 model ID
CLAUDE_MODEL = "claude-opus-4-5-20251101"

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

def analyze_batch(batch_data, market_context):
    """Analyze a batch of tickers using Claude Opus 4.5 via the Anthropic API."""
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    # System prompt for VSA analysis
    system_instruction = """You are a Master Volume Spread Analysis (VSA) Expert with deep knowledge of Wyckoff methodology and institutional trading patterns.

Analyze the provided stock data for multiple tickers. For EACH ticker, provide a comprehensive VSA assessment.

For EACH ticker, output a JSON object with these keys:
- "ticker": string (the stock symbol)
- "vsa_status": string (e.g., "Stopping Volume", "No Supply Test", "Buying Climax", "Supply Dominance", "Effort vs Result Divergence")
- "verdict": string ("BULLISH", "BEARISH", or "NEUTRAL")
- "smart_money_logic": string (2-3 sentences explaining the volume/price behavior and what smart money is likely doing)
- "key_levels": list of strings (important support/resistance levels with prices)
- "setup_stage": string ("Ready for Entry", "Ready for Exit", "Monitoring", "Wait for Confirmation")
- "entry_trigger": string (specific price action that would trigger a trade)
- "invalidation_level": string (price level where the setup fails)

IMPORTANT: Output ONLY a valid JSON array of objects. No markdown, no code blocks, no explanation text outside the JSON. Example format:
[{"ticker": "AAPL", "vsa_status": "...", ...}, {"ticker": "MSFT", "vsa_status": "...", ...}]"""

    # Build the user prompt with ticker data
    user_prompt = f"Market Context: {market_context}\n\nAnalyze the following tickers:\n"

    for ticker, data in batch_data.items():
        user_prompt += f"\n--- Ticker: {ticker} ---\n"
        user_prompt += f"Algorithmic Detection: {data.get('reason')}\n"
        user_prompt += f"Quarterly Context: {data.get('quarterly_context', 'N/A')}\n"

        w_sig = data.get('weekly_signal', {})
        m_sig = data.get('monthly_signal', {})
        user_prompt += f"Weekly Sequence: {w_sig.get('type')} ({w_sig.get('status')})\n"
        user_prompt += f"Monthly Sequence: {m_sig.get('type')} ({m_sig.get('status')})\n"

        # Include recent price/volume data (last 5 weekly, 3 monthly)
        weekly_subset = dict(list(data.get('weekly_data', {}).items())[-5:])
        monthly_subset = dict(list(data.get('monthly_data', {}).items())[-3:])
        user_prompt += f"Weekly Data (last 5 bars): {json.dumps(weekly_subset)}\n"
        user_prompt += f"Monthly Data (last 3 bars): {json.dumps(monthly_subset)}\n"

    max_retries = 5
    base_delay = 30

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=8192,
                system=system_instruction,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Extract text from response
            text = response.content[0].text
            text = text.replace("```json", "").replace("```", "").strip()

            # Ensure it's a list
            if text.startswith('{'):
                text = f"[{text}]"

            return json.loads(text)

        except anthropic.RateLimitError as e:
            wait_time = base_delay * (attempt + 1) + 10
            logging.warning(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            continue

        except anthropic.APIError as e:
            logging.error(f"Anthropic API error: {e}")
            if attempt < max_retries - 1:
                wait_time = base_delay * (attempt + 1)
                logging.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            return []

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {e}")
            logging.debug(f"Raw response: {text[:500]}...")
            return []

        except Exception as e:
            logging.error(f"Unexpected error analyzing batch: {e}")
            return []

    return []

def run_analysis():
    tickers_data = load_filtered_tickers()
    if not tickers_data:
        logging.info("No tickers to analyze.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    # Passthrough Mode if API Key is missing
    if not api_key:
        logging.warning("ANTHROPIC_API_KEY not set. Running in PASSTHROUGH MODE (Algo signals only).")
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

    logging.info(f"Using Claude Opus 4.5 ({CLAUDE_MODEL}) for VSA analysis...")

    # Fetch Market Context
    logging.info("Fetching Market Context (SPY)...")
    market_context = get_market_context()
    logging.info(f"Context: {market_context}")

    # Batching config - Claude handles larger context, but we batch for reliability
    BATCH_SIZE = 30  # Slightly smaller batches for more detailed analysis per ticker

    results = {}
    ticker_list = list(tickers_data.keys())
    total_batches = (len(ticker_list) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(ticker_list), BATCH_SIZE):
        batch_num = i // BATCH_SIZE + 1
        batch_keys = ticker_list[i:i + BATCH_SIZE]
        batch_data = {k: tickers_data[k] for k in batch_keys}

        logging.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_keys)} tickers): {batch_keys[:5]}{'...' if len(batch_keys) > 5 else ''}")

        batch_results = analyze_batch(batch_data, market_context)

        # Merge results
        if isinstance(batch_results, list):
            for res in batch_results:
                ticker = res.get('ticker')
                if ticker:
                    if ticker not in batch_keys:
                        logging.warning(f"LLM returned unexpected ticker {ticker} not in batch")
                    else:
                        # Merge LLM results with Algorithmic data
                        # We prioritize Algo data for 'Priority' and 'Signals', LLM for 'Verdict' and 'Logic'
                        combined = tickers_data[ticker].copy()
                        combined.update(res)

                        # Explicitly keep Algo Priority if it exists (LLM doesn't calculate it)
                        if 'priority' in tickers_data[ticker]:
                            combined['priority'] = tickers_data[ticker]['priority']

                        results[ticker] = combined

            logging.info(f"Batch {batch_num} complete: {len([r for r in batch_results if r.get('ticker') in batch_keys])}/{len(batch_keys)} tickers analyzed")
        else:
            logging.warning(f"Batch {batch_num} returned no results")

        # Buffer between batches to avoid rate limits
        if i + BATCH_SIZE < len(ticker_list):
            time.sleep(10)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Analysis complete. {len(results)}/{len(tickers_data)} tickers analyzed. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_analysis()
