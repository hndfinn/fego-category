#!/usr/bin/env python3
"""Local approval/snapshot preflight. No network, credentials or CMS writes.
Approval messages must come from an actual human instruction; this program cannot
verify identity or substitute for tool permissions or live QA.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

REQUIRED_QA = ('targets', 'facts', 'approved_voice', 'headings', 'placement',
               'seo', 'links', 'media', 'review_bundle', 'write_scope')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(run, state):
    path = Path(run) / 'state.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)

def safe_file(run, name):
    root = Path(run).resolve()
    p = (root / name).resolve()
    if not p.is_relative_to(root) or not p.is_file():
        raise ValueError('Required file missing or outside run directory: ' + str(name))
    return p

def content_valid(run, state):
    approval = state.get('content_approval')
    if not approval or not approval.get('gemini_edited'):
        raise ValueError('Gate 1 is closed: user/Gemini content approval required.')
    if digest(safe_file(run, approval['file'])) != approval['sha256']:
        raise ValueError('Approved content changed. Reopen Gate 1.')
    return approval

def snapshot(run, state, manifest_name):
    approval = content_valid(run, state)
    path = safe_file(run, manifest_name)
    manifest = read(path)
    if manifest.get('target') != state['target']:
        raise ValueError('Deployment target differs from approved run target.')
    if manifest.get('approved_content_sha256') != approval['sha256']:
        raise ValueError('Manifest must identify the Gate 1 source hash.')
    files = manifest.get('files', [])
    if not isinstance(files, list) or not files or len(set(files)) != len(files):
        raise ValueError('Manifest needs a nonempty unique files list.')
    qa_name = manifest.get('qa_file')
    review_name = manifest.get('review_file')
    if qa_name not in files or review_name not in files:
        raise ValueError('QA and full review bundle must be covered by manifest files.')
    qa = read(safe_file(run, qa_name))
    if any(qa.get('checks', {}).get(key) != 'pass' for key in REQUIRED_QA):
        raise ValueError('Required preparation QA checks must all pass.')
    hashes = {name: digest(safe_file(run, name)) for name in files}
    payload = {'manifest': manifest, 'files': hashes}
    return {'manifest_file': str(path.relative_to(Path(run).resolve())),
            'sha256': hashlib.sha256(canonical(payload)).hexdigest(),
            'files': hashes}

def prepared_valid(run, state):
    previous = state.get('deployment')
    if not previous:
        raise ValueError('Prepare a concrete deployment bundle first.')
    current = snapshot(run, state, previous['manifest_file'])
    if current['sha256'] != previous['sha256']:
        raise ValueError('Deployment changed. Prepare again and renew Gate 2 if needed.')
    return current

def publish_ready(run, state):
    approval = content_valid(run, state)
    prepared = prepared_valid(run, state)
    gate = state.get('publish_approval', {})
    exact = gate.get('deployment_sha256') == prepared['sha256']
    advance = (gate.get('mode') == 'advance' and
               gate.get('scope') == 'seo_and_publish' and
               gate.get('content_sha256') == approval['sha256'] and
               gate.get('target') == state['target'])
    if not (exact or advance):
        raise ValueError('Gate 2 is closed: exact deployment or scoped advance approval required.')
    return prepared

def act(args):
    run = Path(args.run).resolve()
    if args.command == 'init':
        run.mkdir(parents=True, exist_ok=True)
        if (run / 'state.json').exists():
            raise ValueError('Run exists; refusing to overwrite approval history.')
        if not args.category_url.startswith('https://fegowoodworker.com/'):
            raise ValueError('Verify the FEGO HTTPS category URL first.')
        state = {'version': 1, 'status': 'researching', 'target': {
            'category_url': args.category_url, 'taxonomy': 'product_cat',
            'term_id': args.term_id, 'block_id': args.block_id}, 'history': []}
    else:
        state = read(run / 'state.json')
    command = args.command
    if command == 'approve-content':
        path = safe_file(run, args.file)
        state['content_approval'] = {'file': str(path.relative_to(run)),
            'sha256': digest(path), 'message': args.message,
            'gemini_edited': args.gemini_edited, 'at': timestamp()}
        if not args.gemini_edited:
            raise ValueError('Confirm user returned the Gemini-edited content.')
        state.pop('deployment', None)
        state.pop('publish_approval', None)
        state['status'] = 'content_approved'
    elif command == 'prepare':
        state['deployment'] = snapshot(run, state, args.manifest)
        if state.get('publish_approval', {}).get('mode') != 'advance':
            state.pop('publish_approval', None)
        state['status'] = 'awaiting_publish_approval'
    elif command == 'approve-publish':
        content = content_valid(run, state)
        if args.advance:
            state['publish_approval'] = {'mode': 'advance', 'scope': 'seo_and_publish',
                'content_sha256': content['sha256'], 'target': state['target'],
                'message': args.message, 'at': timestamp()}
        else:
            prepared = prepared_valid(run, state)
            state['publish_approval'] = {'mode': 'exact',
                'deployment_sha256': prepared['sha256'],
                'message': args.message, 'at': timestamp()}
        state['status'] = 'publish_approved'
    elif command == 'check-publish':
        prepared = publish_ready(run, state)
        print(json.dumps({'local_preflight': 'pass', 'deployment_sha256': prepared['sha256'],
            'note': 'Not proof of human identity, website permissions, or live success.'}))
        return
    elif command == 'status':
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    state['history'].append({'command': command, 'at': timestamp()})
    save(run, state)
    print(json.dumps({'status': state['status'], 'state_file': str(run / 'state.json')}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'approve-content', 'prepare', 'approve-publish', 'check-publish', 'status'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--run', required=True)
        if name == 'init':
            cmd.add_argument('--category-url', required=True)
            cmd.add_argument('--term-id', type=int, required=True)
            cmd.add_argument('--block-id', type=int, required=True)
        elif name == 'approve-content':
            cmd.add_argument('--file', required=True)
            cmd.add_argument('--message', required=True)
            cmd.add_argument('--gemini-edited', action='store_true')
        elif name == 'prepare':
            cmd.add_argument('--manifest', required=True)
        elif name == 'approve-publish':
            cmd.add_argument('--message', required=True)
            cmd.add_argument('--advance', action='store_true')
    try:
        act(parser.parse_args())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, 'BLOCKED: ' + str(exc) + '\n')

if __name__ == '__main__':
    main()
