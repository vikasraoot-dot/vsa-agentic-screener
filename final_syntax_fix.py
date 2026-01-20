#!/usr/bin/env python3
"""
Final syntax error fix for remaining VSA backtest issues
"""

import os

def fix_vsa_backtester_line_178():
    """Fix the syntax error at line 178 in vsa_backtester.py"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix line 178 - missing closing parenthesis and quote
        old_line = '        logger.info("Backtest completed successfully"        return result'
        new_lines = '        logger.info("Backtest completed successfully")\n        return result'

        if old_line in content:
            content = content.replace(old_line, new_lines)
            print("✅ Fixed vsa_backtester.py line 178 syntax error")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print("⚠️ Could not find the exact error line in vsa_backtester.py")
            return False

    except Exception as e:
        print(f"❌ Error fixing vsa_backtester.py: {e}")
        return False

def fix_comprehensive_validator_line_299():
    """Fix the syntax error at line 299 in comprehensive_validator.py"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix line 299 - malformed f-string
        old_line = '            ".2f"".2f"".2f"".2f"".2f"".2f"",'
        new_line = '            f"{wf.average_stability:.2f} {wf.average_overfitting:.2f} {wf.consistency_score:.2f} {wf.predictive_power:.2f} {result.performance_degradation:.2f} {wf.robustness_rating}",'

        if old_line in content:
            content = content.replace(old_line, new_line)
            print("✅ Fixed comprehensive_validator.py line 299 syntax error")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print("⚠️ Could not find the exact error line in comprehensive_validator.py")
            return False

    except Exception as e:
        print(f"❌ Error fixing comprehensive_validator.py: {e}")
        return False

def test_final_fixes():
    """Test that all syntax errors are finally fixed"""
    files_to_test = [
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\vsa_backtester.py",
        r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\comprehensive_validator.py"
    ]

    print("\n🧪 Testing final syntax fixes...")

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
    """Final fix for remaining syntax errors"""
    print("🔧 FINAL VSA Backtest Syntax Error Fix")
    print("="*50)

    # Fix the remaining syntax errors
    print("\n🔧 Fixing final syntax errors...")
    fix_vsa_backtester_line_178()
    fix_comprehensive_validator_line_299()

    # Test all fixes
    all_fixed = test_final_fixes()

    print("\n" + "="*50)

    if all_fixed:
        print("🎉 ALL SYNTAX ERRORS FINALLY FIXED!")
        print("✅ Ready to run backtests")
        print("\n🚀 Next steps:")
        print("1. Run: python test_backtest_setup.py")
        print("2. Run: python run_real_backtest.py")
        print("3. Check enhanced_reports/ for results")
    else:
        print("❌ Some syntax errors still remain")
        print("   Please check the error messages above")

    print("="*50)

if __name__ == "__main__":
    main()