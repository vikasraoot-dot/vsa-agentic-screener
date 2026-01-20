#!/usr/bin/env python3
"""
Comprehensive indentation fix for run_real_backtest.py
Fixes all indentation issues throughout the file
"""

def fix_all_indentation():
    """Fix all indentation issues in the file"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []
        in_function = False

        for i, line in enumerate(lines):
            # Track if we're inside a function
            if line.startswith('def '):
                in_function = True
                fixed_lines.append(line)  # Function definition stays as-is
                continue
            elif line.startswith('if __name__') or (line.startswith('def ') and in_function):
                in_function = False  # End of previous function or start of main block

            # Fix indentation for lines inside functions
            if in_function and line.strip():  # Non-empty lines in functions
                # Remove existing indentation
                stripped = line.lstrip()
                # Add proper 4-space indentation
                fixed_line = '    ' + stripped
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        # Write back the fixed content
        content = '\n'.join(fixed_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Applied comprehensive indentation fixes")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_comprehensive_fix():
    """Test if all indentation issues are resolved"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("SUCCESS: All indentation errors fixed!")
            print("File compiles perfectly!")
            return True
        else:
            print(f"Still has errors:")
            error_lines = result.stderr.split('\n')[:10]
            for line in error_lines:
                if line.strip() and not line.startswith('Sorry:'):
                    print(f"  {line}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Comprehensive indentation fix for run_real_backtest.py")
    print("="*60)

    if fix_all_indentation():
        print("\n🧪 Testing comprehensive fix...")
        if test_comprehensive_fix():
            print("\n" + "="*60)
            print("🎉 PERFECT! ALL INDENTATION ERRORS FIXED!")
            print("✅ File compiles successfully")
            print("✅ Ready to run VSA backtest")
            print("\n🚀 RUN YOUR BACKTEST NOW:")
            print("   python run_real_backtest.py")
            print("="*60)
        else:
            print("\n❌ Still has indentation errors - check output above")
    else:
        print("\n❌ Comprehensive fix failed")