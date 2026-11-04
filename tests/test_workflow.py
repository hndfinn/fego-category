import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('workflow', Path(__file__).parents[1] / 'scripts/workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        self.target = {'category_url': 'https://fegowoodworker.com/category/',
                       'taxonomy': 'product_cat', 'term_id': 1, 'block_id': 2}
        (self.run / 'gemini-source.md').write_text('User returned Gemini content')
        (self.run / 'body.json').write_text('{"text":"Gemini voice"}')
        self.media = {'images': [{'section': 'H2 chọn theo không gian', 'file': 'a.webp',
                                  'alt': 'Kệ gỗ trong phòng khách',
                                  'provenance': 'generated_illustration'}]}
        self.write_json('media-map.json', self.media)
        self.qa = {'checks': {key: 'pass' for key in w.REQUIRED_QA}}
        self.write_json('qa.json', self.qa)
        self.write_json('backup.json', {'target': self.target,
                                        'objects': {'term': {}, 'block': {}}})
        self.state = {'target': self.target, 'history': [], 'gemini_source': {
            'file': 'gemini-source.md', 'sha256': w.digest(self.run / 'gemini-source.md'),
            'message': 'Đây là bản Gemini, đưa lên WordPress'}}
        self.manifest = {'target': self.target,
            'source_sha256': self.state['gemini_source']['sha256'],
            'files': ['gemini-source.md', 'body.json', 'media-map.json', 'qa.json'],
            'media_file': 'media-map.json', 'qa_file': 'qa.json'}
        self.write_json('manifest.json', self.manifest)

    def write_json(self, name, data):
        (self.run / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def prepare(self):
        self.state['deployment'] = w.snapshot(self.run, self.state, 'manifest.json')

    def backed_up(self):
        self.prepare()
        self.state['backup'] = w.backup_snapshot(self.run, self.state, 'backup.json')

    def test_gemini_source_required(self):
        self.state.pop('gemini_source')
        with self.assertRaisesRegex(ValueError, 'Gemini source'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_source_changed_blocks(self):
        self.backed_up()
        (self.run / 'gemini-source.md').write_text('Different content')
        with self.assertRaisesRegex(ValueError, 'Gemini source changed'):
            w.deploy_ready(self.run, self.state)

    def test_no_approval_gate_after_backup(self):
        self.backed_up()
        self.assertEqual(w.deploy_ready(self.run, self.state)['sha256'],
                         self.state['deployment']['sha256'])

    def test_backup_required_before_deploy(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'Back up'):
            w.deploy_ready(self.run, self.state)

    def test_backup_must_match_target_and_have_objects(self):
        self.prepare()
        self.write_json('backup.json', {'target': dict(self.target, block_id=9), 'objects': {'x': 1}})
        with self.assertRaisesRegex(ValueError, 'target differs'):
            w.backup_snapshot(self.run, self.state, 'backup.json')
        self.write_json('backup.json', {'target': self.target, 'objects': {}})
        with self.assertRaisesRegex(ValueError, 'live objects'):
            w.backup_snapshot(self.run, self.state, 'backup.json')

    def test_payload_changed_blocks(self):
        self.backed_up()
        (self.run / 'body.json').write_text('{"text":"changed"}')
        with self.assertRaisesRegex(ValueError, 'bundle changed'):
            w.deploy_ready(self.run, self.state)

    def test_changed_block_blocks(self):
        self.manifest['target'] = dict(self.target, block_id=99)
        self.write_json('manifest.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'target differs'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_missing_block_id_blocks(self):
        self.target['block_id'] = None
        self.manifest['target'] = self.target
        self.write_json('manifest.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'block ID'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_pending_qa_blocks(self):
        self.qa['checks']['media_mapping'] = 'pending'
        self.write_json('qa.json', self.qa)
        with self.assertRaisesRegex(ValueError, 'QA'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_media_map_requires_section_alt_provenance(self):
        self.media['images'][0].pop('section')
        self.write_json('media-map.json', self.media)
        with self.assertRaisesRegex(ValueError, 'section'):
            w.snapshot(self.run, self.state, 'manifest.json')
        self.media['images'][0].update(section='Intro', provenance='customer_photo')
        self.write_json('media-map.json', self.media)
        with self.assertRaisesRegex(ValueError, 'provenance'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_templates_match_required_checks(self):
        root = Path(__file__).parents[1] / 'templates'
        qa = json.loads((root / 'qa-preflight.json').read_text(encoding='utf-8'))
        live = json.loads((root / 'live-qa.json').read_text(encoding='utf-8'))
        manifest = json.loads((root / 'deployment-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(set(qa['checks']), set(w.REQUIRED_QA))
        self.assertEqual(set(live['checks']), set(w.LIVE_QA))
        self.assertIn(manifest['media_file'], manifest['files'])
        self.assertIn(manifest['qa_file'], manifest['files'])
        self.assertIn('source_sha256', manifest)

    def test_cli_flow_complete_and_needs_attention(self):
        w.act(Args(command='init', run=str(self.run / 'r'), term_id=1, block_id=2,
                   category_url='https://fegowoodworker.com/category/'))
        run = self.run / 'r'
        for name in ('gemini-source.md', 'body.json', 'media-map.json', 'qa.json',
                     'manifest.json', 'backup.json'):
            (run / name).write_bytes((self.run / name).read_bytes())
        w.act(Args(command='record-draft', run=str(run),
                   doc='https://docs.google.com/document/d/x', media='media-map.json'))
        w.act(Args(command='record-gemini', run=str(run), file='gemini-source.md', message='m'))
        w.act(Args(command='prepare', run=str(run), manifest='manifest.json'))
        w.act(Args(command='record-backup', run=str(run), file='backup.json'))
        live = {'target': self.target, 'checks': {key: 'pass' for key in w.LIVE_QA}}
        live['checks']['render'] = 'unverified'
        (run / 'live.json').write_text(json.dumps(live), encoding='utf-8')
        w.act(Args(command='record-live-qa', run=str(run), file='live.json'))
        state = w.read(run / 'state.json')
        self.assertEqual(state['status'], 'needs_attention')
        self.assertEqual(state['live_qa']['failed'], ['render'])
        live['checks']['render'] = 'pass'
        (run / 'live.json').write_text(json.dumps(live), encoding='utf-8')
        w.act(Args(command='record-live-qa', run=str(run), file='live.json'))
        self.assertEqual(w.read(run / 'state.json')['status'], 'complete')

    def test_image_routing_copies_in_sync(self):
        root = Path(__file__).parents[1]
        docs = (root / 'docs/FEGO_IMAGE_SKILL.md').read_text(encoding='utf-8').splitlines()
        skill = (root / '.agents/skills/fego-category/references/shared-image-routing.md'
                 ).read_text(encoding='utf-8').splitlines()
        self.assertEqual(docs, skill)

    def test_paths_cannot_escape_run(self):
        with self.assertRaises(ValueError):
            w.safe_file(self.run, '../outside.txt')


if __name__ == '__main__':
    unittest.main()
