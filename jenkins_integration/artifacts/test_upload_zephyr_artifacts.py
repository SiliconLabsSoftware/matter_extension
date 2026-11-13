from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, call, patch

import yaml

with patch.dict(os.environ, {'GITHUB_ACCESS_TOKEN': 'test-token'}):
    from jenkins_integration.artifacts import upload_zephyr_artifacts as uploader


class TestDownloadZephyrArtifact(unittest.TestCase):
    def setUp(self):
        self.api_request = self.enterContext(
            patch.object(uploader, '_make_github_api_request'))
        self.download = self.enterContext(
            patch.object(uploader, '_download_and_extract', return_value='./extracted'))
        self.sleep = self.enterContext(patch.object(uploader.time, 'sleep'))
        self.workflow_id = 12345
        self.run_url = f'{uploader.config.actions_runs_base_url}/{self.workflow_id}'
        self.artifacts_url = f'{self.run_url}/artifacts?per_page=100&page=1'
        self.run = {
            'path': uploader.WORKFLOW_PATH,
            'status': 'completed',
            'conclusion': 'failure',
        }
        self.artifact = {
            'name': uploader.ARTIFACT_NAME,
            'archive_download_url': 'https://example.com/artifact.zip',
        }

    def test_downloads_available_artifact_regardless_of_workflow_result(self):
        for status, conclusion in (
            ('completed', 'success'),
            ('completed', 'failure'),
            ('completed', 'cancelled'),
            ('completed', 'timed_out'),
            ('in_progress', None),
        ):
            with self.subTest(status=status, conclusion=conclusion):
                self.run.update(status=status, conclusion=conclusion)
                self.api_request.reset_mock()
                self.api_request.side_effect = [
                    Mock(json=Mock(return_value=self.run)),
                    Mock(json=Mock(return_value={'artifacts': [self.artifact]})),
                ]

                result = uploader._download_zephyr_artifact(self.workflow_id)

                self.assertEqual(result, './extracted')
                self.assertEqual(self.api_request.call_args_list, [
                    call(self.run_url), call(self.artifacts_url)])
                self.download.assert_called_with(
                    self.artifact['archive_download_url'], uploader.ARTIFACT_NAME + '.zip')
                self.sleep.assert_not_called()

    def test_retries_missing_artifact_even_when_workflow_failed(self):
        self.api_request.side_effect = [
            Mock(json=Mock(return_value=self.run)),
            Mock(json=Mock(return_value={'artifacts': []})),
            Mock(json=Mock(return_value=self.run)),
            Mock(json=Mock(return_value={'artifacts': [self.artifact]})),
        ]

        result = uploader._download_zephyr_artifact(self.workflow_id)

        self.assertEqual(result, './extracted')
        self.sleep.assert_called_once_with(uploader.WAIT_SECONDS)
        self.download.assert_called_once_with(
            self.artifact['archive_download_url'], uploader.ARTIFACT_NAME + '.zip')

    def test_missing_artifact_fails_after_retry_limit(self):
        self.api_request.side_effect = [
            Mock(json=Mock(return_value=self.run)),
            Mock(json=Mock(return_value={'artifacts': []})),
        ] * 2

        with patch.object(uploader, 'WAIT_ATTEMPTS', 2):
            with self.assertRaisesRegex(RuntimeError, f'No {uploader.ARTIFACT_NAME}'):
                uploader._download_zephyr_artifact(self.workflow_id)

        self.assertEqual(self.api_request.call_count, 4)
        self.sleep.assert_called_once_with(uploader.WAIT_SECONDS)
        self.download.assert_not_called()

    def test_skips_package_workflows(self):
        self.run['path'] = '.github/workflows/packages-validation.yaml'
        self.api_request.return_value.json.return_value = self.run

        result = uploader._download_zephyr_artifact(self.workflow_id)

        self.assertIsNone(result)
        self.api_request.assert_called_once_with(self.run_url)
        self.download.assert_not_called()
        self.sleep.assert_not_called()

    def test_artifact_api_error_is_not_retried(self):
        self.run['conclusion'] = 'success'
        self.api_request.side_effect = [
            Mock(json=Mock(return_value=self.run)),
            RuntimeError('GitHub API request failed. Status: 403'),
        ]

        with self.assertRaisesRegex(RuntimeError, 'Status: 403'):
            uploader._download_zephyr_artifact(self.workflow_id)

        self.assertEqual(self.api_request.call_count, 2)
        self.download.assert_not_called()
        self.sleep.assert_not_called()

    def test_download_error_is_not_retried(self):
        self.run['conclusion'] = 'success'
        self.api_request.side_effect = [
            Mock(json=Mock(return_value=self.run)),
            Mock(json=Mock(return_value={'artifacts': [self.artifact]})),
        ]
        self.download.side_effect = RuntimeError('Download failed')

        with self.assertRaisesRegex(RuntimeError, 'Download failed'):
            uploader._download_zephyr_artifact(self.workflow_id)

        self.download.assert_called_once()
        self.sleep.assert_not_called()


