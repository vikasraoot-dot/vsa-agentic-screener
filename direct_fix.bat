@echo off
REM Direct fix for run_real_backtest.py syntax error
echo ========================================
echo 🔧 Direct Fix for run_real_backtest.py
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running direct fix...
python direct_fix.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause