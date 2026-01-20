#!/usr/bin/env python3
"""
Fix syntax errors in VSA backtesting files
"""

import os
import re

def fix_vsa_backtester():
    """Fix syntax error in vsa_backtester.py line 664"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py"

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix the malformed f-string on line 664
        # Replace the broken string with proper f-string
        old_line = '            ".2%"".2%"".3f"".3f"".3f"",'
        new_line = '            f"{result.total_return:.2%} {result.annualized_return:.2%} {result.sharpe_ratio:.3f} {result.max_drawdown:.3f} {result.win_rate:.2%},",'

        if old_line in content:
            content = content.replace(old_line, new_line)
            print("✅ Fixed vsa_backtester.py syntax error")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print("⚠️ Could not find the exact error line in vsa_backtester.py")
            return False

    except Exception as e:
        print(f"❌ Error fixing vsa_backtester.py: {e}")
        return False

def fix_comprehensive_validator():
    """Fix syntax error in comprehensive_validator.py line 292"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for the syntax error around line 292
        lines = content.split('\n')
        if len(lines) > 291:
            error_line = lines[291]
            print(f"Line 292 content: {repr(error_line)}")

            # Look for unterminated string patterns
            if ',"' in error_line and not error_line.count('"') % 2 == 0:
                # Try to find the complete string and fix it
                # This is a complex fix, let's look for common patterns
                pass

        # For now, let's try a simple search and replace for common issues
        content = re.sub(r'(\w+)"(\w+)"([^"]*)$', r'\1"\2"\3"', content, flags=re.MULTILINE)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Attempted to fix comprehensive_validator.py")
        return True

    except Exception as e:
        print(f"❌ Error fixing comprehensive_validator.py: {e}")
        return False

def add_statsmodels_to_requirements():
    """Add statsmodels to requirements.txt"""
    req_file = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\requirements.txt"

    if not os.path.exists(req_file):
        print(f"❌ Requirements file not found: {req_file}")
        return False

    try:
        with open(req_file, 'r') as f:
            requirements = f.read()

        if 'statsmodels' not in requirements:
            requirements += '\nstatsmodels>=0.14.0\n'
            with open(req_file, 'w') as f:
                f.write(requirements)
            print("✅ Added statsmodels to requirements.txt")
            return True
        else:
            print("✅ statsmodels already in requirements.txt")
            return True

    except Exception as e:
        print(f"❌ Error updating requirements.txt: {e}")
        return False

def test_syntax_fixes():
    """Test that the syntax errors are fixed"""
    files_to_test = [
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py",
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"
    ]

    print("\n🧪 Testing syntax fixes...")

    for filepath in files_to_test:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            compile(content, filepath, 'exec')
            print(f"✅ {os.path.basename(filepath)} - Syntax OK")

        except SyntaxError as e:
            print(f"❌ {os.path.basename(filepath)} - Still has syntax error: {e}")
        except Exception as e:
            print(f"⚠️ {os.path.basename(filepath)} - Other error: {e}")

def main():
    """Main fix function"""
    print("🔧 Fixing VSA Backtest Syntax Errors")
    print("="*50)

    # Add missing dependency
    print("📦 Adding statsmodels dependency...")
    add_statsmodels_to_requirements()

    # Fix syntax errors
    print("\n🔧 Fixing syntax errors...")
    fix_vsa_backtester()
    fix_comprehensive_validator()

    # Test fixes
    test_syntax_fixes()

    print("\n" + "="*50)
    print("🎯 NEXT STEPS:")
    print("1. Install statsmodels: pip install statsmodels")
    print("2. Run: python test_backtest_setup.py")
    print("3. If still errors, run: python run_real_backtest.py")
    print("="*50)

if __name__ == "__main__":
    main()