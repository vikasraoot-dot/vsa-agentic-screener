@echo off
REM Manual fix for indentation errors
echo ========================================
echo 🔧 Manual Indentation Fix
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running manual indentation fix...
python manual_indentation_fix.py

echo.
echo If successful, run: python run_real_backtest.py
echo.
pause