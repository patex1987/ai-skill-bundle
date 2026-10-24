#!/usr/bin/env python3
"""Validate the AI catalog and install selected entities into repositories.

    aibundle.py list                         packs and entities
    aibundle.py validate                     catalog structure, packs, links, portability
    aibundle.py init    --repo R --pack P…   write R/.ai/bundle.json
    aibundle.py install --repo R [--dry-run] sync R/.ai/ with its bundle.json
    aibundle.py status  --repo R             managed, modified, and outdated entities

Installation only writes canonical files under R/.ai/ and records them in
R/.ai/bundle-lock.json. Assistant folders are produced afterwards by the
vendored renderer: python3 R/.ai/render.py. Python standard library only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import render  # noqa: E402  (shared frontmatter parser and constants)

KINDS = ('skills', 'agents', 'rules')
SUPPORT_FILES = {'render.py': ROOT / 'scripts' / 'render.py', 'routing.json': ROOT / 'routing' / 'tiers.json'}
METADATA_KEYS = {'routing-tier', 'routing-effort', 'invocation', 'context', 'agent', 'tags', 'max-turns', 'skills'}
SKILL_FRONT_KEYS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
AGENT_FRONT_KEYS = {'name', 'description', 'access', 'metadata'}
RULE_FRONT_KEYS = {'name', 'description', 'always-apply', 'paths', 'metadata'}
LOCK_VERSION = 2


class BundleError(Exception):
    pass


# --- Catalog -------------------------------------------------------------------

def digest(path):
    """Content digest over relative names, executable bits, and bytes."""
    files = [path] if path.is_file() else sorted(p for p in path.rglob('*'))
    rows = []
    for file in files:
        if file.is_symlink():
            raise BundleError(f'symlink not allowed: {file}')
        mode = file.stat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise BundleError(f'non-regular file: {file}')
        relative = '.' if path.is_file() else file.relative_to(path).as_posix()
        rows.append([relative, bool(mode & 0o111), hashlib.sha256(file.read_bytes()).hexdigest()])
    return hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def entity_path(base, kind, name):
    return base / kind / name if kind == 'skills' else base / kind / f'{name}.md'


def catalog_entities():
    found = {}
    for kind in KINDS:
        folder = ROOT / 'catalog' / kind
        for item in sorted(folder.iterdir()) if folder.is_dir() else []:
            if item.name.startswith('.'):
                continue
            name = item.name if kind == 'skills' else item.stem
            if (kind == 'skills') != item.is_dir() or (kind != 'skills' and item.suffix != '.md'):
                raise BundleError(f'unexpected catalog entry: {item.relative_to(ROOT)}')
            found[(kind, name)] = item
    return found


def load_packs():
    packs = {}
    for file in sorted((ROOT / 'packs').glob('*.json')):
        data = json.loads(file.read_text())
        unknown = set(data) - {'description', 'requires', *KINDS}
        if unknown:
            raise BundleError(f'{file.name}: unknown keys {sorted(unknown)}')
        packs[file.stem] = data
    return packs


def resolve_packs(names, packs):
    order, seen = [], set()

    def visit(name, trail):
        if name in trail:
            raise BundleError(f'pack cycle: {" -> ".join(trail + [name])}')
        if name not in packs:
            raise BundleError(f'unknown pack: {name}')
        if name in seen:
            return
        for required in packs[name].get('requires', []):
            visit(required, trail + [name])
        seen.add(name)
        order.append(name)

    for name in names:
        visit(name, [])
    return order


def selection(manifest, packs, entities):
    pack_order = resolve_packs(manifest.get('packs', []), packs)
    chosen = {}
    for pack in pack_order:
        for kind in KINDS:
            for name in packs[pack].get(kind, []):
                chosen.setdefault((kind, name), []).append(pack)
    for kind in KINDS:
        spec = manifest.get(kind, {})
        for name in spec.get('add', []):
            chosen.setdefault((kind, name), []).append('manifest')
        for name in spec.get('remove', []):
            if (kind, name) not in chosen:
                raise BundleError(f'bundle.json: {kind}.remove names unselected entity {name!r}')
            chosen.pop((kind, name))
    for key in chosen:
        if key not in entities:
            raise BundleError(f'unknown catalog entity {key[0]}/{key[1]}')
    for (kind, name) in chosen:
        if kind != 'agents':
            continue
        for skill in agent_skills(entities[(kind, name)]):
            if ('skills', skill) not in chosen:
                raise BundleError(f'agent {name!r} uses skill {skill!r}, which is not selected; '
                                  f'add it under "skills": {{"add": [...]}} in bundle.json or remove the agent')
    return pack_order, chosen


def agent_skills(path):
    """Skills an agent declares in metadata.skills (it reads or preloads them at start)."""
    try:
        front, _ = render.parse_frontmatter(path.read_text(), str(path))
    except (render.RenderError, OSError):
        return []  # reported by validate_catalog
    meta = front.get('metadata', {})
    skills = meta.get('skills', []) if isinstance(meta, dict) else []
    if isinstance(skills, str):
        return [skills]
    return [s for s in skills if isinstance(s, str)] if isinstance(skills, list) else []


# --- Validation ------------------------------------------------------------------

LINK_RE = re.compile(r'\]\(([^)#\s]+)(?:#[^)]*)?\)')


def lint_patterns():
    file = ROOT / 'catalog' / 'lint.json'
    data = json.loads(file.read_text()) if file.is_file() else {}
    return [(re.compile(p['pattern'], re.I if p.get('ignore_case', True) else 0), p['reason'])
            for p in data.get('forbidden', [])]


def validate_evals(skill_dir, name):
    """Check the optional evals/evals.json validation examples of a skill."""
    file = skill_dir / 'evals' / 'evals.json'
    if not file.exists():
        return []
    where = file.relative_to(ROOT)
    try:
        data = json.loads(file.read_text())
    except json.JSONDecodeError as error:
        return [f'{where}: invalid JSON: {error}']
    if not isinstance(data, dict) or data.get('skill_name') != name:
        return [f'{where}: skill_name must be {name!r}']
    cases = data.get('evals')
    if not isinstance(cases, list) or not cases:
        return [f'{where}: evals must be a non-empty list']
    problems, ids = [], set()
    for number, case in enumerate(cases, start=1):
        label = f'{where}: eval #{number}'
        if not isinstance(case, dict):
            problems.append(f'{label} must be an object')
            continue
        if not isinstance(case.get('id'), int) or case['id'] in ids:
            problems.append(f'{label} needs a unique integer id')
        ids.add(case.get('id'))
        if not isinstance(case.get('prompt'), str) or not case['prompt'].strip():
            problems.append(f'{label} needs a prompt')
        expectations = case.get('expectations')
        if not isinstance(expectations, list) or not expectations or \
                not all(isinstance(e, str) and e.strip() for e in expectations):
            problems.append(f'{label} needs a non-empty list of expectations')
        for target in case.get('files', []):
            resolved = (skill_dir / str(target)).resolve()
            if not resolved.is_relative_to(skill_dir.resolve()) or not resolved.is_file():
                problems.append(f'{label}: file {target!r} must exist inside the skill directory')
    return problems


def validate_catalog():
    problems = []
    entities = catalog_entities()
    patterns = lint_patterns()
    for (kind, name), path in entities.items():
        where = path.relative_to(ROOT)
        main = path / 'SKILL.md' if kind == 'skills' else path
        try:
            front, body = render.parse_frontmatter(main.read_text(), str(where))
        except (render.RenderError, OSError) as error:
            problems.append(str(error))
            continue
        allowed = {'skills': SKILL_FRONT_KEYS, 'agents': AGENT_FRONT_KEYS, 'rules': RULE_FRONT_KEYS}[kind]
        if set(front) - allowed:
            problems.append(f'{where}: unsupported frontmatter keys {sorted(set(front) - allowed)}; '
                            'tool-specific fields are generated by render.py')
        if front.get('name') != name or not render.NAME_RE.match(name) or len(name) > 64:
            problems.append(f'{where}: name must be kebab-case, at most 64 characters, and match the path')
        description = front.get('description', '')
        if not isinstance(description, str) or not 20 <= len(description) <= 1024:
            problems.append(f'{where}: description must be 20-1024 characters')
        meta = front.get('metadata', {})
        if not isinstance(meta, dict) or set(meta) - METADATA_KEYS:
            problems.append(f'{where}: unknown metadata keys {sorted(set(meta) - METADATA_KEYS)}')
        if meta.get('routing-tier') not in (None, *render.TIERS):
            problems.append(f'{where}: routing-tier must be one of {render.TIERS}')
        if kind in ('skills', 'agents') and not meta.get('routing-tier'):
            problems.append(f'{where}: routing-tier is required so orchestrators can pick a cost tier')
        if meta.get('routing-effort') not in (None, *render.EFFORTS):
            problems.append(f'{where}: routing-effort must be one of {render.EFFORTS}')
        if meta.get('invocation') not in (None, 'auto', 'explicit'):
            problems.append(f'{where}: invocation must be auto or explicit')
        if 'skills' in meta:
            skills = meta['skills']
            if kind != 'agents':
                problems.append(f'{where}: metadata.skills is only supported on agents')
            elif not isinstance(skills, list) or not all(isinstance(s, str) for s in skills):
                problems.append(f'{where}: metadata.skills must be a list of skill names')
            else:
                for skill in skills:
                    if ('skills', skill) not in entities:
                        problems.append(f'{where}: metadata.skills names unknown skill {skill!r}')
        if kind == 'skills':
            if body.count('\n') > 500:
                problems.append(f'{where}: SKILL.md body exceeds 500 lines; move detail into references/')
            for target in LINK_RE.findall(body):
                if re.match(r'[a-z]+:', target):
                    continue
                resolved = (path / target).resolve()
                if not resolved.is_relative_to(path.resolve()) or not resolved.exists():
                    problems.append(f'{where}: link {target!r} must resolve inside the skill directory')
            problems.extend(validate_evals(path, name))
        files = [path] if path.is_file() else [p for p in path.rglob('*')]
        for file in files:
            if file.is_symlink():
                problems.append(f'{file.relative_to(ROOT)}: symlinks are not allowed')
            elif file.is_file():
                text = file.read_text(errors='replace')
                for number, line in enumerate(text.splitlines(), start=1):
                    for pattern, reason in patterns:
                        if pattern.search(line):
                            problems.append(f'{file.relative_to(ROOT)}:{number}: {reason}: {line.strip()[:90]}')
    try:
        packs = load_packs()
        for name, pack in packs.items():
            resolve_packs([name], packs)
            for kind in KINDS:
                for entity in pack.get(kind, []):
                    if (kind, entity) not in entities:
                        problems.append(f'packs/{name}.json: unknown {kind} entity {entity!r}')
        for name in packs:
            members = {(k, e) for p in resolve_packs([name], packs) for k in KINDS for e in packs[p].get(k, [])}
            for kind, entity in sorted(members):
                if kind == 'agents' and (kind, entity) in entities:
                    for skill in agent_skills(entities[(kind, entity)]):
                        if ('skills', skill) not in members:
                            problems.append(f'packs/{name}.json: agent {entity!r} uses skill {skill!r}, '
                                            'which the pack does not include')
        referenced = {(k, e) for p in packs.values() for k in KINDS for e in p.get(k, [])}
        for key in sorted(set(entities) - referenced):
            problems.append(f'catalog/{key[0]}/{key[1]}: not referenced by any pack')
    except (BundleError, json.JSONDecodeError) as error:
        problems.append(str(error))
    tiers = json.loads(SUPPORT_FILES['routing.json'].read_text())
    for tier in render.TIERS:
        if tier not in tiers.get('tiers', {}):
            problems.append(f'routing/tiers.json: missing tier {tier!r}')
    return entities, problems


# --- Repository installation -------------------------------------------------------

def read_manifest(repo):
    path = repo / '.ai' / 'bundle.json'
    if not path.is_file():
        raise BundleError(f'{path} not found; create it with: aibundle.py init --repo {repo} --pack core')
    data = json.loads(path.read_text())
    unknown = set(data) - {'schema_version', 'packs', 'local', 'targets', 'routing', 'invocation', *KINDS}
    if unknown:
        raise BundleError(f'{path}: unknown keys {sorted(unknown)}')
    if data.get('schema_version', 2) != 2:
        raise BundleError(f'{path}: unsupported schema_version {data.get("schema_version")}')
    for key in ('packs', 'local', 'targets'):
        if not isinstance(data.get(key, []), list) or not all(isinstance(v, str) for v in data.get(key, [])):
            raise BundleError(f'{path}: "{key}" must be a list of strings')
    for kind in KINDS:
        spec = data.get(kind, {})
        if not isinstance(spec, dict) or set(spec) - {'add', 'remove'} or not all(
                isinstance(v, list) for v in spec.values()):
            raise BundleError(f'{path}: "{kind}" must be {{"add": [...], "remove": [...]}}')
    for key in ('routing', 'invocation'):
        if not isinstance(data.get(key, {}), dict):
            raise BundleError(f'{path}: "{key}" must be an object')
    return data


def read_lock(repo):
    path = repo / '.ai' / 'bundle-lock.json'
    if not path.is_file():
        return {'entities': {}}
    lock = json.loads(path.read_text())
    if lock.get('schema_version') != LOCK_VERSION:
        raise BundleError(f'{path}: unsupported lock schema {lock.get("schema_version")}')
    return lock


def catalog_revision():
    try:
        result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        if result.returncode == 0:
            dirty = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'],
                                   capture_output=True, text=True).stdout.strip()
            return result.stdout.strip() + ('+dirty' if dirty else '')
    except OSError:
        pass
    return 'unversioned'


def plan_install(repo):
    ai = repo / '.ai'
    manifest = read_manifest(repo)
    lock = read_lock(repo)
    entities = catalog_entities()
    pack_order, chosen = selection(manifest, load_packs(), entities)
    local = set(manifest.get('local', []))
    desired = {}
    for (kind, name), packs in sorted(chosen.items()):
        slot = f'{kind}/{name}'
        if slot in local:
            continue
        desired[slot] = {'source': entities[(kind, name)], 'packs': packs}
    for slot, source in SUPPORT_FILES.items():
        desired[slot] = {'source': source, 'packs': ['support']}

    actions, conflicts = [], []
    for slot, item in desired.items():
        target = ai / slot if slot in SUPPORT_FILES else entity_path(ai, *slot.split('/'))
        item['digest'] = digest(item['source'])
        locked = lock['entities'].get(slot, {}).get('sha256')
        if not target.exists() and not target.is_symlink():
            actions.append(('create', slot, target, item))
            continue
        current = digest(target)
        if current == item['digest']:
            actions.append(('keep', slot, target, item))
        elif locked is None:
            conflicts.append(f'{slot}: exists but is not managed by the catalog. Add it to "local" in '
                             'bundle.json to keep the repository version, or delete it to install the catalog version.')
        elif current != locked:
            conflicts.append(f'{slot}: modified locally since installation. Upstream the change to the catalog, '
                             'add the slot to "local" to keep the fork, or restore the locked version.')
        else:
            actions.append(('update', slot, target, item))
    for slot in sorted(set(lock['entities']) - set(desired)):
        target = ai / slot if slot in SUPPORT_FILES else entity_path(ai, *slot.split('/'))
        if slot in local:
            actions.append(('release', slot, target, None))
        elif not target.exists():
            actions.append(('forget', slot, target, None))
        elif digest(target) != lock['entities'][slot]['sha256']:
            conflicts.append(f'{slot}: deselected but modified locally. Add it to "local" to keep it, or delete it.')
        else:
            actions.append(('remove', slot, target, None))
    return manifest, pack_order, actions, conflicts


def apply_install(repo, actions, pack_order):
    for _, slot, _, _ in actions:
        render.contained(repo, f'.ai/{slot}' if slot in SUPPORT_FILES else
                         str(entity_path(Path('.ai'), *slot.split('/'))))
    for verb, slot, target, item in actions:
        if verb in ('update', 'remove'):
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        if verb in ('create', 'update'):
            target.parent.mkdir(parents=True, exist_ok=True)
            if item['source'].is_dir():
                shutil.copytree(item['source'], target)
            else:
                shutil.copy2(item['source'], target)
    lock = {
        'schema_version': LOCK_VERSION,
        'catalog': {'revision': catalog_revision()},
        'packs': pack_order,
        'entities': {slot: {'sha256': item['digest'], 'packs': item['packs']}
                     for verb, slot, _, item in sorted(actions, key=lambda a: a[1])
                     if verb in ('create', 'update', 'keep')},
    }
    path = repo / '.ai' / 'bundle-lock.json'
    temporary = path.with_name('.bundle-lock.json.tmp')
    temporary.write_text(json.dumps(lock, indent=2) + '\n')
    temporary.replace(path)  # atomic: a failed install never leaves a truncated lock


def legacy_warnings(repo):
    ai = repo / '.ai'
    notes = []
    if (ai / 'sync.sh').exists():
        notes.append('.ai/sync.sh is superseded by .ai/render.py; delete it after the first render is reviewed.')
    if (ai / 'meta').is_dir():
        notes.append('.ai/meta/ is not read by render.py; descriptions now live in frontmatter. '
                     'Move any repository-specific wording into .ai/overlays/ or a local entity, then delete it.')
    return notes


# --- Commands ------------------------------------------------------------------------

def cmd_list(_):
    packs = load_packs()
    print('Packs:')
    for name, pack in packs.items():
        counts = ', '.join(f'{len(pack.get(k, []))} {k}' for k in KINDS if pack.get(k))
        requires = f" (requires {', '.join(pack['requires'])})" if pack.get('requires') else ''
        print(f'  {name:24} {counts}{requires}\n  {"":24} {pack["description"]}')
    print('\nEntities:')
    for (kind, name), path in catalog_entities().items():
        main = path / 'SKILL.md' if kind == 'skills' else path
        front, _ = render.parse_frontmatter(main.read_text(), str(main))
        meta = front.get('metadata', {})
        print(f"  {kind[:-1]:6} {name:30} tier={meta.get('routing-tier', '-'):9} "
              f"effort={meta.get('routing-effort', '-'):7} invocation={meta.get('invocation', 'auto')}")
    return 0


def cmd_validate(_):
    entities, problems = validate_catalog()
    for problem in problems:
        print(f'  {problem}')
    if problems:
        print(f'{len(problems)} problem(s) in {len(entities)} entities')
        return 1
    print(f'Validated {len(entities)} entities, {len(load_packs())} packs, and routing tiers')
    return 0


def cmd_init(args):
    repo = Path(args.repo).resolve()
    path = repo / '.ai' / 'bundle.json'
    if path.exists():
        raise BundleError(f'{path} already exists; edit it instead')
    resolve_packs(args.pack, load_packs())
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 2, 'packs': args.pack, 'targets': render.DEFAULT_TARGETS,
                'skills': {'add': [], 'remove': []}, 'agents': {'add': [], 'remove': []},
                'rules': {'add': [], 'remove': []}, 'local': [], 'invocation': {},
                'routing': {'apply': {'skills': 'advisory', 'agents': 'enforce'}, 'models': {}, 'overrides': {}}}
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Wrote {path}. Review it, then run: aibundle.py install --repo {repo}')
    return 0


def cmd_install(args):
    repo = Path(args.repo).resolve()
    _, problems = validate_catalog()
    if problems:
        raise BundleError('catalog is invalid; run aibundle.py validate')
    _, pack_order, actions, conflicts = plan_install(repo)
    for verb, slot, _, _ in actions:
        if verb != 'keep' or args.verbose:
            print(f'  {verb:8} .ai/{slot}')
    if conflicts:
        print('Conflicts (nothing was written):', file=sys.stderr)
        for conflict in conflicts:
            print(f'  {conflict}', file=sys.stderr)
        return 1
    for note in legacy_warnings(repo):
        print(f'  note: {note}')
    if args.dry_run:
        print('Dry run: no files written')
        return 0
    apply_install(repo, actions, pack_order)
    changed = sum(1 for a in actions if a[0] != 'keep')
    print(f'Installed {sum(1 for a in actions if a[0] in ("create", "update", "keep"))} managed files '
          f'({changed} changed). Next: python3 {repo}/.ai/render.py')
    return 0


def cmd_status(args):
    repo = Path(args.repo).resolve()
    _, _, actions, conflicts = plan_install(repo)
    pending = [a for a in actions if a[0] != 'keep']
    for verb, slot, _, _ in pending:
        print(f'  pending {verb:8} .ai/{slot}')
    for conflict in conflicts:
        print(f'  conflict {conflict}')
    print('up to date' if not pending and not conflicts else
          f'{len(pending)} pending change(s), {len(conflicts)} conflict(s)')
    return 0 if not pending and not conflicts else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate the AI catalog and install it into repositories.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('validate')
    init = sub.add_parser('init')
    init.add_argument('--repo', required=True)
    init.add_argument('--pack', action='append', required=True)
    install = sub.add_parser('install')
    install.add_argument('--repo', required=True)
    install.add_argument('--dry-run', action='store_true')
    install.add_argument('--verbose', action='store_true')
    status = sub.add_parser('status')
    status.add_argument('--repo', required=True)
    args = parser.parse_args(argv)
    commands = {'list': cmd_list, 'validate': cmd_validate, 'init': cmd_init,
                'install': cmd_install, 'status': cmd_status}
    try:
        return commands[args.command](args)
    except (BundleError, render.RenderError, OSError, json.JSONDecodeError) as error:  # noqa: B014
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
