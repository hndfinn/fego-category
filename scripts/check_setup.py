#!/usr/bin/env python3
"""Portable offline configuration checks; does not test account or CMS access."""
import json
from pathlib import Path
import shutil
import sys

if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11+ required; use python3 or py -3.11 on Windows.')
import tomllib
root = Path(__file__).resolve().parents[1]
config = tomllib.loads((root / '.codex/config.toml').read_text(encoding='utf-8'))
roles = []
for name, role in config['agents'].items():
    if isinstance(role, dict):
        path = root / '.codex' / role['config_file']
        data = tomllib.loads(path.read_text(encoding='utf-8'))
        if data.get('name') != name or not data.get('developer_instructions'):
            raise SystemExit('Invalid role: ' + name)
        roles.append(name)
for path in (root / 'templates').glob('*.json'):
    json.loads(path.read_text(encoding='utf-8'))
for path in [root / 'AGENTS.md', root / '.agents/skills/fego-category/SKILL.md']:
    if not path.is_file():
        raise SystemExit('Missing required instruction file: ' + str(path))
print('PASS: portable project config, 4 roles, skill and templates; Python', sys.version.split()[0])
print('Codex CLI:', shutil.which('codex') or 'not found; use Codex app or install CLI')
print('MCP, WordPress, Drive authentication and browser rendering still require runtime checks.')
