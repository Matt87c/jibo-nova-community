#!/usr/bin/env python3
"""Static safeguards for exporting community themes to a public repository.

Checks paths, ZIP members and plaintext for common private setup details.
A passing scan is not proof of zero secrets or of artwork redistribution rights.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_NAMES = {
    '.env', 'id_rsa', 'id_ed25519', 'credentials.json', 'secrets.json',
    'openclaw.json', 'config.local.json', '.npmrc', '.pypirc',
}
BLOCKED_EXTENSIONS = {
    '.pem', '.key', '.p12', '.pfx', '.crt', '.sqlite', '.sqlite3',
    '.db', '.log', '.bak', '.backup', '.keystore',
}
TEXT_EXTENSIONS = {
    '.md', '.txt', '.json', '.py', '.ps1', '.sh', '.yml', '.yaml',
    '.toml', '.ini', '.cfg', '.gitignore', '.gitattributes',
}
TEXT_NAMES = {'LICENSE', 'README', 'SECURITY', 'CONTRIBUTING'}
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache'}
CHECKS = [
    ('private_ipv4', re.compile(
        r'(?<![0-9])(?:10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}'
        r'|192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3}'
        r'|172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.)[0-9]{1,3})(?![0-9])'
    )),
    ('private_key_header', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('github_token', re.compile(r'(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})')),
    ('openai_api_key', re.compile(r'(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{20,}')),
    ('aws_key', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('authorization_header', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9_.~+/-]{18,}')),
    ('credential_assignment', re.compile(
        r'(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password'
        r'|client[_-]?secret|webhook[_-]?secret|authorization)\s*[:=]\s*'
        r'["\x27]?[A-Za-z0-9_./+=~-]{15,}'
    )),
    ('user_home_path', re.compile(r'(?i)(?:[A-Z]:\\Users\\[^\s\\]+|/Users/[^\s/]+|/home/[^\s/]+)')),
]


def scan_text(content: str, location: str, findings: list[str]) -> None:
    for label, rx in CHECKS:
        if rx.search(content):
            findings.append(f'{location}: {label}')  # never echo the secret itself


def is_text_file(name: str) -> bool:
    return Path(name).suffix.lower() in TEXT_EXTENSIONS or Path(name).name in TEXT_NAMES


def main() -> int:
    findings = []
    text_files = 0
    zips = 0
    for file in sorted(ROOT.rglob('*')):
        if not file.is_file() or any(part in SKIP_DIRS for part in file.relative_to(ROOT).parts):
            continue
        rel = file.relative_to(ROOT).as_posix()
        name = file.name.lower()
        if name in BLOCKED_NAMES or (name.startswith('.env') and name != '.env.example'):
            findings.append(f'{rel}: prohibited filename')
        if file.suffix.lower() in BLOCKED_EXTENSIONS:
            findings.append(f'{rel}: prohibited extension')
        if is_text_file(file.name):
            text_files += 1
            try:
                scan_text(file.read_text('utf-8'), rel, findings) if rel != 'scripts/security_scan.py' else None
            except UnicodeDecodeError:
                findings.append(f'{rel}: invalid text encoding')
        if file.suffix.lower() != '.zip':
            continue
        zips += 1
        try:
            with ZipFile(file) as archive:
                if archive.testzip() is not None:
                    findings.append(f'{rel}: corrupt archive')
                members = archive.infolist()
                if len(members) != len({m.filename.casefold() for m in members}):
                    findings.append(f'{rel}: duplicate archive paths')
                for member in members:
                    p = PurePosixPath(member.filename)
                    if (p.is_absolute() or '..' in p.parts or '\\' in member.filename or
                            member.filename.startswith('./')):
                        findings.append(f'{rel}: unsafe ZIP path')
                    if member.flag_bits & 1:
                        findings.append(f'{rel}: encrypted ZIP entry')
                    if (member.external_attr >> 16) & 0o170000 == 0o120000:
                        findings.append(f'{rel}: ZIP symlink')
                    if member.filename.startswith('face/') and not member.filename.endswith('.png') and not member.filename.endswith('.json'):
                        findings.append(f'{rel}: unexpected face asset')
                    if is_text_file(member.filename):
                        try:
                            data = archive.read(member.filename)
                            scan_text(data.decode('utf-8'), rel + ':' + member.filename, findings)
                        except Exception:
                            findings.append(f'{rel}: cannot inspect ZIP text member')
        except Exception as exc:
            findings.append(f'{rel}: cannot open ZIP ({type(exc).__name__})')
    if findings:
        print('FAIL: public release safety scan:')
        for item in findings:
            print(' - ' + item)
        return 1
    print(f'PASS: public package scan: {text_files} text files, {zips} ZIPs, no common secret/path signatures')
    return 0


if __name__ == '__main__':
    sys.exit(main())
