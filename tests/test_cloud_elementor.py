import importlib.util
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import cloud_elementor as m


class CloudTests(unittest.TestCase):
    def test_existing_config_wins_over_new_credentials(self):
        text = '[mcp_servers.existing]\nurl="' + m.ENDPOINT + '"\n[mcp_servers.existing.http_headers]\nAuthorization="FAKE_EXISTING"\n'
        name, headers, fresh = m.select_connection(text, {'FEGO_WP_USERNAME': 'new', 'FEGO_WP_APPLICATION_PASSWORD': 'fake'})
        self.assertEqual((name, headers['Authorization'], fresh), ('existing', 'FAKE_EXISTING', False))

    def test_missing_binding_never_replaces_existing(self):
        text = '[mcp_servers.existing]\nurl="' + m.ENDPOINT + '"\n[mcp_servers.existing.env_http_headers]\nAuthorization="MISSING"\n'
        with self.assertRaises(m.SetupError):
            m.select_connection(text, {'FEGO_WP_USERNAME': 'user', 'FEGO_WP_APPLICATION_PASSWORD': 'fake'})

    def test_missing_credentials_do_not_leak(self):
        with self.assertRaises(m.SetupError) as cm:
            m.select_connection('', {'FEGO_WP_USERNAME': 'FAKE_PRIVATE_USERNAME'})
        self.assertNotIn('FAKE_PRIVATE_USERNAME', str(cm.exception))

    def test_persist_preserves_other_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.toml'
            text = '[mcp_servers.other]\ncommand="example"\n'
            m.persist(path, text, m.NAME, {'Authorization': 'FAKE_TEST'})
            data = tomllib.loads(path.read_text())
            self.assertEqual(data['mcp_servers']['other']['command'], 'example')
            self.assertEqual(data['mcp_servers'][m.NAME]['http_headers']['Authorization'], 'FAKE_TEST')

    def test_refuses_secret_config_in_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / '.git').mkdir()
            with self.assertRaises(m.SetupError):
                m.persist(Path(tmp) / '.codex/config.toml', '', m.NAME, {'Authorization': 'FAKE'})

    def test_handshake_notification_and_paginated_tools(self):
        client = m.Client({})
        replies = [{'serverInfo': {'name': 'test'}, 'protocolVersion': '2025-03-26'},
                   None, {'tools': [{'name': 'read-object'}], 'nextCursor': 'p2'},
                   {'tools': [{'name': 'get-site'}]}]
        with patch.object(client, 'rpc', side_effect=replies) as rpc:
            self.assertEqual(client.verify(), ['get-site', 'read-object'])
            self.assertEqual(rpc.call_args_list[1].args, ('notifications/initialized',))
            self.assertEqual(rpc.call_args_list[3].args[1], {'cursor': 'p2'})

    def test_empty_tools_is_not_ready(self):
        client = m.Client({})
        with patch.object(client, 'rpc', side_effect=[{'serverInfo': {'name': 't'}, 'protocolVersion': '2025-03-26'}, None, {'tools': []}]):
            with self.assertRaises(m.SetupError):
                client.verify()


if __name__ == '__main__':
    unittest.main()
