#!/usr/bin/env python3
"""
Simple fix for run_real_backtest.py
"""

def fix_file():
    """Simple direct fix"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find and replace the problematic section
        # The issue is around line 70-85 where there are malformed print statements

        # Replace the broken section with correct code
        old_broken = '''    print("\\n✅ Validation Results:")
✅ Validation Results:")No results to analyze")'''

        new_correct = '''    print("\\n✅ Validation Results:")
    print("No results to analyze")'''

        if old_broken in content:
            content = content.replace(old_broken, new_correct)
            print("✅ Fixed malformed print statements")

        # Also fix any remaining unterminated strings
        content = content.replace('print("\\n✅ Validation Results:")✅ Validation Results:")', 'print("\\n✅ Validation Results:")')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ File fixed successfully")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_file():
    """Test if file compiles"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Syntax OK - Ready to run!")
            return True
        else:
            print(f"❌ Still syntax error: {result.stderr[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple fix for run_real_backtest.py")
    if fix_file():
        test_file()
    print("\\n🚀 Now run: python run_real_backtest.py")