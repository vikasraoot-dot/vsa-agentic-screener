import pandas as pd
import numpy as np

def calculate_spread(df):
    """
    Calculates the spread (High - Low) for each bar.
    Appends 'Spread' column to df.
    """
    df['Spread'] = df['High'] - df['Low']
    return df

def calculate_clv(df):
    """
    Calculates Close Location Value (CLV).
    Formula: ((Close - Low) - (High - Close)) / (High - Low)
    Range: -1 (Low) to +1 (High).
    Appends 'CLV' column to df.
    Handles division by zero (if High == Low) by setting CLV to 0.
    """
    high_low_diff = df['High'] - df['Low']
    # Avoid division by zero
    high_low_diff.replace(0, 0.0001, inplace=True) 
    
    df['CLV'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / high_low_diff
    return df

def calculate_relative_volume(df, sma_period=20):
    """
    Calculates Relative Volume (Vol / SMA_Vol).
    Appends 'VolSMA' and 'RelVol' columns to df.
    """
    df['VolSMA'] = df['Volume'].rolling(window=sma_period).mean()
    # Avoid division by zero
    filled_sma = df['VolSMA'].replace(0, 1)
    df['RelVol'] = df['Volume'] / filled_sma
    return df

def calculate_average_spread(df, sma_period=20):
    """
    Calculates SMA of Spread to determine if current spread is wide or narrow.
    Appends 'SpreadSMA' column to df.
    """
    if 'Spread' not in df.columns:
        df = calculate_spread(df)
    df['SpreadSMA'] = df['Spread'].rolling(window=sma_period).mean()
    return df

def prepare_vsa_features(df, sma_period=20):
    """
    Runs all VSA calculations on the dataframe.
    """
    df = calculate_spread(df)
    df = calculate_clv(df)
    df = calculate_relative_volume(df, sma_period)
    df = calculate_average_spread(df, sma_period)
    return df

def check_no_supply(row, prev_close):
    """
    Checks for 'No Supply' pattern on a single row (pandas Series).
    Definition:
    1. Close < Open (Down bar) OR Close < Prev Close (Down move)
    2. Narrow Spread (Spread < SpreadSMA * 0.8)
    3. Low Volume (RelVol < 0.8)
    """
    # Check for Down move (Comparing to previous close is strictly better, but if unavailable, use bar color)
    is_down = row['Close'] < prev_close
    
    is_narrow = row['Spread'] < (row['SpreadSMA'] * 0.85)
    is_low_vol = row['RelVol'] < 0.85
    
    return is_down and is_narrow and is_low_vol

def check_stopping_volume(row, prev_close):
    """
    Checks for 'Stopping Volume' / 'Absorption' pattern.
    Definition:
    1. Down move
    2. High Volume (RelVol > 1.5)
    3. Close off the lows (CLV > -0.5, preferably > 0)
    """
    is_down = row['Close'] < prev_close
    is_high_vol = row['RelVol'] > 1.5
    # Close is not at the very bottom (absorption happening)
    is_absorbing = row['CLV'] > -0.25 
    
    return is_down and is_high_vol and is_absorbing

def check_test_rising(row, prev_close):
    """
    Checks for a 'Test' in a rising trend.
    Simplification: Down Bar, Low Volume, CLV not at bottom.
    """
    is_down = row['Close'] < prev_close
    is_low_vol = row['RelVol'] < 0.8
    not_bottom = row['CLV'] > -0.8
    

# --- VSA SEQUENCE LOGIC ---

def identify_anchor_bar(row, prev_close):
    """
    Identifies if a bar is a potential 'Anchor' (Stopping Volume or Buying Climax).
    Returns: 'STOPPING_VOLUME' (Bullish), 'BUYING_CLIMAX' (Bearish), or None.
    """
    is_down = row['Close'] < prev_close
    is_up = row['Close'] > prev_close
    
    # Ultra High Volume is a key characteristic for Anchors
    is_high_vol = row['RelVol'] > 1.8 
    
    # STOPPING VOLUME: High Vol + Down Move + Close off lows
    if is_down and is_high_vol and row['CLV'] > -0.25:
        return 'STOPPING_VOLUME'
        
    # BUYING CLIMAX / UPTHRUST: High Vol + Up Move + Close off highs (selling into strength)
    # OR: High Vol + Down Move + Close on lows (Supply Swamping Demand) - but that's weakness, not necessarily an anchor for a test.
    # We focus on the classic "Buying Climax" where professionals sell into the public buying.
    if is_high_vol and row['CLV'] < 0.25:
        if is_up:
            return 'BUYING_CLIMAX'
        elif is_down:
            return 'SUPPLY_DOMINANCE'
        
    return None

def identify_test_bar(row, prev_close, type='BULLISH'):
    """
    Identifies if a bar is a 'Test' (Bullish) or 'No Demand' (Bearish).
    type: 'BULLISH' checks for Test (Supply exhausted)
          'BEARISH' checks for No Demand (Demand exhausted)
    """
    is_low_vol = row['RelVol'] < 0.85
    
    if type == 'BULLISH':
        # TEST: Down move or narrow range, low volume, ideally closing off lows
        is_down = row['Close'] < prev_close
        is_narrow = row['Spread'] < (row['SpreadSMA'] * 0.85)
        not_bottom = row['CLV'] > -0.8
        
        # Scenario A: Down bar on low vol (Standard Test)
        if is_down and is_low_vol and not_bottom:
            return True
        # Scenario B: Narrow spread bar on low vol (No Supply)
        if is_narrow and is_low_vol:
            return True
            
    elif type == 'BEARISH':
        # NO DEMAND: Up move on low volume, closing off highs
        is_up = row['Close'] > prev_close
        not_top = row['CLV'] < 0.8
        
        if is_up and is_low_vol and not_top:
            return True
        
        # Also check for narrow spread up bar (Weak Rally)
        is_narrow = row['Spread'] < (row['SpreadSMA'] * 0.85)
        if is_up and is_narrow and is_low_vol:
            return True
            
    return False

def check_vsa_sequence(df, lookback=5):
    """
    Scans the last 'lookback' bars for a VSA Sequence.
    Bullish: Anchor (Stopping Vol) -> Primary Test -> Secondary Test (Optional)
    Bearish: Anchor (Buying Climax) -> Primary No Demand -> Secondary No Demand (Optional)
    
    Returns a dict with sequence details.
    """
    # Ensure we have enough data
    if len(df) < lookback + 1:
        return {"signal": "NONE", "verdict": "NEUTRAL"}
    
    subset = df.iloc[-(lookback+1):] # Take lookback + 1 to have prev_close for the first bar of lookback
    
    # Trackers
    anchor_found = None # (Type, Date/Index)
    primary_test = None # (Date/Index)
    secondary_test = None # (Date/Index)
    
    # 1. Scan for Anchor
    # We scan from the start of the window up to the 2nd to last bar (need space for test)
    # Using integer indexing on the subset
    
    potential_signals = []
    
    # Convert to list of dicts for easier iteration with index tracking related to original dates if needed
    # But for now, we just need relative position in the window.
    
    dates = subset.index.tolist()
    
    for i in range(1, len(subset)):
        curr_row = subset.iloc[i]
        prev_close = subset.iloc[i-1]['Close']
        date_str = dates[i].strftime('%Y-%m-%d')
        
        # Check patterns
        anchor_type = identify_anchor_bar(curr_row, prev_close)
        
        if anchor_type:
            # Found an anchor. Now look ahead for tests.
            anchor_found = (anchor_type, date_str, i)
            
            # Reset tests for this new anchor candidate
            primary_test = None
            secondary_test = None
            
            test_type_target = 'BULLISH' if anchor_type == 'STOPPING_VOLUME' else 'BEARISH'
            
            # Scan forward from anchor
            for j in range(i + 1, len(subset)):
                test_row = subset.iloc[j]
                test_prev = subset.iloc[j-1]['Close']
                test_date = dates[j].strftime('%Y-%m-%d')
                
                if identify_test_bar(test_row, test_prev, type=test_type_target):
                    if not primary_test:
                        primary_test = (test_date, j)
                    elif not secondary_test:
                        secondary_test = (test_date, j)
            
            # Evaluate this sequence
            status = "NONE"
            if primary_test and secondary_test:
                status = "CONFIRMED_STRONG"
            elif primary_test:
                status = "CONFIRMED_EARLY"
            else:
                status = "WATCH_FOR_TEST"
                
            signal = {
                "signal": "DETECTED",
                "type": anchor_type,
                "status": status,
                "anchor_date": anchor_found[1],
                "test1_date": primary_test[0] if primary_test else None,
                "test2_date": secondary_test[0] if secondary_test else None
            }
            potential_signals.append(signal)

    # Return the most recent/relevant signal
    if not potential_signals:
         return {"signal": "NONE", "verdict": "NEUTRAL"}
         
    # Prioritize the "freshest" sequence or the most confirmed one?
    # Usually the most recent Anchor is the dominant context.
    return potential_signals[-1]

