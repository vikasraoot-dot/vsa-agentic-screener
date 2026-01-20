@echo off
REM Simple fix for run_real_backtest.py
echo ========================================
echo 🔧 Simple Fix for run_real_backtest.py
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running simple fix...
python simple_fix.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause