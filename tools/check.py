"""One-command check (the pre-commit hook runs this): unit tests + text lint.

    python -X utf8 tools/check.py
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
steps = [[sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', os.path.join(ROOT, 'tests')]]
if os.path.exists(os.path.join(ROOT, 'tools', 'lint.py')):
    steps.append([sys.executable, '-X', 'utf8', os.path.join(ROOT, 'tools', 'lint.py')])
for s in steps:
    r = subprocess.run(s, cwd=ROOT)
    if r.returncode:
        sys.exit(r.returncode)
print('check OK')
