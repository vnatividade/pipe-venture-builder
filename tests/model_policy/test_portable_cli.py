"""Cross-machine policy install boundaries; no runtime inference or user-home writes."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import subprocess
import sys

from pipe_venture_builder.cli import main
from pipe_venture_builder.model_policy import model_policy as engine


class PortableModelPolicyTests(TestCase):
    def run_pipe(self, *args):
        out, err = StringIO(), StringIO()
        code = main(['model-policy', '--json', *args], stdout=out, stderr=err)
        return code, json.loads(out.getvalue() or err.getvalue())

    def test_new_home_plan_apply_and_relocated_installed_wrapper(self):
        with TemporaryDirectory(prefix='pipe imported machine ') as tmp:
            home = Path(tmp).resolve() / 'new user home'
            code, plan = self.run_pipe('--home', str(home), 'install')
            self.assertEqual(code, 0)
            self.assertTrue(plan['result']['dry_run'])
            self.assertFalse(home.exists())
            code, applied = self.run_pipe('--home', str(home), 'install', '--apply')
            self.assertEqual(code, 0)
            self.assertFalse(applied['result']['sessions_modified'])
            rerun = self.run_pipe('--home', str(home), 'install', '--apply')[1]['result']
            self.assertEqual(rerun['changed_paths'], [])
            project = home / 'imported project'
            project.mkdir()
            # Wrapper references destination/interpreter, never the toolkit/source checkout.
            wrapper = home / '.local/bin/agent-model'
            self.assertNotIn(str(engine.ROOT), wrapper.read_text())
            result = subprocess.run([str(wrapper), '--json', '--home', str(home),
                                     'check', '--runtime', 'codex', '--project', str(project)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)  # No observation, never certified.
            report = json.loads(result.stdout)
            self.assertEqual(report['configuration_status'], 'matches_files')
            self.assertEqual(report['observation_status'], 'not_verified')
            for runtime, model in [('codex', 'gpt-6.1-sol'), ('claude', 'sonnet')]:
                code, report = self.run_pipe('--home', str(home), 'inspect', '--runtime', runtime,
                                             '--project', str(project))
                self.assertEqual(code, 0)
                self.assertEqual(report['result']['configured']['model'], model)
                self.assertEqual(report['result']['configured']['effort'], 'medium')

    def test_json_and_home_after_subcommand_and_text_mode(self):
        with TemporaryDirectory() as tmp:
            out, err = StringIO(), StringIO()
            code = main(['model-policy', 'install', '--json', '--home', str(Path(tmp)/'absent')],
                        stdout=out, stderr=err)
            self.assertEqual(code, 0)
            self.assertTrue(json.loads(out.getvalue())['result']['dry_run'])
        out = StringIO()
        code = main(['model-policy', 'select', '--runtime', 'claude'], stdout=out)
        self.assertEqual(code, 0)
        self.assertIn('sonnet', out.getvalue())

    def test_standalone_installed_helper_also_defaults_to_plan(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            engine.install(home)
            other = home / 'untouched home'
            result = subprocess.run([str(home/'.local/bin/agent-model'), '--json', 'install',
                                     '--home', str(other)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stdout)['dry_run'])
            self.assertFalse(other.exists())

    def test_parent_symlink_preserves_foreign_configs_before_any_write(self):
        with TemporaryDirectory() as tmp:
            home, foreign = Path(tmp)/'home', Path(tmp)/'foreign'
            home.mkdir(); foreign.mkdir()
            original = b'model="gpt-6-astra"\n'
            (foreign/'config.toml').write_bytes(original)
            (home/'.codex').symlink_to(foreign, target_is_directory=True)
            for apply in [False, True]:
                with self.assertRaises(ValueError):
                    engine.install(home, dry_run=not apply)
            self.assertEqual((foreign/'config.toml').read_bytes(), original)
            self.assertEqual(sorted(p.name for p in home.iterdir()), ['.codex'])

    def test_custom_runtime_home_blocks_standard_install_without_disclosure(self):
        for name in ['CODEX_HOME', 'CLAUDE_CONFIG_DIR']:
            with TemporaryDirectory() as tmp, patch.dict(os.environ, {name:'/custom/local-config'}):
                home=Path(tmp)/'absent'
                code, error=self.run_pipe('--home',str(home),'install','--apply')
                self.assertEqual(code,2)
                self.assertEqual(error['code'],'MODEL_POLICY_BLOCKED')
                self.assertNotIn('/custom/local-config', json.dumps(error))
                self.assertFalse(home.exists())

    def test_windows_install_and_release_fail_explicitly_without_writes(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/'absent'
            with patch.object(engine.os, 'name', 'nt'):
                with self.assertRaisesRegex(ValueError,'Windows'):
                    engine.install(home)
            with patch.object(engine,'fcntl',None):
                with self.assertRaisesRegex(ValueError,'macOS/Linux'):
                    engine.release(home,'codex','gpt-test','human notice')
            self.assertFalse(home.exists())
            self.assertEqual(engine.select('codex')['recommended']['effort'],'medium')

    def test_malformed_destination_error_does_not_echo_contents(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp);(home/'.claude').mkdir()
            (home/'.claude/settings.json').write_text('{ sensitive-fixture-value')
            code,error=self.run_pipe('--home',str(home),'install','--apply')
            self.assertEqual(code,2)
            self.assertNotIn('sensitive-fixture-value',json.dumps(error))
            self.assertFalse((home/'.agents/model-policy').exists())

    def test_project_override_is_reported_and_preserved(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp).resolve();engine.install(home)
            project=home/'project';(project/'.codex').mkdir(parents=True)
            cfg=project/'.codex/config.toml';original=b'model="gpt-6-astra"\nmodel_reasoning_effort="high"\n'
            cfg.write_bytes(original)
            code,result=self.run_pipe('--home',str(home),'check','--runtime','codex','--project',str(project))
            self.assertEqual(code,1)
            self.assertEqual(result['result']['configuration_status'],'divergent')
            self.assertEqual(cfg.read_bytes(),original)
            self.assertFalse((project/'.pipe/mode.json').exists())

    def test_manual_release_cli_deduplicates_and_cannot_adopt(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp).resolve();engine.install(home)
            before=(home/'.agents/model-policy/matrix.json').read_bytes()
            command=['--home',str(home),'release','--runtime','claude','--model','claude-opus-new',
                     '--notice','user says release is available']
            code,r=self.run_pipe(*command)
            self.assertEqual(code,0)
            self.assertFalse(r['result']['policy_changed'])
            self.assertEqual(r['result']['evaluation']['status'],'awaiting_evaluation')
            self.assertTrue(self.run_pipe(*command)[1]['result']['deduplicated'])
            self.assertEqual(before,(home/'.agents/model-policy/matrix.json').read_bytes())
