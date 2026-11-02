#!/usr/bin/env python3
"""Configure this machine's Codex MCP connection without putting secrets in Git.
Run interactively; never pass passwords via CLI arguments. Restart/reopen the
Codex session afterwards. Successful initialize is not a write authorization.
"""
import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.request

if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11+ required.')
import tomllib


def merge_server(text, name, new_block):
    prefix = 'mcp_servers.' + name
    lines = text.splitlines(keepends=True)
    output = []
    skipping = False
    for line in lines:
        match = re.match(r'^\s*\[+([^\]]+)\]+\s*(?:#.*)?$', line.strip())
        if match:
            key = match.group(1).strip()
            skipping = key == prefix or key.startswith(prefix + '.')
        if not skipping:
            output.append(line)
    return ''.join(output).rstrip() + '\n\n' + new_block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://fegowoodworker.com/wp-json/elementor/mcp/')
    parser.add_argument('--name', default='fego-woodworker-elementor')
    parser.add_argument('--username', required=True)
    parser.add_argument('--replace', action='store_true', help='Replace this named server only')
    args = parser.parse_args()
    if not args.url.startswith('https://') or not re.fullmatch(r'[A-Za-z0-9_-]+', args.name):
        parser.error('HTTPS URL and simple server name required.')
    config_dir = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    path = config_dir / 'config.toml'
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    current = tomllib.loads(text)
    if args.name in current.get('mcp_servers', {}) and not args.replace:
        parser.error('Server already exists. Use --replace only if you intend to replace it.')
    password = getpass.getpass('WordPress Application Password (hidden): ')
    if not password.strip():
        parser.error('Password cannot be empty.')
    auth = 'Basic ' + base64.b64encode((args.username + ':' + ''.join(password.split())).encode()).decode()
    # Verify first; do not persist a failed connection or reveal error bodies/headers.
    payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-03-26', 'capabilities': {},
        'clientInfo': {'name': 'fego-category-setup', 'version': '1.0'}}}
    req = urllib.request.Request(args.url, data=json.dumps(payload).encode(), headers={
        'Authorization': auth, 'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'})
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.load(response)
        if 'serverInfo' not in result.get('result', {}):
            raise ValueError('MCP initialize failed')
    except Exception as exc:
        raise SystemExit('Connection check failed (' + type(exc).__name__ + '); config was not changed.')
    block = ('[mcp_servers.' + args.name + ']\nurl = ' + json.dumps(args.url) +
             '\n\n[mcp_servers.' + args.name + '.http_headers]\nAuthorization = ' + json.dumps(auth) + '\n')
    updated = merge_server(text, args.name, block)
    tomllib.loads(updated)
    config_dir.mkdir(parents=True, exist_ok=True)
    # Keep any backup outside the repository alongside the original private config.
    if path.exists():
        backup = config_dir / 'config.toml.fego-backup'
        backup.write_text(text, encoding='utf-8')
        backup.chmod(0o600)
    fd, temporary = tempfile.mkstemp(prefix='.fego-config-', dir=config_dir)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(updated)
        Path(temporary).chmod(0o600)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print('MCP initialize passed. Saved machine-local config:', path)
    print('Reopen the Codex session and verify tools/list. No website content changed.')
    print('This config/backup contains a credential: keep private; never commit or share it.')

if __name__ == '__main__':
    main()
