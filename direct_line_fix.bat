@echo off
REM Direct fix for line 70 syntax error
echo ========================================
echo 🔧 Direct Line 70 Fix
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running direct line fix...
python direct_line_fix.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause