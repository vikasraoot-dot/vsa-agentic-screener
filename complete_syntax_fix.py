#!/usr/bin/env python3
"""
Complete syntax error fix for all VSA backtesting files
"""

import os
import re

def fix_vsa_backtester():
    """Fix all syntax errors in vsa_backtester.py"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py"

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix multiple malformed f-strings
        fixes = [
            # Line 664 (original)
            ('            ".2%"".2%"".3f"".3f"".3f"",',
             '            f"{result.total_return:.2%} {result.annualized_return:.2%} {result.sharpe_ratio:.3f} {result.max_drawdown:.3f} {result.win_rate:.2%},",'),

            # Line 685 (newly discovered)
            ('            ".1%"".4f"".1%"".3f"",',
             '            f"{result.win_rate:.1%} {result.statistical_significance:.4f} {result.monte_carlo_confidence:.1%} {result.profit_factor:.3f},",'),
        ]

        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Fixed malformed f-string in vsa_backtester.py")
            else:
                print(f"⚠️ Could not find exact pattern in vsa_backtester.py")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"❌ Error fixing vsa_backtester.py: {e}")
        return False

def fix_comprehensive_validator():
    """Fix all syntax errors in comprehensive_validator.py"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix the malformed f-string at line 292
        old_line = '            ".2%"".2%"".2%"".1%"".2%"".4f"",'
        new_line = '            f"{result.total_return:.2%} {result.annualized_return:.2%} {result.sharpe_ratio:.2%} {result.win_rate:.1%} {result.max_drawdown:.2%} {result.statistical_significance:.4f},",'

        if old_line in content:
            content = content.replace(old_line, new_line)
            print("✅ Fixed comprehensive_validator.py syntax error")
        else:
            print("⚠️ Could not find the exact error pattern in comprehensive_validator.py")
            # Try a more general fix
            content = re.sub(r'"\.(\d+)%"\.(\d+)%"\.(\d+)%"\.(\d+)%"\.(\d+)%"\.(\d+)f"",',
                           r'f"{\1:.\2%} {\3:.\4%} {\5:.\6%} {\7:.\8%} {\9:.\10%} {\11:.\12f},",',
                           content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"❌ Error fixing comprehensive_validator.py: {e}")
        return False

def install_statsmodels():
    """Install statsmodels package"""
    import subprocess
    import sys

    try:
        print("📦 Installing statsmodels...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'statsmodels>=0.14.0',
            '--quiet', '--disable-pip-version-check'
        ])
        print("✅ statsmodels installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install statsmodels: {e}")
        return False

def test_all_fixes():
    """Test that all syntax errors are fixed"""
    files_to_test = [
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py",
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"
    ]

    print("\n🧪 Testing all syntax fixes...")

    all_passed = True
    for filepath in files_to_test:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            compile(content, filepath, 'exec')
            print(f"✅ {os.path.basename(filepath)} - Syntax OK")

        except SyntaxError as e:
            print(f"❌ {os.path.basename(filepath)} - Still has syntax error: {e}")
            all_passed = False
        except Exception as e:
            print(f"⚠️ {os.path.basename(filepath)} - Other error: {e}")
            all_passed = False

    return all_passed

def main():
    """Complete fix for all syntax errors"""
    print("🔧 COMPLETE VSA Backtest Syntax Error Fix")
    print("="*50)

    # Install missing dependency
    install_statsmodels()

    # Fix syntax errors
    print("\n🔧 Fixing all syntax errors...")
    fix_vsa_backtester()
    fix_comprehensive_validator()

    # Test all fixes
    all_fixed = test_all_fixes()

    print("\n" + "="*50)

    if all_fixed:
        print("🎉 ALL SYNTAX ERRORS FIXED!")
        print("✅ Ready to run backtests")
        print("\n🚀 Next steps:")
        print("1. Run: python test_backtest_setup.py")
        print("2. Run: python run_real_backtest.py")
        print("3. Check enhanced_reports/ for results")
    else:
        print("❌ Some syntax errors remain")
        print("   Check the error messages above")
        print("   You may need to manually fix remaining issues")

    print("="*50)

if __name__ == "__main__":
    main()