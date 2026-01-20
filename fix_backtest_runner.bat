@echo off
REM Fix syntax error in run_real_backtest.py
echo ========================================
echo 🔧 Fix run_real_backtest.py Syntax Error
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running fix for run_real_backtest.py...
python fix_run_real_backtest.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause