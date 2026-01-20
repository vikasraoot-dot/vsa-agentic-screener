#!/usr/bin/env python3
"""
Targeted indentation fix for run_real_backtest.py
Only fixes indentation issues within function bodies, not function definitions
"""

def fix_targeted_indentation():
    """Fix only the problematic indentation within function bodies"""
    filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []
        in_function = False
        indent_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track function boundaries and indentation levels
            if stripped.startswith('def '):
                # Function definition - should not be indented
                in_function = True
                indent_level = 0
                fixed_lines.append(stripped)  # Remove any existing indentation
                continue
            elif stripped.startswith('class '):
                # Class definition - should not be indented
                in_function = False
                indent_level = 0
                fixed_lines.append(stripped)
                continue
            elif stripped.startswith('if __name__'):
                # Main block - should not be indented
                in_function = False
                indent_level = 0
                fixed_lines.append(stripped)
                continue
            elif stripped == '' or stripped.startswith('#'):
                # Empty lines and comments maintain their indentation context
                if in_function:
                    fixed_lines.append('    ' * indent_level + line.lstrip())
                else:
                    fixed_lines.append(line)
                continue

            # Handle indentation within functions
            if in_function:
                # Count leading spaces in original line
                original_indent = len(line) - len(line.lstrip())

                # Special handling for try/except blocks
                if stripped.startswith(('try:', 'except', 'finally:', 'else:')):
                    # These should align with the containing block
                    current_indent = indent_level
                elif stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'with ')):
                    # Control structures
                    current_indent = indent_level
                elif original_indent == 0 and stripped:
                    # This line should be indented within the function
                    current_indent = indent_level + 1  # 4 spaces
                else:
                    # Maintain relative indentation
                    current_indent = indent_level + (original_indent // 4)

                # Apply the correct indentation
                fixed_lines.append('    ' * current_indent + stripped)

                # Update indent level for next lines
                if stripped.endswith(':') and not stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                    indent_level += 1

            else:
                # Not in a function, keep original indentation
                fixed_lines.append(line)

        # Write back the fixed content
        content = '\n'.join(fixed_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Applied targeted indentation fixes")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_targeted_fix():
    """Test if the targeted fix worked"""
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
    print("🎯 Targeted indentation fix for run_real_backtest.py")
    print("="*60)

    if fix_targeted_indentation():
        print("\n🧪 Testing targeted fix...")
        if test_targeted_fix():
            print("\n" + "="*60)
            print("🎉 SUCCESS! ALL INDENTATION ERRORS FIXED!")
            print("✅ File compiles perfectly")
            print("✅ Ready to run VSA backtest")
            print("\n🚀 RUN YOUR BACKTEST NOW:")
            print("   python run_real_backtest.py")
            print("="*60)
        else:
            print("\n❌ Still has indentation errors - check output above")
    else:
        print("\n❌ Targeted fix failed")