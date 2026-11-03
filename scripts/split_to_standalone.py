#!/usr/bin/env python3
"""Create one public BEacon repo per theme, preserving its Git subtree history.

Dry run by default. --apply explicitly creates repositories and pushes code.
Only clones the public jibo-nova-community repository; never reads private NOVA data.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SOURCE_REPO = 'jibo-nova-community'
WORKFLOW = """name: Validate BEacon theme
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: read
jobs:
  theme:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
        with:
          python-version: '3.11'
      - run: python -m pip install Pillow==11.3.0
      - run: python scripts/build_release.py
      - run: python scripts/validate_release.py
"""


def run(*args, cwd=None, check=True):
    proc = subprocess.run(args, cwd=cwd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode:
        raise RuntimeError('{} failed: {}'.format(' '.join(map(str, args)),
                                                 (proc.stderr or proc.stdout)[-1400:]))
    return proc


def load_catalog(repo):
    info = json.loads((repo / 'themes/catalog.json').read_text(encoding='utf-8'))['themes']
    seen = set()
    for item in info:
        slug = item['slug']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug) or slug in seen:
            raise ValueError('Unsafe or duplicate theme slug: ' + repr(slug))
        seen.add(slug)
        path = repo / 'themes' / slug
        manifest = json.loads((path / 'manifest.json').read_text(encoding='utf-8'))
        if (manifest.get('name') != item['name'] or
                manifest.get('version') != item['version'] or
                manifest.get('type') != 'theme'):
            raise ValueError('Catalog/manifest mismatch: ' + slug)
        for filename in ('scripts/build_release.py', 'scripts/validate_release.py',
                         'face/face.json', 'README.md', 'banner.png'):
            if not (path / filename).is_file():
                raise ValueError('Missing {} in {}'.format(filename, slug))
    return info


def create_one(source, item, owner, workspace, license_path):
    slug = item['slug']
    target = owner + '/' + slug
    if run('gh', 'repo', 'view', target, '--json', 'name', check=False).returncode == 0:
        print('SKIP existing repository; never overwrite:', target, flush=True)
        return
    sha = run('git', '-C', str(source), 'subtree', 'split', '--prefix',
              'themes/' + slug, 'HEAD').stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise RuntimeError('Unexpected subtree SHA for ' + slug)
    print('CREATING', target, 'from subtree', sha[:12], flush=True)
    run('gh', 'repo', 'create', target, '--public', '--description',
        item['name'] + ' - Jibo 5x1/BEacon theme by Matt87c')
    url = 'https://github.com/' + target + '.git'
    run('git', '-C', str(source), 'push', url, sha + ':refs/heads/main')
    dst = workspace / slug
    run('git', 'clone', '--branch', 'main', url, str(dst))
    shutil.copy2(license_path, dst / 'LICENSE')
    workflow_dir = dst / '.github' / 'workflows'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / 'validate.yml').write_text(WORKFLOW, encoding='utf-8')
    run(sys.executable, 'scripts/build_release.py', cwd=dst)
    run(sys.executable, 'scripts/validate_release.py', cwd=dst)
    # Retain the exact validated installable package in every standalone repository.
    release_name = 'dist/' + slug + '.zip'
    if not (dst / release_name).is_file():
        raise RuntimeError('Missing rebuilt release ZIP: ' + release_name)
    run('git', 'add', 'LICENSE', '.github/workflows/validate.yml', release_name, cwd=dst)
    run('git', 'commit', '-m', 'Add standalone theme licensing and CI', cwd=dst)
    run('git', 'push', 'origin', 'main', cwd=dst)
    print('SOURCE AND ZIP READY; stable release withheld until hardware QA:', target, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Create public repos and push code')
    parser.add_argument('--owner', default='Matt87c')
    args = parser.parse_args()
    if args.owner != 'Matt87c':
        raise SystemExit('Review target owner before modifying this script')
    if not args.apply:
        print('DRY RUN - no network or changes. Planned per-theme repositories:')
        for slug in ('jibo-nova-core-holographic-theme',
                     'jibo-quantum-iris-cybernetic-theme', 'jibo-nova-halo-theme',
                     'jibo-nova-core-theme', 'jibo-quantum-iris-theme',
                     'jibo-nova-sentient-eye-theme', 'jibo-nova-sentient-orb-theme'):
            print('  https://github.com/' + args.owner + '/' + slug)
        print('Review MIGRATION.md, then run with --apply.')
        return
    for command in ('git', 'gh'):
        if shutil.which(command) is None:
            raise SystemExit('Missing command: ' + command)
    try:
        import PIL  # noqa: F401 - validator dependency, checked before any remote write
    except ImportError:
        raise SystemExit('First run: python -m pip install Pillow==11.3.0')
    run('gh', 'auth', 'status')
    login = run('gh', 'api', 'user', '-q', '.login').stdout.strip()
    if login.lower() != args.owner.lower():
        raise SystemExit('STOP: authenticated GitHub account is %s, expected %s' % (login, args.owner))
    with tempfile.TemporaryDirectory(prefix='beacon-split-') as td:
        workspace = Path(td)
        source = workspace / SOURCE_REPO
        run('gh', 'repo', 'clone', args.owner + '/' + SOURCE_REPO, str(source))
        if run('git', 'status', '--porcelain', cwd=source).stdout.strip():
            raise RuntimeError('Source clone is unexpectedly dirty')
        themes = load_catalog(source)
        print('Preflight: validating all theme source and ZIPs', flush=True)
        run(sys.executable, 'scripts/validate_all.py', cwd=source)
        license_path = source / 'LICENSE'
        if not license_path.is_file():
            raise RuntimeError('Source LICENSE missing')
        for item in themes:
            create_one(source, item, args.owner, workspace, license_path)
    print('Done: review GitHub Actions, then create releases after robot acceptance.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        raise SystemExit('STOP: ' + str(exc))
