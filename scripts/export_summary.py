# coding: utf-8
from pathlib import Path
import posixpath
import re
p = Path(__file__).resolve().parents[1]
names = ['profile.md', 'preferences.md', 'projects/index.md']
sources = {name: (p / name).read_text(encoding='utf-8') for name in names}
updates = re.findall(r'更新[：:]\s*(\d{4}-\d{2}-\d{2})', '\n'.join(sources.values()))
updated = max(updates)
text = f'# Portable summary\nSource: canonical files; updated {updated}. Regenerate; do not edit independently.\n\n'
relative_link = re.compile(r'\]\((?![a-zA-Z][a-zA-Z0-9+.-]*:|/|#)([^\s)]+)\)')
for name, source in sources.items():
    directory = Path(name).parent.as_posix()
    source = relative_link.sub(
        lambda link: f"]({posixpath.normpath(posixpath.join(directory, link[1]))})",
        source,
    )
    text += f'\nSource: {name}\n{source}'
(p/'portable-summary.md').write_text(text, encoding='utf-8')