class TestZephyrConnectivityFirmware(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.artifacts = self.root / 'artifacts'
        self.workspace = self.root / 'zephyrproject'
        self.workspace.mkdir()
        blob_dir = (
            self.workspace / 'modules/hal/silabs/zephyr/blobs'
            / 'wiseconnect/connectivity_firmware/standard')
        blob_dir.mkdir(parents=True)
        self.firmware = blob_dir / 'SiWG917-B.current.rps'
        self.firmware.write_bytes(b'current NWP firmware')
        (blob_dir / 'SiWG917-B.old.rps').write_bytes(b'stale NWP firmware')

        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        west = bin_dir / 'west'
        west.write_text(
            '#!/bin/sh\n'
            'printf "%s\\n" "$@" > "$TEST_WEST_ARGUMENTS"\n'
            'printf "%s\\n" "$TEST_BLOB_PATHS"\n'
            'exit "${TEST_WEST_EXIT_CODE:-0}"\n')
        west.chmod(0o755)
        self.environment = {
            **os.environ,
            'GITHUB_WORKSPACE': str(self.root),
            'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
            'TEST_BLOB_PATHS': str(self.firmware),
            'TEST_WEST_ARGUMENTS': str(self.root / 'west-arguments'),
            'TEST_WEST_EXIT_CODE': '0',
        }
        workflow_path = (
            Path(__file__).resolve().parents[2]
            / '.github/workflows/build-zephyr.yaml')
        workflow = yaml.safe_load(workflow_path.read_text())
        self.step = next(
            step for step in workflow['jobs']['zephyr-all-devices']['steps']
            if step['name'] == 'Export SiWx917 connectivity firmware')

    def _export_firmware(self):
        return subprocess.run(
            ['bash', '-c', self.step['run']],
            cwd=self.workspace, env=self.environment,
            capture_output=True, text=True, check=False)

    def test_exports_only_manifest_firmware_and_uploads_to_ubai(self):
        result = self._export_firmware()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / 'west-arguments').read_text().splitlines(),
            ['blobs', 'list', 'hal_silabs', '-f', '{abspath}'])
        exported = self.artifacts / 'WiFi-Firmware/siwx917' / self.firmware.name
        self.assertEqual(exported.read_bytes(), self.firmware.read_bytes())
        self.assertEqual(list(exported.parent.iterdir()), [exported])

        application = self.artifacts / 'all-devices-app-zephyr/BRD4338A/matter.rps'
        application.parent.mkdir(parents=True)
        application.write_bytes(b'Matter application')
        with patch.object(uploader, 'upload_to_ubai', return_value=True) as upload:
            uploader._upload_binaries(str(self.artifacts), 'test-branch', '69')

        self.assertEqual(upload.call_count, 2)
        upload.assert_has_calls([
            call(str(exported), 'Zephyr-WiFi-Firmware-siwx917', 'siwx917', 'test-branch', '69'),
            call(str(application), '', 'BRD4338A', 'test-branch', '69'),
        ], any_order=True)

    def test_other_artifacts_keep_empty_app_name(self):
        expected_calls = []
        for app_name, target in (
            ('all-devices-app-zephyr', 'siwx917'),
            ('WiFi-Firmware', 'other-target'),
        ):
            binary = self.artifacts / app_name / target / 'firmware.rps'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'firmware')
            expected_calls.append(
                call(str(binary), '', target, 'test-branch', '69'))

        with patch.object(uploader, 'upload_to_ubai', return_value=True) as upload:
            uploader._upload_binaries(str(self.artifacts), 'test-branch', '69')

        self.assertEqual(upload.call_count, len(expected_calls))
        upload.assert_has_calls(expected_calls, any_order=True)

    def test_missing_manifest_firmware_fails_instead_of_using_stale_blob(self):
        self.firmware.unlink()

        result = self._export_firmware()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(self.firmware.name, result.stderr)
        self.assertEqual(list(self.artifacts.rglob('*.rps')), [])

    def test_missing_firmware_entry_fails(self):
        self.environment['TEST_BLOB_PATHS'] = '/zephyr/blobs/unrelated-library.a'

        result = self._export_firmware()

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.artifacts.exists())

    def test_west_failure_is_not_ignored(self):
        self.environment['TEST_WEST_EXIT_CODE'] = '1'

        result = self._export_firmware()

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.artifacts.exists())


class TestZephyrUploaderEntryPoint(unittest.TestCase):
    def test_direct_script_execution_does_not_require_pythonpath(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, '-E', '-B', uploader.__file__, '--help'],
                cwd=directory,
                env={**os.environ, 'GITHUB_ACCESS_TOKEN': 'test-token'},
                capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--workflow_id', result.stdout)


