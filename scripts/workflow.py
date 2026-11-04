#!/usr/bin/env python3
"""Local source/deployment snapshot helper for the FEGO category workflow.

No network, credentials, approval prompts or CMS writes. A real user instruction
must authorize WordPress deployment; this helper only records the returned
Gemini source and verifies that the prepared deployment bundle is unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

REQUIRED_QA = ('target', 'facts', 'section_fit', 'seo', 'links', 'media', 'write_scope')


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
    if manifest.get('target') != state['target']:
        raise ValueError('Deployment target differs from the verified run target.')
    if manifest.get('source_sha256') != source['sha256']:
        raise ValueError('Manifest must identify the returned Gemini source hash.')
    files = manifest.get('files', [])
    if not isinstance(files, list) or not files or len(set(files)) != len(files):
        raise ValueError('Manifest needs a nonempty unique files list.')
    qa_name = manifest.get('qa_file')
    if qa_name not in files:
        raise ValueError('QA report must be covered by manifest files.')
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


def act(args):
    run = Path(args.run).resolve()
    if args.command == 'init':
        run.mkdir(parents=True, exist_ok=True)
        if (run / 'state.json').exists():
            raise ValueError('Run exists; refusing to overwrite history.')
        if not args.category_url.startswith('https://fegowoodworker.com/'):
            raise ValueError('Verify the FEGO HTTPS category URL first.')
        state = {'version': 2, 'status': 'drafting', 'target': {
            'category_url': args.category_url, 'taxonomy': 'product_cat',
            'term_id': args.term_id, 'block_id': args.block_id}, 'history': []}
    else:
        state = read(run / 'state.json')
    command = args.command
    if command == 'record-gemini':
        path = safe_file(run, args.file)
        state['gemini_source'] = {'file': str(path.relative_to(run)),
            'sha256': digest(path), 'message': args.message, 'at': timestamp()}
        state.pop('deployment', None)
        state['status'] = 'gemini_returned'
    elif command == 'prepare':
        state['deployment'] = snapshot(run, state, args.manifest)
        state['status'] = 'deployment_prepared'
    elif command == 'check-deploy':
        prepared = prepared_valid(run, state)
        print(json.dumps({'local_preflight': 'pass', 'deployment_sha256': prepared['sha256'],
            'note': 'Snapshot check only; confirm user deployment instruction, target identity, and live QA.'}))
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
    for name in ('init', 'record-gemini', 'prepare', 'check-deploy', 'status'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--run', required=True)
        if name == 'init':
            cmd.add_argument('--category-url', required=True)
            cmd.add_argument('--term-id', type=int, required=True)
            cmd.add_argument('--block-id', type=int)
        elif name == 'record-gemini':
            cmd.add_argument('--file', required=True)
            cmd.add_argument('--message', required=True)
        elif name == 'prepare':
            cmd.add_argument('--manifest', required=True)
    try:
        act(parser.parse_args())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, 'BLOCKED: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
