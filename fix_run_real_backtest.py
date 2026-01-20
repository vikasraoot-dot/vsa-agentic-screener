#!/usr/bin/env python3
"""
Fix syntax error in run_real_backtest.py
"""

def fix_run_real_backtest():
    """Fix the syntax error in run_real_backtest.py"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # The issue is around line 85 where there's an unterminated string
        # Let's find and fix the problematic area
        lines = content.split('\n')

        # Check if we can identify the problematic line
        for i, line in enumerate(lines):
            if i + 1 == 85:  # Line 85 (0-indexed as 84)
                print(f"Line 85 content: {repr(line)}")
                if line.strip().startswith('print("\\n') and not line.strip().endswith('")'):
                    print("Found unterminated string at line 85")
                    # This line is incomplete, let's look at surrounding context
                    context_start = max(0, i-2)
                    context_end = min(len(lines), i+5)
                    print("Context:")
                    for j in range(context_start, context_end):
                        marker = " <-- PROBLEM" if j == i else ""
                        print(f"  {j+1}: {repr(lines[j])}{marker}")

                    # Fix the unterminated string - it looks like it should be part of a larger print statement
                    # Let's look for the next line that might complete it
                    if i+1 < len(lines) and 'breakdown' in lines[i+1]:
                        # Replace the broken line with proper formatting
                        lines[i] = '    print("\\n✅ Validation Results:")'
                        print("Fixed line 85")
                    break

        # Write back the fixed content
        fixed_content = '\n'.join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print("✅ Attempted to fix run_real_backtest.py")
        return True

    except Exception as e:
        print(f"❌ Error fixing run_real_backtest.py: {e}")
        return False

def test_fix():
    """Test that the fix worked"""
    import subprocess
    import sys

    try:
        # Try to compile the file
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ run_real_backtest.py - Syntax OK")
            return True
        else:
            print(f"❌ run_real_backtest.py - Still has syntax error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing fix: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing run_real_backtest.py syntax error")
    fix_run_real_backtest()
    test_fix()