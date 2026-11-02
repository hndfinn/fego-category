#!/usr/bin/env python3
"""Idempotent cloud MCP setup and read-only readiness check. Never logs credentials."""
import argparse
import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import tomllib
import urllib.error
import urllib.request

from connect_elementor import merge_server

ENDPOINT = 'https://fegowoodworker.com/wp-json/elementor/mcp/'
NAME = 'fego-woodworker-elementor'


class SetupError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an Authorization header to a redirected destination.
        return None


class Client:
    def __init__(self, headers):
        self.headers = dict(headers)
        self.session = None
        self.protocol = None
        self.opener = urllib.request.build_opener(NoRedirect)

    def rpc(self, method, params=None, ident=None):
        body = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            body['params'] = params
        if ident is not None:
            body['id'] = ident
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json',
                        'Accept': 'application/json, text/event-stream'})
        if self.session:
            headers['Mcp-Session-Id'] = self.session
        if self.protocol:
            headers['MCP-Protocol-Version'] = self.protocol
        request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers=headers)
        try:
            with self.opener.open(request, timeout=30) as response:
                self.session = response.headers.get('Mcp-Session-Id', self.session)
                if ident is None:
                    return None
                # Read bounded data; SSE streams need not close after a response.
                if 'text/event-stream' in response.headers.get('Content-Type', ''):
                    parts = []
                    total = 0
                    while total < 2_000_000:
                        line = response.readline(262144)
                        if not line:
                            break
                        total += len(line)
                        line = line.decode('utf-8').rstrip('\r\n')
                        if line.startswith('data:'):
                            parts.append(line[5:].lstrip(' '))
                        elif not line and parts:
                            message = json.loads('\n'.join(parts))
                            parts = []
                            if message.get('id') == ident:
                                return self.result(message)
                    raise SetupError('No matching bounded MCP response received.')
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise SetupError('MCP response exceeded the readiness-check limit.')
                message = json.loads(raw)
                if message.get('id') != ident:
                    raise SetupError('MCP response ID mismatch.')
                return self.result(message)
        except urllib.error.HTTPError as exc:
            # Do not print response bodies, URLs, headers or exception repr.
            raise SetupError('MCP HTTP ' + str(exc.code) + '; check cloud egress and authentication.') from None
        except (OSError, ValueError) as exc:
            raise SetupError('MCP transport failed (' + type(exc).__name__ + ').') from None

    @staticmethod
    def result(message):
        if 'error' in message or not isinstance(message.get('result'), dict):
            raise SetupError('MCP returned a protocol error; no configuration changed.')
        return message['result']

    def verify(self):
        result = self.rpc('initialize', {
            'protocolVersion': '2025-03-26', 'capabilities': {},
            'clientInfo': {'name': 'fego-cloud-readiness', 'version': '1.0'}}, 1)
        if not result.get('serverInfo') or not result.get('protocolVersion'):
            raise SetupError('MCP initialize did not identify a server and protocol.')
        self.protocol = result['protocolVersion']
        self.rpc('notifications/initialized')
        cursor = None
        seen = set()
        names = set()
        for page in range(100):
            result = self.rpc('tools/list', {'cursor': cursor} if cursor else {}, page + 2)
            entries = result.get('tools')
            if not isinstance(entries, list):
                raise SetupError('tools/list did not return a tools array.')
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get('name'), str):
                    names.add(entry['name'])
            cursor = result.get('nextCursor')
            if not cursor:
                if not names:
                    raise SetupError('Server exposes no callable tools.')
                return sorted(names)
            if cursor in seen:
                raise SetupError('Repeated tools/list cursor.')
            seen.add(cursor)
        raise SetupError('tools/list exceeded the page limit.')


def select_connection(text, env):
    data = tomllib.loads(text)
    servers = data.get('mcp_servers', {})
    matches = [(name, value) for name, value in servers.items()
               if isinstance(value, dict) and value.get('url', '').rstrip('/') == ENDPOINT.rstrip('/')]
    if len(matches) > 1:
        raise SetupError('Multiple Elementor connections exist; select one manually before setup.')
    if matches:
        name, server = matches[0]
        headers = dict(server.get('http_headers', {}))
        for key, variable in server.get('env_http_headers', {}).items():
            if not env.get(variable):
                raise SetupError('An existing MCP header environment binding is missing.')
            headers[key] = env[variable]
        bearer = server.get('bearer_token_env_var')
        if bearer:
            if not env.get(bearer):
                raise SetupError('The existing MCP bearer environment binding is missing.')
            headers['Authorization'] = 'Bearer ' + env[bearer]
        return name, headers, False
    if NAME in servers:
        raise SetupError('The Elementor server name already points elsewhere; refusing to replace it.')
    user = env.get('FEGO_WP_USERNAME', '').strip()
    password = ''.join(env.get('FEGO_WP_APPLICATION_PASSWORD', '').split())
    if not user or not password:
        raise SetupError('No existing Elementor MCP in this runtime. Cloud secrets '
                         'FEGO_WP_USERNAME and FEGO_WP_APPLICATION_PASSWORD are not both supplied. '
                         'No configuration changed; an existing saved cloud setup may not be attached here.')
    if ':' in user:
        raise SetupError('WordPress username cannot contain a colon.')
    auth = 'Basic ' + base64.b64encode((user + ':' + password).encode()).decode()
    return NAME, {'Authorization': auth}, True


def persist(path, text, name, headers):
    # Secret-bearing config stays outside every Git checkout.
    for parent in [path.parent, *path.parent.parents]:
        if (parent / '.git').exists():
            raise SetupError('Refusing to store secret-bearing MCP config inside a Git checkout.')
    block = ('[mcp_servers.' + name + ']\nurl = ' + json.dumps(ENDPOINT) +
             '\n\n[mcp_servers.' + name + '.http_headers]\n' +
             ''.join(json.dumps(k) + ' = ' + json.dumps(v) + '\n' for k, v in headers.items()))
    updated = merge_server(text, name, block)
    tomllib.loads(updated)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.fego-cloud-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(updated)
        Path(temp).chmod(0o600)
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Probe existing/injected credentials without saving config.')
    args = parser.parse_args()
    path = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'config.toml'
    try:
        text = path.read_text(encoding='utf-8') if path.exists() else ''
        name, headers, fresh = select_connection(text, os.environ)
        names = Client(headers).verify()
        if fresh and not args.check_only:
            persist(path, text, name, headers)
        print(json.dumps({'mcp_readiness': 'pass', 'initialize': 'pass',
                          'tools_list': 'pass', 'tool_count': len(names), 'tool_names': names,
                          'connection': 'new_not_saved' if fresh and args.check_only else
                          'saved' if fresh else 'reused',
                          'cms_writes': False,
                          'note': 'Transport/tools verified. Native chat tool registration, object permissions '
                                  'and other devices still require a new cloud-session test.'}))
    except (SetupError, OSError, ValueError) as exc:
        if isinstance(exc, SetupError):
            print(str(exc), file=sys.stderr)
        else:
            print('Cloud setup failed (' + type(exc).__name__ + '); credentials not logged.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
