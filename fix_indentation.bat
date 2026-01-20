@echo off
REM Fix indentation errors in run_real_backtest.py
echo ========================================
echo 🔧 Fix Indentation Errors
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running indentation fix...
python fix_indentation.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause