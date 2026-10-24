"""Behavioural tests for the catalog installer (aibundle.py) and renderer (render.py)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import render  # noqa: E402


def run(*args, cwd=None):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)


class Workspace(unittest.TestCase):
    """Each test gets a private copy of the catalog and an empty repository."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.catalog = self.base / 'catalog-copy'
        for part in ('catalog', 'packs', 'routing', 'scripts'):
            shutil.copytree(ROOT / part, self.catalog / part, ignore=shutil.ignore_patterns('__pycache__'))
        self.repo = self.base / 'repo'
        (self.repo / '.ai').mkdir(parents=True)

    def bundle(self, *args):
        return run(self.catalog / 'scripts' / 'aibundle.py', *args)

    def write_manifest(self, **fields):
        manifest = {'schema_version': 2, 'packs': ['core']}
        manifest.update(fields)
        (self.repo / '.ai' / 'bundle.json').write_text(json.dumps(manifest))

    def install(self, expect=0):
        result = self.bundle('install', '--repo', self.repo)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return result

    def render(self, *flags, expect=0):
        result = run(self.repo / '.ai' / 'render.py', *flags)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return result

    def read(self, relative):
        return (self.repo / relative).read_text()


class CatalogValidation(Workspace):
    def test_shipped_catalog_is_valid(self):
        result = run(ROOT / 'scripts' / 'aibundle.py', 'validate')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_portability_lint_rejects_host_paths_and_model_ids(self):
        skill = self.catalog / 'catalog/skills/typescript/SKILL.md'
        skill.write_text(skill.read_text() + '\nSee /home/alice/notes and use gpt-5.4 here.\n')
        result = self.bundle('validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn('host-specific absolute path', result.stdout)
        self.assertIn('pinned vendor model ID', result.stdout)

    def test_tool_specific_frontmatter_is_rejected_in_canonical_skills(self):
        skill = self.catalog / 'catalog/skills/typescript/SKILL.md'
        skill.write_text(skill.read_text().replace('metadata:', 'model: opus\nmetadata:', 1))
        result = self.bundle('validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported frontmatter keys ['model']", result.stdout)

    def test_unreferenced_entity_and_broken_link_are_reported(self):
        orphan = self.catalog / 'catalog/skills/orphan-skill'
        orphan.mkdir()
        (orphan / 'SKILL.md').write_text('---\nname: orphan-skill\ndescription: A skill that no pack references at all.\n'
                                         'metadata:\n  routing-tier: fast\n---\nSee [missing](references/nope.md).\n')
        result = self.bundle('validate')
        self.assertIn('not referenced by any pack', result.stdout)
        self.assertIn("link 'references/nope.md'", result.stdout)

    def test_unknown_effort_is_rejected(self):
        agent = self.catalog / 'catalog/agents/scout.md'
        agent.write_text(agent.read_text().replace('routing-effort: low', 'routing-effort: turbo'))
        self.assertIn('routing-effort must be one of', self.bundle('validate').stdout)

    def test_agent_skill_dependencies_are_checked(self):
        packs = self.catalog / 'packs'
        data = json.loads((packs / 'review.json').read_text())
        data.pop('skills')
        (packs / 'review.json').write_text(json.dumps(data))
        (packs / 'security-extra.json').write_text(json.dumps({'description': 'x', 'skills': ['appsec-review']}))
        result = self.bundle('validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn("agent 'security-practices' uses skill 'appsec-review'", result.stdout)
        agent = self.catalog / 'catalog/agents/scout.md'
        agent.write_text(agent.read_text().replace('metadata:\n', 'metadata:\n  skills: [no-such-skill]\n', 1))
        self.assertIn("names unknown skill 'no-such-skill'", self.bundle('validate').stdout)

    def test_pack_cycles_are_rejected(self):
        packs = self.catalog / 'packs'
        data = json.loads((packs / 'typescript.json').read_text())
        data['requires'] = ['nestjs']
        (packs / 'typescript.json').write_text(json.dumps(data))
        result = self.bundle('validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn('pack cycle', result.stdout)


class Installation(Workspace):
    def test_install_creates_entities_support_files_and_lock(self):
        self.write_manifest(packs=['nestjs'])
        self.install()
        ai = self.repo / '.ai'
        for path in ('skills/nestjs/SKILL.md', 'skills/typescript/SKILL.md', 'skills/clean-architecture/SKILL.md',
                     'render.py', 'routing.json'):
            self.assertTrue((ai / path).is_file(), path)
        lock = json.loads((ai / 'bundle-lock.json').read_text())
        self.assertEqual(lock['packs'], ['typescript', 'architecture', 'nestjs'])
        self.assertIn('skills/nestjs', lock['entities'])

    def test_reinstall_without_changes_is_a_no_op(self):
        self.write_manifest()
        self.install()
        result = self.install()
        self.assertIn('(0 changed)', result.stdout)

    def test_local_edit_blocks_install_and_writes_nothing(self):
        self.write_manifest()
        self.install()
        skill = self.repo / '.ai/skills/plan-execution/SKILL.md'
        skill.write_text(skill.read_text() + '\nlocal tweak\n')
        self.write_manifest(packs=['core', 'review'])
        result = self.install(expect=1)
        self.assertIn('modified locally', result.stderr)
        self.assertFalse((self.repo / '.ai/agents/security-practices.md').exists())

    def test_unmanaged_existing_entity_is_a_conflict_until_declared_local(self):
        own = self.repo / '.ai/skills/model-routing'
        own.mkdir(parents=True)
        (own / 'SKILL.md').write_text('---\nname: model-routing\ndescription: Our own routing policy.\n---\nbody\n')
        self.write_manifest()
        self.assertIn('not managed by the catalog', self.install(expect=1).stderr)
        self.write_manifest(local=['skills/model-routing'])
        self.install()
        self.assertIn('Our own routing policy', (own / 'SKILL.md').read_text())
        lock = json.loads((self.repo / '.ai/bundle-lock.json').read_text())
        self.assertNotIn('skills/model-routing', lock['entities'])

    def test_catalog_update_replaces_unmodified_entity(self):
        self.write_manifest()
        self.install()
        source = self.catalog / 'catalog/skills/plan-validation/SKILL.md'
        source.write_text(source.read_text() + '\nUpstream improvement.\n')
        result = self.install()
        self.assertIn('update   .ai/skills/plan-validation', result.stdout)
        self.assertIn('Upstream improvement.', self.read('.ai/skills/plan-validation/SKILL.md'))

    def test_deselected_entity_is_removed_only_when_unmodified(self):
        self.write_manifest(packs=['core', 'review'])
        self.install()
        agent = self.repo / '.ai/agents/security-practices.md'
        agent.write_text(agent.read_text() + '\nextra\n')
        self.write_manifest(packs=['core'])
        self.assertIn('deselected but modified', self.install(expect=1).stderr)
        self.write_manifest(packs=['core'], local=['agents/security-practices'])
        self.install()
        self.assertTrue(agent.exists())
        self.assertFalse((self.repo / '.ai/agents/performance-scalability.md').exists())

    def test_remove_of_unselected_entity_is_an_error(self):
        self.write_manifest(skills={'remove': ['nestjs']})
        self.assertIn('unselected entity', self.install(expect=1).stderr)

    def test_malformed_manifest_is_rejected_before_any_write(self):
        for manifest in ({'packs': 'core'}, {'packs': ['core'], 'skills': ['x']}, {'packs': ['core'], 'schema_version': 3}):
            (self.repo / '.ai' / 'bundle.json').write_text(json.dumps(manifest))
            self.install(expect=1)
            self.assertFalse((self.repo / '.ai/render.py').exists(), manifest)

    def test_status_reports_pending_changes(self):
        self.write_manifest()
        result = self.bundle('status', '--repo', self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn('pending create', result.stdout)
        self.install()
        self.assertEqual(self.bundle('status', '--repo', self.repo).returncode, 0)


class Rendering(Workspace):
    def setUp(self):
        super().setUp()
        self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'])
        self.install()

    def test_renders_every_target_and_is_idempotent(self):
        self.render()
        for path in ('AGENTS.md', '.claude/CLAUDE.md', 'GEMINI.md',
                     '.claude/skills/plan-execution/SKILL.md', '.agents/skills/plan-execution/SKILL.md',
                     '.agents/skills/plan-execution/agents/openai.yaml',
                     '.claude/agents/scout.md', '.codex/agents/scout.toml', '.cursor/agents/scout.md',
                     '.gemini/agents/scout.md', '.cursor/rules/teaching-mode.mdc', '.claude/rules/teaching-mode.md'):
            self.assertTrue((self.repo / path).exists(), path)
        self.assertFalse((self.repo / '.codex/skills').exists(), 'Codex reads .agents/skills')
        self.assertIn('outputs are current', self.render('--check').stdout)

    def test_gemini_imports_the_shared_index_from_a_loaded_location(self):
        self.render()
        self.assertIn('@./AGENTS.md', self.read('GEMINI.md'))
        self.assertFalse((self.repo / '.gemini/GEMINI.md').exists())

    def test_index_stays_compact(self):
        self.render()
        index = self.read('AGENTS.md')
        long_description = render.parse_frontmatter(
            self.read('.ai/skills/plan-execution/SKILL.md'), 'x')[0]['description']
        self.assertNotIn(long_description, index)
        self.assertTrue(all(len(line) < 400 for line in index.splitlines()), 'one short line per entity')

    def test_codex_display_names_keep_acronyms(self):
        self.render()
        self.assertIn('"Programming KB"', self.read('.agents/skills/programming-kb/agents/openai.yaml'))

    def test_check_detects_stale_outputs(self):
        self.render()
        source = self.repo / '.ai/agents/scout.md'
        source.write_text(source.read_text() + '\nNew instruction.\n')
        self.assertIn('stale  .claude/agents/scout.md', self.render('--check', expect=1).stdout)

    def test_agent_tiers_map_to_tool_models_and_efforts(self):
        self.render()
        claude = self.read('.claude/agents/security-practices.md')
        self.assertIn('model: opus', claude)
        self.assertIn('effort: high', claude)
        self.assertIn('tools: "Read, Grep, Glob, Bash"', claude, 'needs git to resolve a change range')
        self.assertIn('tools: "Read, Grep, Glob"\n', self.read('.claude/agents/system-design-scalability.md'))
        self.assertIn('model: haiku', self.read('.claude/agents/scout.md'))
        codex = self.read('.codex/agents/scout.toml')
        self.assertNotIn('model =', codex, 'unmapped tiers inherit the session model')
        self.assertIn('model_reasoning_effort = "low"', codex)
        self.assertIn('readonly: true', self.read('.cursor/agents/scout.md'))
        self.assertIn('run_shell_command', self.read('.gemini/agents/check-runner.md'))

    def test_repository_overrides_models_and_entity_tiers(self):
        self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'], routing={
            'models': {'codex': {'deep': 'example-codex-large'}, 'claude': {'fast': 'sonnet'}},
            'overrides': {'readability-maintainability': {'tier': 'deep', 'effort': 'low'}}})
        self.render()
        self.assertIn('model = "example-codex-large"', self.read('.codex/agents/security-practices.toml'))
        self.assertIn('model: sonnet', self.read('.claude/agents/scout.md'))
        readability = self.read('.claude/agents/readability-maintainability.md')
        self.assertIn('model: opus', readability)
        self.assertIn('effort: low', readability)

    def test_routing_and_invocation_typos_fail_loudly(self):
        for manifest in ({'routing': {'overrides': {'scoutt': {'tier': 'deep'}}}},
                         {'routing': {'overrides': {'scout': {'effort': 'extreme'}}}},
                         {'invocation': {'programming-kbb': 'auto'}}):
            self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'], **manifest)
            self.assertIn('bundle.json', self.render(expect=1).stderr, manifest)

    def test_tier_table_lists_only_enabled_tools(self):
        self.write_manifest(packs=['core'], targets=['claude', 'agents-md'])
        self.install()
        self.render()
        table = [line for line in self.read('AGENTS.md').splitlines() if line.startswith('| Tier')]
        self.assertEqual(table, ['| Tier | Use for | claude |'])

    def test_skills_are_advisory_unless_enforced_or_forked(self):
        self.render()
        front, _ = render.parse_frontmatter(self.read('.claude/skills/principal-engineer-planner/SKILL.md'), 'x')
        self.assertNotIn('effort', front)
        self.assertNotIn('model', front)
        self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'],
                            routing={'apply': {'skills': 'enforce'}})
        skill = self.repo / '.ai/skills/codebase-research/SKILL.md'
        skill.write_text(skill.read_text().replace('metadata:\n', 'metadata:\n  context: fork\n  agent: Explore\n', 1))
        self.render()
        planner, _ = render.parse_frontmatter(self.read('.claude/skills/principal-engineer-planner/SKILL.md'), 'x')
        self.assertEqual(planner['effort'], 'high')
        self.assertNotIn('model', planner, 'inline skills never change the session model')
        forked, _ = render.parse_frontmatter(self.read('.claude/skills/codebase-research/SKILL.md'), 'x')
        self.assertEqual((forked['context'], forked['agent'], forked['model']), ('fork', 'Explore', 'sonnet'))

    def test_explicit_invocation_is_rendered_for_every_tool(self):
        self.render()
        claude, body = render.parse_frontmatter(self.read('.claude/skills/programming-kb/SKILL.md'), 'x')
        self.assertTrue(claude['disable-model-invocation'])
        self.assertIn('Explicit only', body)
        self.assertIn('allow_implicit_invocation: false', self.read('.agents/skills/programming-kb/agents/openai.yaml'))
        self.assertIn('allow_implicit_invocation: true', self.read('.agents/skills/plan-execution/agents/openai.yaml'))
        self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'], invocation={'programming-kb': 'auto'})
        self.render()
        claude, _ = render.parse_frontmatter(self.read('.claude/skills/programming-kb/SKILL.md'), 'x')
        self.assertNotIn('disable-model-invocation', claude)

    def test_agent_skills_are_preloaded_in_claude_and_read_first_elsewhere(self):
        self.render()
        claude, body = render.parse_frontmatter(self.read('.claude/agents/security-practices.md'), 'x')
        self.assertEqual(claude['skills'], ['appsec-review'])
        self.assertNotIn('Before starting, read', body)
        note = '`.agents/skills/appsec-review/SKILL.md`'
        for path in ('.codex/agents/security-practices.toml', '.cursor/agents/security-practices.md',
                     '.gemini/agents/security-practices.md'):
            self.assertIn(note, self.read(path), path)
        self.assertNotIn('skills', render.parse_frontmatter(self.read('.claude/agents/scout.md'), 'x')[0])

    def test_explicit_only_agent_skill_is_read_instead_of_preloaded(self):
        self.write_manifest(packs=['core', 'review', 'knowledge-base', 'teaching'],
                            invocation={'appsec-review': 'explicit'})
        self.render()
        claude, body = render.parse_frontmatter(self.read('.claude/agents/security-practices.md'), 'x')
        self.assertNotIn('skills', claude, 'Claude cannot preload disable-model-invocation skills')
        self.assertIn('`.claude/skills/appsec-review/SKILL.md`', body)

    def test_install_refuses_agent_without_its_skill(self):
        self.write_manifest(packs=['core', 'review'], skills={'remove': ['appsec-review']})
        result = self.install(expect=1)
        self.assertIn("uses skill 'appsec-review'", result.stdout + result.stderr)

    def test_overlay_is_referenced_and_unknown_overlays_fail(self):
        overlays = self.repo / '.ai/overlays'
        overlays.mkdir()
        (overlays / 'plan-execution.md').write_text('Use make check.\n')
        self.render()
        self.assertIn('.ai/overlays/plan-execution.md', self.read('.claude/skills/plan-execution/SKILL.md'))
        self.assertIn('Overlay: `.ai/overlays/plan-execution.md`', self.read('AGENTS.md'))
        (overlays / 'no-such-skill.md').write_text('x')
        self.assertIn('unknown skill', self.render(expect=1).stderr)

    def test_removed_entity_outputs_are_cleaned_up(self):
        self.render()
        self.write_manifest(packs=['core', 'knowledge-base', 'teaching'])
        self.install()
        self.render()
        for path in ('.claude/agents/security-practices.md', '.codex/agents/security-practices.toml'):
            self.assertFalse((self.repo / path).exists(), path)

    def test_refuses_to_overwrite_hand_written_files(self):
        target = self.repo / '.claude/agents/scout.md'
        target.parent.mkdir(parents=True)
        target.write_text('my own agent\n')
        self.assertIn('not created by the renderer', self.render(expect=1).stderr)
        self.assertEqual(target.read_text(), 'my own agent\n')

    def test_symlinked_tool_directory_is_never_written_through(self):
        outside = self.base / 'user-config'
        outside.mkdir()
        (outside / 'settings.json').write_text('{}')
        (self.repo / '.claude').symlink_to(outside, target_is_directory=True)
        self.assertIn('symlink', self.render(expect=1).stderr)
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ['settings.json'])
        self.assertFalse((self.repo / '.cursor').exists(), 'nothing is written when any target is unsafe')

    def test_install_refuses_symlinked_ai_subdirectory(self):
        self.write_manifest(packs=['core', 'review'])
        outside = self.base / 'elsewhere'
        outside.mkdir()
        shutil.rmtree(self.repo / '.ai/agents')
        (self.repo / '.ai/agents').symlink_to(outside, target_is_directory=True)
        self.assertIn('symlink', self.install(expect=1).stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_unsafe_manifest_paths_are_refused(self):
        (self.repo / '.ai' / render.MANIFEST).write_text('../outside\n')
        self.assertIn('unsafe managed path', self.render(expect=1).stderr)

    def test_legacy_sync_outputs_listed_in_manifest_are_removed(self):
        legacy = self.repo / '.codex/skills/old-skill'
        legacy.mkdir(parents=True)
        (legacy / 'SKILL.md').write_text('old')
        (self.repo / '.gemini').mkdir()
        (self.repo / '.gemini/GEMINI.md').write_text('old index')
        (self.repo / '.ai' / render.MANIFEST).write_text(
            '.codex/skills/old-skill\n.codex/AGENTS.md\n.gemini/GEMINI.md\n')
        self.render()
        self.assertFalse(legacy.exists())
        self.assertFalse((self.repo / '.codex/skills').exists(), 'empty legacy directories are pruned')
        self.assertFalse((self.repo / '.gemini/GEMINI.md').exists())

    def test_removed_roo_target_fails_and_old_outputs_are_cleaned(self):
        self.write_manifest(packs=['core'], targets=['claude', 'roo'])
        self.assertIn('Roo support was removed', self.render(expect=1).stderr)
        old = self.repo / '.roo/skills/plan-execution'
        old.mkdir(parents=True)
        (old / 'SKILL.md').write_text('old')
        (self.repo / '.ai' / render.MANIFEST).write_text('.roo/skills/plan-execution\n')
        self.write_manifest(packs=['core'], targets=['claude'])
        self.render()
        self.assertFalse((self.repo / '.roo').exists())

    def test_targets_limit_outputs(self):
        self.write_manifest(packs=['core'], targets=['claude'])
        self.install()
        self.render()
        self.assertTrue((self.repo / '.claude/CLAUDE.md').exists())
        for path in ('AGENTS.md', '.agents', '.codex', '.cursor', '.gemini'):
            self.assertFalse((self.repo / path).exists(), path)

    def test_executable_bits_survive_install_and_render(self):
        self.render()
        for base in ('.ai/skills', '.claude/skills', '.agents/skills'):
            script = self.repo / base / 'programming-kb/scripts/kb-query.sh'
            self.assertTrue(os.access(script, os.X_OK), script)


class Frontmatter(unittest.TestCase):
    def test_round_trip_quotes_risky_scalars(self):
        data = {'name': 'x', 'description': 'Uses: colons, #hashes and "quotes"', 'flag': True,
                'items': ['a', 'b c'], 'metadata': {'routing-tier': 'fast'}}
        parsed, body = render.parse_frontmatter(render.dump_frontmatter(data) + 'body\n', 't')
        self.assertEqual(parsed, data)
        self.assertEqual(body, 'body\n')

    def test_unsupported_yaml_is_rejected(self):
        for text in ('---\ndescription: |\n  block\n---\n', '---\nkey: {a: 1}\n---\n', '---\n  orphan: x\n---\n'):
            with self.assertRaises(render.RenderError, msg=text):
                render.parse_frontmatter(text, 't')


if __name__ == '__main__':
    unittest.main()
