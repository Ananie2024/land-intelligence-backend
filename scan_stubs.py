import os
import sys

stub_threshold = 5  # files with <= lines of actual code are considered stubs

exclude_dirs = {'.venv', 'venv', '.git', 'mypy_report', 'mypy_html', 'backups', 'logs', 'node_modules'}
results = []
for root, dirs, files in os.walk('.'):
    parts = root.split(os.sep)
    if any(ex in parts for ex in exclude_dirs):
        continue
    if 'tests' in parts or root.endswith(os.sep + 'tests'):
        continue
    for file in files:
        if not file.endswith('.py'):
            continue
        path = os.path.join(root, file)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                code_lines = 0
                for line in f:
                    s = line.strip()
                    if s and not s.startswith('#'):
                        code_lines += 1
        except Exception as e:
            code_lines = -1
        results.append((path, code_lines))

empty_or_stub = [(p, n) for p, n in results if n >= 0 and n <= stub_threshold and not p.endswith(os.sep + '__init__.py')]
empty_or_stub.sort(key=lambda x: x[1])

if empty_or_stub:
    print('Empty/stub files in project source (excluding __init__.py and tests):')
    for path, n in empty_or_stub:
        print(f'{n} lines: {path}')
else:
    print('No empty/stub files found in project source.')