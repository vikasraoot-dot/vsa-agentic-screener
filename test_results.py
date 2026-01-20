#!/usr/bin/env python3
"""Test what the backtest function returns"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from run_real_backtest import run_real_vsa_backtest
import logging
logging.basicConfig(level=logging.ERROR)

tickers = ['AAPL', 'MSFT']
print(f"Testing backtest with tickers: {tickers}")

try:
    results = run_real_vsa_backtest(tickers, '2023-01-01', '2024-01-01')
    print('Results type:', type(results))
    if isinstance(results, dict):
        print('Results keys:', list(results.keys()))
        for key, value in results.items():
            print(f"  {key}: {type(value)} - {str(value)[:100]}...")
    else:
        print('Results:', results)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()