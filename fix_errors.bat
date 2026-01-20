@echo off
REM Fix VSA backtest syntax errors
echo Fixing VSA backtest syntax errors...

cd /d C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw

python fix_syntax_errors.py

echo.
echo If successful, run: python test_backtest_setup.py
echo.
pause