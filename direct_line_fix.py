#!/usr/bin/env python3
"""
Direct fix for the specific line continuation error in run_real_backtest.py
"""

def fix_line_70():
    """Fix the specific line 70 issue"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Replace the malformed line 70
        # The issue is: print("\n Validation Results:")\n Validation Results:")No results to analyze")
        old_malformed = '        print("\\n Validation Results:")\\n Validation Results:")No results to analyze")'

        new_correct = '''        print("\\nValidation Results:")
        print("No results to analyze")'''

        if old_malformed in content:
            content = content.replace(old_malformed, new_correct)
            print("Fixed the malformed line 70")

        # Also fix any other potential issues
        content = content.replace('\\n Validation Results:")\\n Validation Results:")', '')
        content = content.replace('")\\n Validation Results:")No results to analyze")', '')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("File fixed")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_fix():
    """Test if the fix worked"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("SUCCESS: Syntax error fixed!")
            return True
        else:
            print(f"Still has error: {result.stderr[:200]}...")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("Direct fix for line 70 syntax error")
    if fix_line_70():
        if test_fix():
            print("\\nREADY TO RUN BACKTEST!")
            print("Run: python run_real_backtest.py")
        else:
            print("\\nStill has syntax errors")
    else:
        print("\\nFix failed")