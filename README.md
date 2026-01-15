# VSA Agentic Screener

This project implements an automated Volume Spread Analysis (VSA) screener using Python and Google Gemini.

## Overview

The workflow consists of three main steps:
1.  **Filter**: `filter_tickers.py` scans a list of tickers (`tickers.txt`) and selects those where current volume on Weekly or Monthly timeframes is greater than the 20-period SMA.
2.  **Analyze**: `analyze_vsa.py` takes the filtered tickers and their OHLCV data, and sends it to Google Gemini (Pro 1.5) to perform a deep VSA analysis.
3.  **Report**: `generate_report.py` compiles the analysis into a daily Markdown report in the `reports/` folder.

## Setup

### 1. GitHub Secrets
For the automated workflow to work, you must add a repository secret:
-   Go to **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
-   Name: `GEMINI_API_KEY`
-   Value: Your Google AI Studio API Key.

### 2. Ticker List
Edit `tickers.txt` to add or remove tickers you want to scan.

### 3. Local Run
To run locally:
1.  Install dependencies: `pip install -r requirements.txt`
2.  Set API Key: `export GEMINI_API_KEY="your_key"` (Linux/Mac) or `$env:GEMINI_API_KEY="your_key"` (PowerShell)
3.  Run the scripts:
    ```bash
    python filter_tickers.py
    python analyze_vsa.py
    python generate_report.py
    ```

## Output
Reports are saved in `reports/REPORT_YYYY-MM-DD.md`.
