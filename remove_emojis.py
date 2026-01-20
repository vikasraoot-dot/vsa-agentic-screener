#!/usr/bin/env python3
"""
Remove all emojis from run_real_backtest.py to fix Unicode encoding issues
"""

import re

def remove_emojis():
    """Remove all emoji characters from the file"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Remove all emoji characters (Unicode range U+1F600-U+1F64F, U+1F300-U+1F5FF, etc.)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+",
            flags=re.UNICODE
        )

        cleaned_content = emoji_pattern.sub('', content)

        # Write back the cleaned content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        print("Removed all emojis from run_real_backtest.py")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_clean_file():
    """Test if the cleaned file works"""
    import subprocess
    import sys

    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', r'C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py'],
                              capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("SUCCESS: File compiles without Unicode errors!")
            return True
        else:
            print(f"Still has errors: {result.stderr[:200]}")
            return False

    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("Removing emojis from run_real_backtest.py...")
    if remove_emojis():
        print("Testing cleaned file...")
        if test_clean_file():
            print("PERFECT! All Unicode issues resolved.")
            print("Ready to run VSA backtest!")
        else:
            print("Still has issues")
    else:
        print("Failed to remove emojis")