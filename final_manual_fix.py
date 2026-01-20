#!/usr/bin/env python3
"""
Final manual fix - replace the entire problematic function
"""

def fix_analyze_results_function():
    """Replace the entire analyze_backtest_results function"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find the analyze_backtest_results function and replace it entirely
        old_function = '''def analyze_backtest_results(results):
    """
    Analyze and display backtest results
    """
    if not results:
        print("No results to analyze")
        return

    print("\\n" + "="*60)
    print("🎯 REAL VSA BACKTEST RESULTS ANALYSIS")
    print("="*60)

    # Overall assessment
    assessment = results.get('final_assessment', {})
    print(f"\\n📊 OVERALL ASSESSMENT: {assessment.get('overall_rating', 'N/A')}")
    print(f"Confidence Level: {assessment.get('confidence_level', 'N/A')}")
    print(".1%"
    # Validation breakdown
    breakdown = assessment.get('validation_breakdown', {})
    print("\\n✅ Validation Results:")
    print(f"   Backtest: {'PASSED' if breakdown.get('backtest_passed') else 'FAILED'}")
    print(f"   Walk-Forward: {'PASSED' if breakdown.get('walk_forward_passed') else 'FAILED'}")
    print(f"   Statistical: {'PASSED' if breakdown.get('statistical_passed') else 'FAILED'}")

    # Key strengths and weaknesses
    print("\\n💪 KEY STRENGTHS:")
    for strength in assessment.get('key_strengths', []):
        print(f"   • {strength}")

    print("\\n⚠️ KEY WEAKNESSES:")
    for weakness in assessment.get('key_weaknesses', []):
        print(f"   • {weakness}")

    # Recommendations
    print("\\n💡 RECOMMENDATIONS:")
    for rec in assessment.get('recommendations', []):
        print(f"   • {rec}")

    print("\\n" + "="*60)'''

        new_function = '''def analyze_backtest_results(results):
    """
    Analyze and display backtest results
    """
    if not results:
        print("No results to analyze")
        return

    print("\\n" + "="*60)
    print("REAL VSA BACKTEST RESULTS ANALYSIS")
    print("="*60)

    # Overall assessment
    assessment = results.get('final_assessment', {})
    print(f"\\nOVERALL ASSESSMENT: {assessment.get('overall_rating', 'N/A')}")
    print(f"Confidence Level: {assessment.get('confidence_level', 'N/A')}")
    print(".1%"
    # Validation breakdown
    breakdown = assessment.get('validation_breakdown', {})
    print("\\nValidation Results:")
    print(f"   Backtest: {'PASSED' if breakdown.get('backtest_passed') else 'FAILED'}")
    print(f"   Walk-Forward: {'PASSED' if breakdown.get('walk_forward_passed') else 'FAILED'}")
    print(f"   Statistical: {'PASSED' if breakdown.get('statistical_passed') else 'FAILED'}")

    # Key strengths and weaknesses
    print("\\nKEY STRENGTHS:")
    for strength in assessment.get('key_strengths', []):
        print(f"   - {strength}")

    print("\\nKEY WEAKNESSES:")
    for weakness in assessment.get('key_weaknesses', []):
        print(f"   - {weakness}")

    # Recommendations
    print("\\nRECOMMENDATIONS:")
    for rec in assessment.get('recommendations', []):
        print(f"   - {rec}")

    print("\\n" + "="*60)'''

        if old_function in content:
            content = content.replace(old_function, new_function)
            print("Replaced the problematic function")

        # Also remove any remaining Unicode characters that might cause issues
        content = content.replace("🎯", "").replace("📊", "").replace("✅", "").replace("💪", "").replace("⚠️", "").replace("💡", "")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Fixed file successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_final_fix():
    """Test the final fix"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("SUCCESS: File compiles without syntax errors!")
            return True
        else:
            print(f"Still has syntax error: {result.stderr[:300]}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("Final manual fix for run_real_backtest.py")
    if fix_analyze_results_function():
        if test_final_fix():
            print("\\nREADY TO RUN BACKTEST!")
            print("Run: python run_real_backtest.py")
        else:
            print("\\nStill has syntax errors")
    else:
        print("\\nFix failed")