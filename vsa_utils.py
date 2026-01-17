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
    
    return is_down and is_low_vol and not_bottom
