#!/usr/bin/env python3
"""Build a release asset bundle and checksums from validated public themes."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'release-assets'


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / 'scripts/validate_all.py')], check=True)
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    themes = json.loads((ROOT / 'themes/catalog.json').read_text(encoding='utf-8'))['themes']
    checks = []
    rows = []
    for theme in themes:
        slug, ver, title = theme['slug'], theme['version'], theme['name']
        src = ROOT / 'themes' / slug / 'dist' / (slug + '.zip')
        dest = DEST / src.name
        shutil.copy2(src, dest)
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        checks.append(f'{digest}  {dest.name}')
        rows.append(f'| {title} | {ver} | `{dest.name}` |')
    (DEST / 'SHA256SUMS.txt').write_text('\n'.join(checks) + '\n', encoding='utf-8')
    (DEST / 'RELEASE_NOTES.md').write_text('''# Jibo NOVA Community theme collection - release candidate

Five individually installable 5x1/OpenJibo BEacon eye themes by Matt87c.
**This is a prerelease:** ZIP/source/security checks passed, but physical Jibo
acceptance for every exact build is not yet recorded. Do not claim Store approval.

| Theme | Version | Asset |
| --- | --- | --- |
''' + '\n'.join(rows) + '''

## Installation

Download one ZIP attachment. In BEacon, choose Store > Themes > three-dot menu
> Upload Theme ZIP; then select the theme and Apply. None restores stock eyes.
Do not extract or upload a source-code ZIP in place of the installable asset.

## Verification

Use SHA256SUMS.txt to verify the download. The checked artifacts contain only
BEacon declarative theme data, not NOVA/OpenClaw or personal robot settings.

## Store support

A combined monorepo release is for manual downloads. Independent GitHub Store
install/update listings generally require per-theme repositories with their
own stable releases, or maintainer-approved alternate storefront URLs.

## Sign-off

Stable promotion requires the hardware checklist in each
`themes/<slug>/docs/HARDWARE_TEST.md` to pass on the actual Jibo.
''', encoding='utf-8')
    print('PASS: release bundle built with', len(themes), 'installable ZIPs, checksums and notes')

if __name__ == '__main__':
    main()
