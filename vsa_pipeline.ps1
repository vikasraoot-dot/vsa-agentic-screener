$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "STEP: $Message" -ForegroundColor Cyan
    Write-Host "========================================================"
}

function Check-Python {
    try {
        python --version | Out-Null
        Write-Host "Python detected." -ForegroundColor Green
    }
    catch {
        Write-Error "Python not found! Please install Python to run this screener."
    }
}

# --- MAIN ---

Write-Step "Checking Environment"
Check-Python

# Optional: Install requirements if flag passed, but skipping for now to be fast.
# pip install -r requirements.txt

Write-Step "1. Filtering Tickers (filter_tickers.py)"
# We can use a test file if provided as argument, else default
$TickerFile = "tickers.txt"
if ($args.Count -gt 0) {
    if ($args[0] -eq "--test") {
        $TickerFile = "test_tickers.txt"
        Write-Host "Running in TEST mode with test_tickers.txt" -ForegroundColor Yellow
        # Create dummy test file if not exists
        if (-not (Test-Path "test_tickers.txt")) {
            "AAPL`nMSFT`nTSLA`nNVDA`nAMD" | Set-Content "test_tickers.txt"
        }
    }
}

# Run Filter
# Note: filter_tickers.py currently hardcodes 'tickers.txt'. 
# We might need to modify filter_tickers.py to accept an arg, perfectly fitting the "amends" part of the request.
# For now, let's swap files if testing.

if ($TickerFile -eq "test_tickers.txt") {
    Copy-Item "tickers.txt" "tickers.txt.bak"
    Copy-Item "test_tickers.txt" "tickers.txt"
}

try {
    python filter_tickers.py
    if ($LASTEXITCODE -ne 0) { throw "Filtering failed." }
}
finally {
    # Restore original tickers if we swapped
    if ($TickerFile -eq "test_tickers.txt") {
        Move-Item "tickers.txt.bak" "tickers.txt" -Force
    }
}

Write-Step "2. Analyzing VSA Signals (analyze_vsa.py)"
# Check API Key
if (-not $env:GEMINI_API_KEY) {
    Write-Host "WARNING: GEMINI_API_KEY not set. Running in PASSTHROUGH MODE." -ForegroundColor Yellow
}
else {
    Write-Host "Gemini API Key detected. Running Full Analysis." -ForegroundColor Green
}

python analyze_vsa.py
if ($LASTEXITCODE -ne 0) { throw "Analysis failed." }

Write-Step "3. Generating Reports (generate_report.py)"
python generate_report.py
if ($LASTEXITCODE -ne 0) { throw "Report generation failed." }

Write-Step "SUCCESS! Reports generated in /reports directory."
