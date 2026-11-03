#!/usr/bin/env python3
"""Validate theme source, distinct native listening art, and exact ZIP."""
from io import BytesIO
import json
import re
from zipfile import ZipFile
from PIL import Image, ImageChops
from build_release import ROOT, RELEASE, package_bytes

REQUIRED = {'manifest.json', 'README.md', 'banner.png', 'face/face.json',
            'face/eye.png', 'face/eyeListening.png', 'face/eyeClosed.png'}


def validate(contents):
    assert set(contents) == REQUIRED, 'Missing/extra theme assets'
    manifest = json.loads(contents['manifest.json'])
    face = json.loads(contents['face/face.json'])
    assert manifest['type'] == 'theme' and manifest['supported'] == '3.1.6'
    assert re.fullmatch(r'\d+\.\d+\.\d+', manifest['version'])
    assert manifest['version'] == '1.0.2'
    assert face == {'backgroundColor': '#000000', 'eyeSize': 135}
    readme = contents['README.md'].decode('utf-8')
    assert 'Matt87c' in readme and 'hardware' in readme.lower()
    assert sum(map(len, contents.values())) <= 64 * 1024 * 1024

    for filename, data in contents.items():
        if filename.endswith('.png'):
            with Image.open(BytesIO(data)) as img:
                img.verify()
            with Image.open(BytesIO(data)) as img:
                img.load()
                assert img.mode in ('RGB', 'RGBA') and 0 < max(img.size) <= 4096
                assert not img.info, 'Embedded metadata in ' + filename
                if filename.startswith('face/'):
                    assert img.width == img.height

    with Image.open(BytesIO(contents['face/eye.png'])) as src, \
         Image.open(BytesIO(contents['face/eyeListening.png'])) as listening:
        assert src.size == listening.size
        a = src.convert('RGBA')
        b = listening.convert('RGBA')
        assert a.getchannel('A').tobytes() == b.getchannel('A').tobytes(), 'Eye silhouette changed'
        assert ImageChops.difference(a.convert('RGB'), b.convert('RGB')).getbbox(), 'Listening image identical to idle'
        c = src.width // 2
        p = (c + round(src.width * 0.22), c)
        assert a.convert('RGB').getpixel(p) != b.convert('RGB').getpixel(p), 'No illumination on iris'
    return manifest


def main():
    expected = package_bytes()
    manifest = validate(expected)
    assert RELEASE.is_file() and RELEASE.stat().st_size <= 32 * 1024 * 1024
    with ZipFile(RELEASE) as archive:
        assert archive.testzip() is None, 'Bad ZIP CRC'
        names = archive.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP path'
        assert set(names) == REQUIRED
        for item in archive.infolist():
            assert item.filename in REQUIRED and '..' not in item.filename.split('/')
            assert item.compress_type in (0, 8)
            assert (item.external_attr >> 16) & 0o170000 != 0o120000, 'Symlink forbidden'
        packaged = {name: archive.read(name) for name in names}
    assert packaged == expected, 'ZIP differs from generated source'
    assert validate(packaged) == manifest
    print('PASS:', manifest['name'], manifest['version'], '- distinct blue listening eye / exact ZIP')


if __name__ == '__main__':
    main()
