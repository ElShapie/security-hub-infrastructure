import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('maestro_vm', ROOT / 'scripts/maestro_vm.py')
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)


class MaestroTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.target = Path(self.temp.name) / 'runtime'

    def tearDown(self):
        self.temp.cleanup()

    def test_separate_role_and_unique_secrets(self):
        dest = vm.prepare('hub', self.target)
        values = vm.env_values(dest)
        self.assertEqual(len({values[k] for k in ('APP_SECRET', 'SCIM_TOKEN', 'DEVICE_TOKEN', 'CARD_PEPPER')}), 4)
        self.assertFalse((self.target / 'nvr').exists())
        self.assertEqual(values['NVR_BASE_URL'], '')

    def test_existing_runtime_is_not_overwritten(self):
        dest = vm.prepare('hub', self.target)
        (dest / '.env').write_text('KEEP=private-fixture')
        (dest / 'compose.yml').write_text('KEEP CONFIG')
        vm.prepare('hub', self.target)
        self.assertEqual((dest / '.env').read_text(), 'KEEP=private-fixture')
        self.assertEqual((dest / 'compose.yml').read_text(), 'KEEP CONFIG')

    def test_unknown_existing_runtime_rejected(self):
        (self.target / 'hub').mkdir(parents=True)
        with self.assertRaises(ValueError):
            vm.prepare('hub', self.target)

    def test_unsafe_paths_rejected(self):
        for path in (ROOT, ROOT / 'runtime', Path.home(), ROOT.parent, Path(ROOT.anchor)):
            with self.assertRaises(ValueError):
                vm.runtime_path(path)

    def test_nvr_missing_fields_no_commands(self):
        dest = vm.prepare('nvr', self.target)
        with patch.object(vm, 'run') as run:
            with self.assertRaises(ValueError):
                vm.validate('nvr', dest)
            run.assert_not_called()

    def test_nvr_wrong_ip_rejected_before_docker(self):
        dest = vm.prepare('nvr', self.target)
        (dest / '.env').write_text('NVR_BIND_IP=10.31.0.21\n' + '\n'.join(k + '=fixture' for k in ('FRIGATE_CAM_ANDROID_USER', 'FRIGATE_CAM_ANDROID_PASSWORD', 'FRIGATE_CAM_IPHONE_USER', 'FRIGATE_CAM_IPHONE_PASSWORD')))
        (dest / '.env').chmod(0o600)
        with patch.object(vm, 'run', return_value=json.dumps([{'addr_info': [{'local': '10.31.0.20'}]}])) as run:
            with self.assertRaises(ValueError):
                vm.validate('nvr', dest)
            self.assertEqual(run.call_count, 1)

    def test_backup_directories(self):
        dest = vm.prepare('respaldo', self.target)
        self.assertTrue((dest / 'entradas').is_dir())
        self.assertFalse((dest / '.env').exists())
        with patch.object(vm.shutil, 'which', return_value='/fixture/tool'):
            vm.validate('respaldo', dest)

    def test_failed_command_does_not_echo_private_output(self):
        from subprocess import CompletedProcess
        with patch.object(vm.subprocess, 'run', return_value=CompletedProcess(['docker'], 1, 'private-fixture', 'private-fixture')):
            with self.assertRaises(ValueError) as error:
                vm.run(['docker', 'info'], capture=True)
            self.assertNotIn('private-fixture', str(error.exception))

    def test_install_only_selected_packages(self):
        with patch.object(vm.Path, 'read_text', return_value='ID=ubuntu\nVERSION_ID="24.04"\n'), patch.object(vm.os, 'geteuid', return_value=1000, create=True), patch.object(vm, 'run') as run:
            vm.install('respaldo')
            calls = [call.args[0] for call in run.call_args_list]
            self.assertEqual(len(calls), 2)
            self.assertNotIn('docker.io', calls[1])
            self.assertIn('age', calls[1])

    def test_valid_hub_uses_quiet_compose(self):
        dest = vm.prepare('hub', self.target)
        text = (dest / '.env').read_text().replace('REEMPLAZAR_CLIENT_ID', 'fixture-id').replace('REEMPLAZAR_CLIENT_SECRET', 'fixture-secret').replace('REEMPLAZAR.onelogin.com', 'fixture.onelogin.com')
        (dest / '.env').write_text(text)
        (dest / '.env').chmod(0o600)
        with patch.object(vm.shutil, 'which', return_value='/fixture/docker'), patch.object(vm, 'run') as run:
            vm.validate('hub', dest)
            self.assertEqual(run.call_count, 3)
            self.assertEqual(run.call_args.args[0][-2:], ['config', '--quiet'])

    def test_unsupported_install_does_not_run_commands(self):
        with patch.object(vm.Path, 'read_text', return_value='ID=debian\nVERSION_ID="12"\n'), patch.object(vm, 'run') as run:
            with self.assertRaises(ValueError):
                vm.install('hub')
            run.assert_not_called()

    def test_wrappers_and_no_destructive_commands(self):
        for role in ('hub', 'nvr', 'respaldo'):
            raw = (ROOT / f'scripts/vm-{role}.sh').read_bytes()
            self.assertNotIn(b'\r', raw)
            self.assertIn(f'exec python3 scripts/maestro_vm.py {role}'.encode(), raw)
        source = (ROOT / 'scripts/maestro_vm.py').read_text(encoding='utf-8')
        for forbidden in ('down', 'prune', 'rmtree', 'shell=True'):
            self.assertNotIn(forbidden, source)


if __name__ == '__main__':
    unittest.main()
