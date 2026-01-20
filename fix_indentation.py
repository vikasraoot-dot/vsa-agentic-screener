#!/usr/bin/env python3
"""
Fix indentation errors in run_real_backtest.py
"""

def fix_indentation():
    """Fix all indentation issues in the file"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.read().split('\n')

        fixed_lines = []

        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                continue

            # Check if this line should be indented (inside a function)
            # We're looking for lines that are inside the analyze_backtest_results function
            # These should be indented with 4 spaces

            # Find the function boundaries (approximate)
            if 'def analyze_backtest_results' in line:
                in_function = True
                fixed_lines.append(line)  # Function definition - no indent needed
                continue
            elif line.startswith('def ') and 'analyze_backtest_results' not in line:
                in_function = False  # New function starts

            # Fix indentation for lines that should be indented
            if in_function and not line.startswith('    ') and not line.startswith('\t'):
                # This line should be indented
                if line.startswith('print') or line.startswith('#') or line.startswith('for ') or line.startswith('if '):
                    fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        # Write back the fixed content
        content = '\n'.join(fixed_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Fixed indentation issues")
        return True

    except Exception as e:
        print(f"Error fixing indentation: {e}")
        return False

def test_indentation_fix():
    """Test if indentation is now correct"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("SUCCESS: Indentation errors fixed!")
            return True
        else:
            print(f"Still has errors: {result.stderr[:300]}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing indentation errors")
    if fix_indentation():
        if test_indentation_fix():
            print("\\n✅ READY TO RUN BACKTEST!")
            print("Run: python run_real_backtest.py")
        else:
            print("\\n❌ Still has indentation errors")
    else:
        print("\\n❌ Fix failed")