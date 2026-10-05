import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from pipe_venture_builder.model_policy import model_policy as policy


class RoutingTests(unittest.TestCase):
    def test_default_and_planning_are_builder_medium(self):
        for runtime, model in [('codex', 'gpt-6.1-sol'), ('claude', 'sonnet')]:
            for task in ('feature', 'plan', 'bug', 'refactor'):
                r = policy.select(runtime, task)
                self.assertEqual(r['recommended'], {'model': model, 'effort': 'medium'})

    def test_worker_is_bounded_and_low_risk(self):
        self.assertEqual(policy.select('codex', 'mechanical')['role'], 'worker')
        self.assertEqual(policy.select('claude', 'search')['recommended'], {'model': 'haiku', 'effort': None})
        self.assertEqual(policy.select('codex', 'mechanical', critical=True)['role'], 'builder')
        self.assertEqual(policy.select('codex', 'mechanical', ambiguous=True)['role'], 'architect')

    def test_two_distinct_hypotheses_escalate_and_resolution_returns(self):
        self.assertEqual(policy.select('codex', 'bug', failed_hypotheses=1)['role'], 'builder')
        self.assertEqual(policy.select('codex', 'bug', failed_hypotheses=2)['role'], 'architect')
        self.assertEqual(policy.select('codex', 'bug', failed_hypotheses=2, resolved=True)['role'], 'builder')
        self.assertEqual(policy.select('claude', 'architecture', architect_failures=2)['recommended']['effort'], 'high')

    def test_review_and_critical_effort(self):
        self.assertEqual(policy.select('codex', 'review')['recommended']['effort'], 'low')
        self.assertEqual(policy.select('codex', 'review', critical=True)['recommended']['effort'], 'medium')
        self.assertTrue(policy.select('claude', 'feature', critical=True)['review_required'])

    def test_human_exception_requires_reference_and_preserves_provider(self):
        with self.assertRaises(ValueError):
            policy.select('codex', explicit_model='gpt-5.5')
        with self.assertRaises(ValueError):
            policy.select('codex', explicit_model='claude-opus-4', authorization='human')
        r = policy.select('codex', explicit_model='gpt-5.5', explicit_effort='high', authorization='contract active')
        self.assertEqual(r['recommended']['model'], 'gpt-5.5')
        self.assertEqual(r['transition_status'], 'recommended_not_observed')


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        (self.home / '.codex').mkdir()
        (self.home / '.claude').mkdir()
        (self.home / '.codex/config.toml').write_text('model = "gpt-6-astra"\nmodel_reasoning_effort = "high"\n[projects."/work"]\ntrust_level = "trusted"\n')
        (self.home / '.claude/settings.json').write_text(json.dumps({'permissions': {'allow': ['Bash(test)']}, 'model': 'opus'}))
        (self.home / 'AGENTS.md').write_text('# Original\nDo not publish.\n')

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_writes_nothing(self):
        before = sorted(str(p.relative_to(self.home)) for p in self.home.rglob('*'))
        r = policy.install(self.home, dry_run=True)
        self.assertTrue(r['changed_paths'])
        self.assertEqual(before, sorted(str(p.relative_to(self.home)) for p in self.home.rglob('*')))

    def test_preserves_permissions_project_keys_instructions_and_backups(self):
        r = policy.install(self.home)
        codex = policy.tomllib.loads((self.home / '.codex/config.toml').read_text())
        self.assertEqual(codex['projects']['/work']['trust_level'], 'trusted')
        self.assertEqual(codex['model_reasoning_effort'], 'medium')
        self.assertEqual(policy.read_json(self.home / '.claude/settings.json')['permissions'], {'allow': ['Bash(test)']})
        self.assertIn('Do not publish.', (self.home / 'AGENTS.md').read_text())
        backups = policy.read_json(r['backup_manifest'])
        original = next(b for b in backups if b['path'] == str(self.home / 'AGENTS.md'))
        self.assertEqual(Path(original['backup']).read_text(), '# Original\nDo not publish.\n')
        self.assertEqual(Path(original['backup']).stat().st_mode & 0o777, 0o600)

    def test_reinstall_is_idempotent_and_does_not_duplicate(self):
        policy.install(self.home)
        receipt = (self.home / '.agents/model-policy/INSTALLATION.json').read_bytes()
        second = policy.install(self.home)
        self.assertEqual(second['changed_paths'], [])
        self.assertEqual((self.home / 'AGENTS.md').read_text().count(policy.BEGIN), 1)
        self.assertEqual((self.home / '.agents/model-policy/INSTALLATION.json').read_bytes(), receipt)

    def test_collision_preflights_before_any_changes(self):
        wrapper = self.home / '.local/bin/agent-model'
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text('unrelated')
        original = (self.home / '.codex/config.toml').read_bytes()
        with self.assertRaises(ValueError):
            policy.install(self.home)
        self.assertEqual((self.home / '.codex/config.toml').read_bytes(), original)
        self.assertFalse((self.home / '.agents/model-policy').exists())

    def test_drift_is_not_overwritten_even_with_approval(self):
        policy.install(self.home)
        matrix = self.home / '.agents/model-policy/matrix.json'
        matrix.write_text('{}')
        with self.assertRaises(ValueError):
            policy.install(self.home, replace_version=True, approval_reference='human')
        self.assertEqual(matrix.read_text(), '{}')

    def test_failed_receipt_finalization_rolls_back_files_and_receipt(self):
        original = (self.home / '.codex/config.toml').read_bytes()
        real_atomic = policy.atomic
        def fail_manifest(path, data, mode=0o600):
            if Path(path).name == 'changes.json':
                raise OSError('simulated failure after receipt write')
            return real_atomic(path, data, mode)
        with patch.object(policy, 'atomic', side_effect=fail_manifest):
            with self.assertRaises(OSError):
                policy.install(self.home)
        self.assertEqual((self.home / '.codex/config.toml').read_bytes(), original)
        self.assertFalse((self.home / '.agents/model-policy/INSTALLATION.json').exists())
        self.assertFalse((self.home / '.local/bin/agent-model').exists())

    def test_different_version_requires_real_approval_reference_record(self):
        policy.install(self.home)
        source = self.home / 'source'
        source.mkdir()
        for name in ('matrix.json', 'model_policy.py'):
            (source / name).write_bytes((policy.ROOT / name).read_bytes())
        for name in ('POLICY.md', 'ONBOARDING.md'):
            (source / name).write_bytes((self.home / '.agents/model-policy' / name).read_bytes())
        (source / 'POLICY.md').write_text((source / 'POLICY.md').read_text() + '\nProposed new policy.\n')
        with patch.object(policy, 'ROOT', source):
            with self.assertRaises(ValueError):
                policy.install(self.home)
            r = policy.install(self.home, replace_version=True, approval_reference='explicit user decision test fixture')
        self.assertIn(str(self.home / '.agents/model-policy/POLICY.md'), r['changed_paths'])


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        self.project = self.home / 'work/project'
        self.project.mkdir(parents=True)
        policy.install(self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def observation(self, **values):
        o = {'runtime': 'codex', 'model': 'gpt-6.1-sol', 'effort': 'medium', 'source': '/status',
             'observed_at': policy.now(), 'session_id': 'session-test', 'project': str(self.project)}
        o.update(values)
        return o

    def test_project_override_and_no_observation_never_claims_success(self):
        cfg = self.project / '.codex/config.toml'
        cfg.parent.mkdir()
        cfg.write_text('model = "gpt-6-astra"\nmodel_reasoning_effort = "high"\n')
        config = policy.inspect('codex', self.project, self.home)
        result = policy.check(policy.select('codex'), config)
        self.assertEqual(result['configuration_status'], 'divergent')
        self.assertEqual(result['observation_status'], 'not_verified')
        self.assertIsNone(result['observed'])

    def test_matching_files_are_not_matching_runtime(self):
        result = policy.check(policy.select('codex'), policy.inspect('codex', self.project, self.home))
        self.assertEqual(result['configuration_status'], 'matches_files')
        self.assertEqual(result['observation_status'], 'not_verified')
        result = policy.check(policy.select('codex'), result['configuration'], self.observation())
        self.assertEqual(result['observation_status'], 'matches')

    def test_mismatching_or_wrong_session_evidence(self):
        cfg = policy.inspect('codex', self.project, self.home)
        self.assertEqual(policy.check(policy.select('codex'), cfg, self.observation(model='gpt-6-astra'))['observation_status'], 'mismatch')
        for changes in ({'runtime': 'claude'}, {'project': '/other'}, {'observed_at': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()}):
            with self.assertRaises(ValueError):
                policy.check(policy.select('codex'), cfg, self.observation(**changes))

    def test_claude_local_settings_and_alias_family(self):
        cfg = self.project / '.claude/settings.local.json'
        cfg.parent.mkdir()
        cfg.write_text('{"model":"opus", "effortLevel":"high"}')
        self.assertEqual(policy.inspect('claude', self.project, self.home)['configured']['model'], 'opus')
        cfg.unlink()
        config = policy.inspect('claude', self.project, self.home)
        o = self.observation(runtime='claude', model='claude-sonnet-4-6')
        self.assertEqual(policy.check(policy.select('claude'), config, o)['observation_status'], 'matches')

    def test_launch_missing_runtime_no_fallback(self):
        with patch.object(policy.shutil, 'which', return_value=None):
            with self.assertRaises(ValueError):
                policy.launch(policy.select('codex'), self.project, [])

    def test_launch_arguments_preserve_model_without_launching_in_test(self):
        with patch.object(policy.shutil, 'which', return_value='/usr/bin/codex'), patch.object(policy.os, 'chdir'), patch.object(policy.os, 'execv') as execute:
            policy.launch(policy.select('codex'), self.project, [])
        argv = execute.call_args.args[1]
        self.assertEqual(argv[argv.index('--model') + 1], 'gpt-6.1-sol')
        self.assertIn('model_reasoning_effort="medium"', argv)


class ReleaseTests(unittest.TestCase):
    def test_human_notice_dedup_reopen_and_no_adoption(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            policy.install(home)
            active = (home / '.agents/model-policy/matrix.json').read_bytes()
            for runtime, model in [('codex', 'gpt-test-new'), ('claude', 'claude-opus-test-new')]:
                first = policy.release(home, runtime, model, 'human notice test fixture')
                self.assertFalse(first['policy_changed'])
                self.assertEqual(first['evaluation']['status'], 'awaiting_evaluation')
                self.assertIn('Decisão humana', Path(first['evaluation']['report']).read_text())
                second = policy.release(home, runtime, model, 'same version')
                self.assertTrue(second['deduplicated'])
                reopened = policy.release(home, runtime, model, 'human notice', reopen='new evidence')
                self.assertNotEqual(first['evaluation']['report'], reopened['evaluation']['report'])
                self.assertTrue(Path(first['evaluation']['report']).exists())
            self.assertEqual((home / '.agents/model-policy/matrix.json').read_bytes(), active)

    def test_empty_notice_or_wrong_provider_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                policy.release(tmp, 'codex', 'gpt-test', '')
            with self.assertRaises(ValueError):
                policy.release(tmp, 'claude', 'gpt-test', 'human notice')


if __name__ == '__main__':
    unittest.main()
