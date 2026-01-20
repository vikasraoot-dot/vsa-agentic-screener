#!/usr/bin/env python3
"""
Manual fix for indentation errors in run_real_backtest.py
"""

def fix_indentation_manually():
    """Manually fix the specific indentation errors"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Replace the specific problematic lines with correct indentation
        replacements = [
            # Line 93: incorrect indentation
            ('  print("No results to analyze")', '    print("No results to analyze")'),

            # Line 95: incorrect indentation
            ('        print(f"   • {strength}")', '    print(f"   - {strength}")'),

            # Line 97: incorrect indentation
            ('  print("No results to analyze")', '    print("No results to analyze")'),

            # Line 99: incorrect indentation
            ('        print(f"   • {weakness}")', '    print(f"   - {weakness}")'),
        ]

        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"Fixed: {old.strip()}")

        # Also fix the bullet points to be dashes for better compatibility
        content = content.replace('•', '-')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Manual indentation fixes applied")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_manual_fix():
    """Test if the manual fix worked"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("PERFECT: All indentation errors fixed!")
            return True
        else:
            print(f"Still has errors: {result.stderr[:300]}...")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Manual indentation fix for run_real_backtest.py")
    if fix_indentation_manually():
        if test_manual_fix():
            print("\\n✅ SUCCESS! READY TO RUN BACKTEST!")
            print("Run: python run_real_backtest.py")
        else:
            print("\\n❌ Still has indentation errors")
    else:
        print("\\n❌ Manual fix failed")