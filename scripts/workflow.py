#!/usr/bin/env python3
"""Local source/deployment snapshot helper for the FEGO category workflow.

Flow: Google Doc draft + mapped images (one pass) -> user rewrites with Gemini ->
deploy the Gemini version to WordPress. No network, credentials, approval prompts
or CMS writes. A real user instruction must direct WordPress deployment; this
helper only records the draft/Gemini source, verifies the category/block target,
media mapping, preparation QA, pre-write backup and post-publish live QA.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

REQUIRED_QA = ('target', 'block', 'facts', 'section_fit', 'headings', 'placement',
               'seo', 'links', 'media_mapping', 'write_scope')
LIVE_QA = ('public_status', 'api_readback', 'single_h1', 'placement', 'seo',
           'links', 'media', 'render', 'publish_state')
PROVENANCE = ('real_product', 'generated_illustration')


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


def check_target(state, data, label):
    if data.get('target') != state['target']:
        raise ValueError(label + ' target differs from the verified run target.')
    if not state['target'].get('term_id') or not state['target'].get('block_id'):
        raise ValueError('Verified term ID and content block ID are required.')


def media_valid(run, name):
    media = read(safe_file(run, name))
    images = media.get('images')
    if not isinstance(images, list):
        raise ValueError('Media map needs an images list.')
    for item in images:
        if not isinstance(item, dict) or not item.get('section') or not item.get('file'):
            raise ValueError('Every media entry needs a section and file.')
        if 'alt' not in item or item.get('provenance') not in PROVENANCE:
            raise ValueError('Every media entry needs alt and provenance '
                             + '/'.join(PROVENANCE) + '.')
    return media


def source_valid(run, state):
    source = state.get('gemini_source')
    if not source:
        raise ValueError('Record the user-returned Gemini source before deployment preparation.')
    if digest(safe_file(run, source['file'])) != source['sha256']:
        raise ValueError('Gemini source changed; record its current snapshot.')
    return source


def snapshot(run, state, manifest_name):
    source = source_valid(run, state)
    path = safe_file(run, manifest_name)
    manifest = read(path)
    check_target(state, manifest, 'Deployment')
    if manifest.get('source_sha256') != source['sha256']:
        raise ValueError('Manifest must identify the returned Gemini source hash.')
    files = manifest.get('files', [])
    if not isinstance(files, list) or not files or len(set(files)) != len(files):
        raise ValueError('Manifest needs a nonempty unique files list.')
    if source['file'] not in files:
        raise ValueError('Gemini source must be covered by manifest files.')
    qa_name = manifest.get('qa_file')
    media_name = manifest.get('media_file')
    if qa_name not in files or media_name not in files:
        raise ValueError('QA report and media map must be covered by manifest files.')
    media_valid(run, media_name)
    qa = read(safe_file(run, qa_name))
    if any(qa.get('checks', {}).get(key) != 'pass' for key in REQUIRED_QA):
        raise ValueError('Required deployment QA checks must all pass.')
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
        raise ValueError('Deployment bundle changed; prepare its current snapshot again.')
    return current


def backup_snapshot(run, state, name):
    path = safe_file(run, name)
    backup = read(path)
    check_target(state, backup, 'Backup')
    if not backup.get('objects'):
        raise ValueError('Backup must contain the current live objects (term, SEO, block).')
    return {'file': str(path.relative_to(Path(run).resolve())), 'sha256': digest(path)}


def backup_valid(run, state):
    previous = state.get('backup')
    if not previous:
        raise ValueError('Back up current live values before WordPress writes.')
    if backup_snapshot(run, state, previous['file'])['sha256'] != previous['sha256']:
        raise ValueError('Backup file changed; take and record a fresh backup.')
    return previous


def deploy_ready(run, state):
    prepared = prepared_valid(run, state)
    backup_valid(run, state)
    return prepared


def act(args):
    run = Path(args.run).resolve()
    if args.command == 'init':
        run.mkdir(parents=True, exist_ok=True)
        if (run / 'state.json').exists():
            raise ValueError('Run exists; refusing to overwrite history.')
        if not args.category_url.startswith('https://fegowoodworker.com/'):
            raise ValueError('Verify the FEGO HTTPS category URL first.')
        state = {'version': 3, 'status': 'drafting', 'target': {
            'category_url': args.category_url, 'taxonomy': 'product_cat',
            'term_id': args.term_id, 'block_id': args.block_id}, 'history': []}
    else:
        state = read(run / 'state.json')
    command = args.command
    if command == 'record-draft':
        if not args.doc.startswith('https://docs.google.com/'):
            raise ValueError('Draft must be a Google Doc URL.')
        media_valid(run, args.media)
        state['draft'] = {'doc': args.doc, 'media_file': args.media,
            'media_sha256': digest(safe_file(run, args.media)), 'at': timestamp()}
        state['status'] = 'draft_ready'
    elif command == 'record-gemini':
        path = safe_file(run, args.file)
        state['gemini_source'] = {'file': str(path.relative_to(run)),
            'sha256': digest(path), 'message': args.message, 'at': timestamp()}
        for key in ('deployment', 'backup', 'live_qa'):
            state.pop(key, None)
        state['status'] = 'gemini_returned'
    elif command == 'prepare':
        state['deployment'] = snapshot(run, state, args.manifest)
        state.pop('backup', None)
        state.pop('live_qa', None)
        state['status'] = 'deployment_prepared'
    elif command == 'record-backup':
        prepared_valid(run, state)
        state['backup'] = dict(backup_snapshot(run, state, args.file), at=timestamp())
        state['status'] = 'backed_up'
    elif command == 'check-deploy':
        prepared = deploy_ready(run, state)
        print(json.dumps({'local_preflight': 'pass', 'deployment_sha256': prepared['sha256'],
            'note': 'Snapshot check only; confirm user deployment instruction, re-read live target, then verify live QA.'}))
        return
    elif command == 'record-live-qa':
        deploy_ready(run, state)
        path = safe_file(run, args.file)
        live = read(path)
        check_target(state, live, 'Live QA')
        failed = [key for key in LIVE_QA if live.get('checks', {}).get(key) != 'pass']
        state['live_qa'] = {'file': str(path.relative_to(run)), 'sha256': digest(path),
            'failed': failed, 'at': timestamp()}
        state['status'] = 'needs_attention' if failed else 'complete'
    elif command == 'status':
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    state['history'].append({'command': command, 'at': timestamp()})
    save(run, state)
    print(json.dumps({'status': state['status'], 'state_file': str(run / 'state.json')}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'record-draft', 'record-gemini', 'prepare', 'record-backup',
                 'check-deploy', 'record-live-qa', 'status'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--run', required=True)
        if name == 'init':
            cmd.add_argument('--category-url', required=True)
            cmd.add_argument('--term-id', type=int, required=True)
            cmd.add_argument('--block-id', type=int, required=True)
        elif name == 'record-draft':
            cmd.add_argument('--doc', required=True)
            cmd.add_argument('--media', required=True)
        elif name == 'record-gemini':
            cmd.add_argument('--file', required=True)
            cmd.add_argument('--message', required=True)
        elif name == 'prepare':
            cmd.add_argument('--manifest', required=True)
        elif name in ('record-backup', 'record-live-qa'):
            cmd.add_argument('--file', required=True)
    try:
        act(parser.parse_args())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, 'BLOCKED: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
