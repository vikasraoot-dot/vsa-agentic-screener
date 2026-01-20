#!/usr/bin/env python3
"""
Manual fix for run_real_backtest.py syntax errors
"""

def read_and_fix_file():
    """Read the file and manually fix the syntax errors"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        # Read the entire file
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        print("Original problematic section:")
        lines = content.split('\n')
        for i in range(68, 75):
            if i < len(lines):
                print(f"Line {i+1}: {repr(lines[i])}")

        # Fix line 70 - the issue seems to be with the checkmark emoji and line continuation
        # Replace the problematic section
        old_section = '''    print("\\n✅ Validation Results:")
✅ Validation Results:")No results to analyze")'''

        new_section = '''    print("\\n✅ Validation Results:")
    print("No results to analyze")'''

        if old_section in content:
            content = content.replace(old_section, new_section)
            print("✅ Fixed the malformed section")

        # Also fix any remaining unterminated strings
        content = content.replace('print("\\n✅ Validation Results:")✅ Validation Results:")', 'print("\\n✅ Validation Results:")')

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ File fixed")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_syntax():
    """Test if syntax is now correct"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-c', '''
import sys
sys.path.insert(0, r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw")
try:
    import run_real_backtest
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
except Exception as e:
    print(f"⚠️ Other Error: {e}")
'''], capture_output=True, text=True, timeout=15)

        print("Test output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return "Syntax OK" in result.stdout

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Manual fix for run_real_backtest.py")
    if read_and_fix_file():
        if test_syntax():
            print("\n🎉 SUCCESS! Ready to run backtest")
            print("🚀 Run: python run_real_backtest.py")
        else:
            print("\n❌ Still has syntax errors")
    else:
        print("\n❌ Fix failed")