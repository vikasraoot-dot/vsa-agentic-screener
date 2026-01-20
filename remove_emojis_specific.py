#!/usr/bin/env python3
"""
Remove all emojis from a specific file
"""

import re
import sys

def remove_emojis_from_file(filepath):
    """Remove all emoji characters from a file"""
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

        print(f"Removed all emojis from {filepath}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_emojis_specific.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    remove_emojis_from_file(filepath)