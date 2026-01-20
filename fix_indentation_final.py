#!/usr/bin/env python3
"""Fix indentation in analyze_backtest_results function"""

filepath = r"C:\Users\vraoo\.cursor\worktrees\vsa-agentic-screener\gfw\run_real_backtest.py"

with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []
in_analyze_function = False

for line in lines:
    if line.strip().startswith('def analyze_backtest_results'):
        in_analyze_function = True
        fixed_lines.append(line)
        continue
    elif in_analyze_function and line.strip().startswith('def ') and 'analyze_backtest_results' not in line:
        # Next function
        in_analyze_function = False
        fixed_lines.append(line)
        continue

    if in_analyze_function:
        # Remove extra indentation
        if line.startswith('        ') and line.strip():
            line = line[4:]  # Remove 4 spaces

    fixed_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print('Fixed indentation in analyze_backtest_results')