#!/usr/bin/env python3
"""Rebuild and validate all public community theme ZIPs and secret hygiene."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'themes' / 'catalog.json'


def run(*command: str) -> None:
    subprocess.run(list(command), check=True, cwd=ROOT)


def main() -> int:
    themes = json.loads(CATALOG.read_text(encoding='utf-8'))['themes']
    names, slugs = set(), set()
    for info in themes:
        slug, name, version = info['slug'], info['name'], info['version']
        if slug in slugs or name in names:
            raise ValueError('Theme names/slugs must be unique')
        slugs.add(slug); names.add(name)
        folder = ROOT / 'themes' / slug
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        if manifest != {'name': name, 'version': version, 'supported': '3.1.6', 'type': 'theme'}:
            raise ValueError(f'Manifest differs from catalog for {slug}')
        print(f'BUILD AND CHECK {name} v{version}', flush=True)
        run(sys.executable, str(folder / 'scripts' / 'build_release.py'))
        run(sys.executable, str(folder / 'scripts' / 'validate_release.py'))
        zip_path = folder / 'dist' / (slug + '.zip')
        if not zip_path.is_file() or zip_path.stat().st_size == 0:
            raise ValueError(f'No distributable archive for {slug}')
    run(sys.executable, str(ROOT / 'scripts' / 'security_scan.py'))
    print('PASS: all theme packages, versions, ZIP integrity, and basic secret safeguards')
    return 0

if __name__ == '__main__':
    sys.exit(main())
