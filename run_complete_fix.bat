@echo off
REM Complete fix for all VSA backtest syntax errors
echo ========================================
echo 🔧 Complete VSA Syntax Error Fix
echo ========================================
echo.

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

echo Running complete syntax fix...
python complete_syntax_fix.py

echo.
echo If successful, run: python test_backtest_setup.py
echo Then run: python run_real_backtest.py
echo.
pause