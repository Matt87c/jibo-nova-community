#!/usr/bin/env python3
"""Validate a 5x1/BEacon eye theme source and the exact release ZIP."""
import json
from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT/'dist'/(ROOT.name+'.zip')
REQUIRED = {'manifest.json','README.md','banner.png','face/face.json',
            'face/eye.png','face/eyeListening.png','face/eyeClosed.png'}
ALLOWED = REQUIRED


def check(files):
    names = set(files)
    assert REQUIRED <= names, 'Missing required files: '+str(sorted(REQUIRED-names))
    assert names <= ALLOWED, 'Unexpected ZIP entries: '+str(sorted(names-ALLOWED))
    assert len(names)<=1024 and sum(map(len,files.values()))<=64*1024*1024
    manifest = json.loads(files['manifest.json'])
    config = json.loads(files['face/face.json'])
    assert manifest['type']=='theme' and manifest['supported']=='3.1.6'
    assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',manifest['version'])
    assert manifest['name'] and len(manifest['name']) < 100
    assert config == {'backgroundColor':'#000000','eyeSize':122}
    assert 'Matt87c' in files['README.md'].decode('utf-8')
    for name in sorted(names):
        if name.endswith('.png'):
            with Image.open(BytesIO(files[name])) as im:
                im.verify()
            with Image.open(BytesIO(files[name])) as im:
                im.load()
                assert im.mode in ('RGB','RGBA') and max(im.size)<=4096
                assert im.width>0 and im.height>0
                # No EXIF/text chunks, GPS, prompt metadata, or local filenames.
                assert not im.info, name+' contains image metadata'
                if name.startswith('face/'):
                    assert im.width==im.height, name+' must be square'
    print('PASS:',manifest['name'],manifest['version'],len(files),'files')
    return manifest


def main():
    source={p: (ROOT/p).read_bytes() for p in sorted(ALLOWED) if (ROOT/p).is_file()}
    manifest=check(source)
    assert RELEASE.stat().st_size<=32*1024*1024
    with ZipFile(RELEASE) as z:
        assert z.testzip() is None, 'Bad ZIP checksum'
        names=z.namelist()
        assert len(names)==len(set(names)), 'Duplicate path'
        assert set(names)==set(source), 'Files differ'
        for item in z.infolist():
            assert item.filename in ALLOWED
            assert item.compress_type in (0,8)
            assert not (item.external_attr >> 16) & 0o170000 == 0o120000, 'Symlink forbidden'
        packaged={name:z.read(name) for name in names}
    assert packaged==source, 'Source != release content'
    assert check(packaged)==manifest
    print('PASS: release ZIP exact source match, size and CRC')

if __name__=='__main__':
    main()
