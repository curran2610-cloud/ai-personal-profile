# coding: utf-8
from pathlib import Path
p = Path(__file__).resolve().parents[1]
names = ['profile.md', 'preferences.md', 'projects/index.md']
text = '# Portable summary\nSource: canonical files; updated 2026-11-24. Regenerate; do not edit independently.\n\n'
for name in names:
    text += '\nSource: ' + name + '\n' + (p/name).read_text(encoding='utf-8')
(p/'portable-summary.md').write_text(text, encoding='utf-8')
