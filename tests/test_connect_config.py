import importlib.util
from pathlib import Path
import tomllib
import unittest

spec = importlib.util.spec_from_file_location('connect', Path(__file__).parents[1] / 'scripts/connect_elementor.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ConfigTests(unittest.TestCase):
    def test_replace_preserves_other_servers_and_array_tables(self):
        source = '''model = "example"
[mcp_servers.fego]
url = "https://old.example/"
[mcp_servers.fego.http_headers]
Authorization = "FAKE_OLD"
[[projects]]
path = "example"
[mcp_servers.other]
command = "other-server"
'''
        block = '[mcp_servers.fego]\nurl = "https://new.example/"\n'
        result = tomllib.loads(m.merge_server(source, 'fego', block))
        self.assertEqual(result['model'], 'example')
        self.assertEqual(result['projects'], [{'path': 'example'}])
        self.assertEqual(result['mcp_servers']['other']['command'], 'other-server')
        self.assertNotIn('http_headers', result['mcp_servers']['fego'])
        self.assertEqual(result['mcp_servers']['fego']['url'], 'https://new.example/')

    def test_new_config(self):
        result = tomllib.loads(m.merge_server('', 'fego', '[mcp_servers.fego]\nurl="https://example.com/"\n'))
        self.assertIn('fego', result['mcp_servers'])

if __name__ == '__main__':
    unittest.main()
