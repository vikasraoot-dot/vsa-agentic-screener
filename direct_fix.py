#!/usr/bin/env python3
"""
Direct fix for run_real_backtest.py line 85
"""

def fix_line_85():
    """Direct fix for the unterminated string"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Replace the broken line
        content = content.replace('    print("', '    print("\\n✅ Validation Results:")', 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Fixed run_real_backtest.py line 85")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fix():
    """Test the fix"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Syntax OK - Ready to run backtest!")
            return True
        else:
            print(f"❌ Still has syntax error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Direct fix for run_real_backtest.py")
    if fix_line_85():
        test_fix()
    print("\n🚀 Now run: python run_real_backtest.py")