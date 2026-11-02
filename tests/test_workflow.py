import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('workflow', Path(__file__).parents[1] / 'scripts/workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        self.target = {'category_url': 'https://fegowoodworker.com/category/',
                       'taxonomy': 'product_cat', 'term_id': 1, 'block_id': 2}
        (self.run / 'approved.md').write_text('User returned Gemini content')
        (self.run / 'body.json').write_text('{"text":"SEO approved voice"}')
        (self.run / 'review.md').write_text('Full concrete review bundle')
        self.qa = {'checks': {key: 'pass' for key in w.REQUIRED_QA}}
        (self.run / 'qa.json').write_text(json.dumps(self.qa))
        self.state = {'target': self.target, 'content_approval': {
            'file': 'approved.md', 'sha256': w.digest(self.run / 'approved.md'),
            'gemini_edited': True, 'message': 'User approved version 2'}}
        self.manifest = {'target': self.target,
            'approved_content_sha256': self.state['content_approval']['sha256'],
            'files': ['approved.md', 'body.json', 'review.md', 'qa.json'],
            'review_file': 'review.md', 'qa_file': 'qa.json'}
        self.write_manifest()

    def write_manifest(self):
        (self.run / 'manifest.json').write_text(json.dumps(self.manifest))

    def prepare_exact(self):
        self.state['deployment'] = w.snapshot(self.run, self.state, 'manifest.json')
        self.state['publish_approval'] = {'mode': 'exact',
            'deployment_sha256': self.state['deployment']['sha256']}

    def test_closed_gate_one(self):
        self.state.pop('content_approval')
        with self.assertRaisesRegex(ValueError, 'Gate 1'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_source_changed_reopens_content_gate(self):
        self.prepare_exact()
        (self.run / 'approved.md').write_text('Different human content')
        with self.assertRaisesRegex(ValueError, 'Gate 1'):
            w.publish_ready(self.run, self.state)

    def test_gate_two_required(self):
        self.state['deployment'] = w.snapshot(self.run, self.state, 'manifest.json')
        with self.assertRaisesRegex(ValueError, 'Gate 2'):
            w.publish_ready(self.run, self.state)

    def test_exact_approval_passes(self):
        self.prepare_exact()
        self.assertEqual(w.publish_ready(self.run, self.state)['sha256'],
                         self.state['deployment']['sha256'])

    def test_payload_changed_blocks(self):
        self.prepare_exact()
        (self.run / 'body.json').write_text('{"text":"unreviewed"}')
        with self.assertRaisesRegex(ValueError, 'Deployment changed'):
            w.publish_ready(self.run, self.state)

    def test_changed_target_blocks(self):
        self.manifest['target'] = dict(self.target, block_id=99)
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'target differs'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_pending_qa_blocks(self):
        self.qa['checks']['facts'] = 'pending'
        (self.run / 'qa.json').write_text(json.dumps(self.qa))
        with self.assertRaisesRegex(ValueError, 'QA'):
            w.snapshot(self.run, self.state, 'manifest.json')

    def test_scoped_advance_approval(self):
        self.state['publish_approval'] = {'mode': 'advance', 'scope': 'seo_and_publish',
            'content_sha256': self.state['content_approval']['sha256'],
            'target': self.target, 'message': 'Tối ưu SEO rồi đăng luôn'}
        self.state['deployment'] = w.snapshot(self.run, self.state, 'manifest.json')
        self.assertTrue(w.publish_ready(self.run, self.state))
        self.state['publish_approval']['scope'] = 'research_only'
        with self.assertRaisesRegex(ValueError, 'Gate 2'):
            w.publish_ready(self.run, self.state)

    def test_paths_cannot_escape_run(self):
        with self.assertRaises(ValueError):
            w.safe_file(self.run, '../outside.txt')

if __name__ == '__main__':
    unittest.main()
