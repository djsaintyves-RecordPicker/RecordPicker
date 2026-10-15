#!/usr/bin/env python3
"""Keep Windows patch-version labels aligned with the verified Store release."""
from pathlib import Path
import re

def refresh_windows_pages(root: Path):
    for page in root.glob('**/windows-app/index.html'):
        if 'dulpi' in page.parts:
            continue
        text = page.read_text()
        text = re.sub(r'Record Picker 3\.0(?![.\d])', 'Record Picker 3.0.1', text)
        text = text.replace('Record Picker · 3.0</span>', 'Record Picker · 3.0.1</span>')
        text = text.replace('"softwareVersion":"3.0"', '"softwareVersion":"3.0.1"')
        text = re.sub(r'"dateModified":"[0-9-]+"', '"dateModified":"2026-10-15"', text)
        page.write_text(text)

if __name__ == '__main__':
    refresh_windows_pages(Path(__file__).resolve().parents[1])
