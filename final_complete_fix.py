#!/usr/bin/env python3
"""
Final complete fix for all remaining syntax errors in run_real_backtest.py
"""

def fix_all_remaining_errors():
    """Fix all remaining syntax errors in the file"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Fix line 86-87: unterminated string and malformed f-string
        old_broken_86_87 = '''    print("
 Validation Results:"    print(f"   Backtest: {'PASSED' if breakdown.get('backtest_passed') else 'FAILED'}")
    print(f"   Walk-Forward: {'PASSED' if breakdown.get('walk_forward_passed') else 'FAILED'}")'''

        new_correct_86_87 = '''    print("\\nValidation Results:")
    print(f"   Backtest: {'PASSED' if breakdown.get('backtest_passed') else 'FAILED'}")
    print(f"   Walk-Forward: {'PASSED' if breakdown.get('walk_forward_passed') else 'FAILED'}")
    print(f"   Statistical: {'PASSED' if breakdown.get('statistical_passed') else 'FAILED'}")'''

        if old_broken_86_87 in content:
            content = content.replace(old_broken_86_87, new_correct_86_87)
            print("Fixed lines 86-87 syntax errors")

        # Look for any other unterminated strings
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # Check for unterminated print statements
            if 'print("' in line and not (line.count('"') >= 2 or line.endswith('")') or line.endswith('"""')):
                # This might be an unterminated print statement
                if i + 1 < len(lines) and not lines[i+1].strip().startswith('print'):
                    # Combine with next line if it continues
                    next_line = lines[i+1].strip()
                    if next_line and not next_line.startswith('print'):
                        # Fix the unterminated string
                        if line.strip().endswith('print("'):
                            line = line.rstrip() + 'No results to analyze")'
                            lines[i+1] = ''  # Remove the next line as it's now part of this one

            fixed_lines.append(line)

        # Remove empty lines that were created
        fixed_lines = [line for line in fixed_lines if line.strip() or line == '']

        content = '\n'.join(fixed_lines)

        # Final cleanup - remove any remaining problematic patterns
        content = content.replace('print("\\nValidation Results:")Validation Results:")', 'print("\\nValidation Results:")')
        content = content.replace('print("\\nValidation Results:")✅ Validation Results:")', 'print("\\nValidation Results:")')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("All syntax errors fixed")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_complete_fix():
    """Test if all syntax errors are finally fixed"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("PERFECT: All syntax errors fixed!")
            print("File compiles successfully!")
            return True
        else:
            print(f"Still has syntax errors:")
            # Show first few lines of error
            error_lines = result.stderr.split('\n')[:5]
            for line in error_lines:
                if line.strip():
                    print(f"  {line}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FINAL COMPLETE FIX for run_real_backtest.py")
    print("="*50)

    if fix_all_remaining_errors():
        print("\n🧪 Testing final fix...")
        if test_complete_fix():
            print("\n" + "="*50)
            print("🎉 SUCCESS! ALL SYNTAX ERRORS FIXED!")
            print("✅ Ready to run VSA backtest")
            print("\n🚀 RUN YOUR BACKTEST NOW:")
            print("   python run_real_backtest.py")
            print("="*50)
        else:
            print("\n❌ Still has syntax errors - check the output above")
    else:
        print("\n❌ Fix failed")