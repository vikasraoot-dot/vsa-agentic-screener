#!/usr/bin/env python3
"""
Simple targeted indentation fix for run_real_backtest.py
"""

def fix_simple_indentation():
    """Fix the specific indentation issues"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []

        # Read the file and identify the problematic areas
        for i, line in enumerate(lines):
            # Line 32 should be indented after the try on line 31
            if i == 31:  # 0-indexed, so line 32
                if 'with open(filename' in line and not line.startswith('    '):
                    fixed_lines.append('    ' + line.lstrip())
                    continue

            # Lines 33-35 should be indented (inside the with block)
            elif i in [32, 33, 34]:  # lines 33-35
                if line.strip() and not line.startswith('    '):
                    fixed_lines.append('    ' + line.lstrip())
                    continue

            # Line 37 should be indented (except block)
            elif i == 36:  # line 37
                if 'except FileNotFoundError' in line and not line.startswith('    '):
                    fixed_lines.append('    ' + line.lstrip())
                    continue

            # Lines 38-39 should be indented (inside except block)
            elif i in [37, 38]:  # lines 38-39
                if line.strip() and not line.startswith('    '):
                    fixed_lines.append('    ' + line.lstrip())
                    continue

            # Keep other lines as is
            fixed_lines.append(line)

        # Write back the fixed content
        content = '\n'.join(fixed_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Applied simple indentation fixes")
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
                              capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("PERFECT: All indentation errors fixed!")
            print("File compiles successfully!")
            return True
        else:
            print("Still has errors:")
            error_lines = result.stderr.split('\n')[:5]
            for line in error_lines:
                if line.strip():
                    print(f"  {line}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("Simple indentation fix for run_real_backtest.py")
    print("="*50)

    if fix_simple_indentation():
        print("\nTesting fix...")
        if test_fix():
            print("\n" + "="*50)
            print("SUCCESS! ALL INDENTATION ERRORS FIXED!")
            print("Ready to run VSA backtest")
            print("\nRUN YOUR BACKTEST NOW:")
            print("python run_real_backtest.py")
            print("="*50)
        else:
            print("\nStill has indentation errors")
    else:
        print("\nFix failed")