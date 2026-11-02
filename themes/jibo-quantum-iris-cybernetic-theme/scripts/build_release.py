#!/usr/bin/env python3
"""Build deterministic, theme-only ZIP for BEacon Store (standard library)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import json

ROOT = Path(__file__).resolve().parents[1]
SLUG = ROOT.name
RELEASE = ROOT / 'dist' / (SLUG + '.zip')
FILES = ['manifest.json', 'README.md', 'banner.png', 'face/face.json',
         'face/eye.png', 'face/eyeListening.png']
if (ROOT / 'face/eyeClosed.png').is_file():
    FILES.append('face/eyeClosed.png')

def main():
    RELEASE.parent.mkdir(exist_ok=True)
    with ZipFile(RELEASE, 'w') as z:
        for name in FILES:
            p = ROOT / name
            if not p.is_file():
                raise SystemExit('Missing required theme file: ' + name)
            zi = ZipInfo(name, date_time=(2026,1,1,0,0,0))
            zi.compress_type = ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = 0o100644 << 16
            z.writestr(zi, p.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    print('Built', RELEASE.name, RELEASE.stat().st_size, 'bytes')

if __name__ == '__main__':
    main()
