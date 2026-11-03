#!/usr/bin/env python3
"""Build deterministic BEacon theme ZIP with distinct native blue listening eye."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from generate_listening import generate_listening_png

ROOT = Path(__file__).resolve().parents[1]
SLUG = ROOT.name
RELEASE = ROOT / 'dist' / (SLUG + '.zip')
SOURCE = ['manifest.json', 'README.md', 'banner.png', 'face/face.json',
          'face/eye.png', 'face/eyeClosed.png']
GENERATED = 'face/eyeListening.png'


def package_bytes():
    contents = {name: (ROOT / name).read_bytes() for name in SOURCE}
    # v1.0.0 shipped identical open/listening assets: generate a visibly
    # different iris state from the selected design, without altering eye.png.
    contents[GENERATED] = generate_listening_png(contents['face/eye.png'])
    return contents


def main():
    contents = package_bytes()
    RELEASE.parent.mkdir(exist_ok=True)
    with ZipFile(RELEASE, 'w') as archive:
        for name, data in sorted(contents.items()):
            entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    print('Built', RELEASE.name, RELEASE.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