class TestZephyrRevisions(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.revision_dir = self.root / 'zephyr-silabs-revisions'
        self.revision_dir.mkdir()
        self.repository = Path(__file__).resolve().parents[2]

    def test_reports_all_unique_checkout_revisions(self):
        for build_id, revision in (
            ('light-firmware', '1' * 40),
            ('light-ota', '1' * 40),
            ('dishwasher-firmware', '2' * 40),
        ):
            (self.revision_dir / f'{build_id}.txt').write_text(revision + '\n')
        output = io.StringIO()

        with redirect_stdout(output):
            uploader._print_zephyr_revisions(str(self.root))

        self.assertEqual(output.getvalue().splitlines(), [
            f"Zephyr-Silabs Commit SHA - {'1' * 40}",
            f"Zephyr-Silabs Commit SHA - {'2' * 40}",
        ])

    def test_legacy_artifact_reports_missing_provenance(self):
        self.revision_dir.rmdir()
        output = io.StringIO()

        with redirect_stdout(output):
            uploader._print_zephyr_revisions(str(self.root))

        self.assertIn('Warning:', output.getvalue())
        self.assertIn('revision metadata is unavailable', output.getvalue())
        self.assertNotIn('Zephyr-Silabs Commit SHA - ', output.getvalue())

    def test_invalid_revision_is_rejected(self):
        (self.revision_dir / 'light.txt').write_text('not-a-commit\n')

        with self.assertRaisesRegex(RuntimeError, 'Invalid Zephyr-Silabs revision'):
            uploader._print_zephyr_revisions(str(self.root))

    def test_empty_revision_metadata_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'No Zephyr-Silabs revisions found'):
            uploader._print_zephyr_revisions(str(self.root))

    def test_main_reports_revision_without_uploading_metadata_individually(self):
        revision = '1' * 40
        (self.revision_dir / 'light.txt').write_text(revision + '\n')
        binary = self.root / 'all-devices-app-zephyr/BRD4338A/matter.rps'
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b'Matter application')
        args = Mock(workflow_id=12345, branch_name='test-branch', build_number='69')
        output = io.StringIO()

        with (
            patch.object(uploader, '_parse_args', return_value=args),
            patch.object(uploader, '_download_zephyr_artifact', return_value=str(self.root)),
            patch.object(uploader, 'upload_to_ubai', return_value=True) as upload,
            redirect_stdout(output),
        ):
            uploader.main()

        self.assertIn(f'Zephyr-Silabs Commit SHA - {revision}', output.getvalue())
        self.assertEqual(upload.call_args_list, [
            call(str(binary), '', 'BRD4338A', 'test-branch', '69'),
            call(file_path='./dev-artifacts-zephyr.zip', app_name='matter',
                 target='matter', branch_name='test-branch', build_number='69'),
        ])

    def test_upload_failure_is_propagated(self):
        (self.revision_dir / 'light.txt').write_text('1' * 40 + '\n')
        binary = self.root / 'all-devices-app-zephyr/BRD4338A/matter.rps'
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b'Matter application')
        args = Mock(workflow_id=12345, branch_name='test-branch', build_number='69')

        with (
            patch.object(uploader, '_parse_args', return_value=args),
            patch.object(uploader, '_download_zephyr_artifact', return_value=str(self.root)),
            patch.object(uploader, 'upload_to_ubai', return_value=False),
            self.assertRaisesRegex(RuntimeError, 'UBAI upload failed'),
        ):
            uploader.main()

    def test_workflow_exports_actual_revision_for_each_matrix_build(self):
        checkout = self.root / 'zephyrproject/zephyr-silabs'
        checkout.parent.mkdir()
        checkout.symlink_to(self.repository, target_is_directory=True)
        revision = subprocess.check_output(
            ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        workflow = yaml.safe_load(
            (self.repository / '.github/workflows/build-zephyr.yaml').read_text())
        step = next(
            step for step in workflow['jobs']['zephyr-all-devices']['steps']
            if step['name'] == 'Export Zephyr checkout revision')

        for build_id in ('siwx917-light-firmware', 'siwx917-light-ota'):
            result = subprocess.run(
                ['bash', '-c', step['run']], cwd=self.root,
                env={**os.environ, 'BUILD_ID': build_id},
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            exported = self.root / 'artifacts/zephyr-silabs-revisions' / f'{build_id}.txt'
            self.assertEqual(exported.read_text(), revision + '\n')

        self.assertEqual(len(list(exported.parent.iterdir())), 2)

    def test_zephyr_artifacts_use_repository_default_retention(self):
        workflow = yaml.safe_load(
            (self.repository / '.github/workflows/build-zephyr.yaml').read_text())
        uploads = [
            step for job in workflow['jobs'].values() for step in job['steps']
            if step.get('uses', '').startswith('actions/upload-artifact@')
        ]

        self.assertEqual(len(uploads), 2)
        for step in uploads:
            with self.subTest(step=step['name']):
                self.assertNotIn('retention-days', step['with'])


if __name__ == '__main__':
    unittest.main()
