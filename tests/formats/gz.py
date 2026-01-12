"""
GZIP Format Tests
"""

import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


def run_tests(config: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        'format': 'gz',
        'tests': {},
        'summary': {'total_tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
    }

    test_suite = GzipTestSuite(config)
    test_methods = ['test_basic_compression', 'test_integrity', 'test_extraction']

    for test_method in test_methods:
        try:
            test_result = getattr(test_suite, test_method)()
            results['tests'][test_method] = test_result
            results['summary']['total_tests'] += 1
            status = test_result['status']
            if status == 'passed':
                results['summary']['passed'] += 1
            elif status == 'failed':
                results['summary']['failed'] += 1
            else:
                results['summary']['skipped'] += 1
        except Exception as exc:
            results['tests'][test_method] = {'status': 'error', 'error': str(exc), 'duration': 0.0}
            results['summary']['failed'] += 1

    return results


class GzipTestSuite:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.temp_dir = Path(config.get('test_settings', {}).get('temp_dir', '/tmp/7z_tests'))
        self.sevenz_exec = self._find_7z_executable()
        if not self.sevenz_exec:
            raise RuntimeError('7-Zip executable not found')
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _find_7z_executable(self) -> Optional[Path]:
        for name in ['7z', '7zz', '7za']:
            exec_path = shutil.which(name)
            if exec_path:
                return Path(exec_path)
        for path in ['./CPP/7zip/Bundles/Alone/7z', './CPP/7zip/Bundles/Alone7z/7z']:
            candidate = Path(path)
            if candidate.exists():
                return candidate
        return None

    def test_basic_compression(self) -> Dict[str, Any]:
        start_time = time.time()
        test_file = None
        archive_file = None
        extract_dir = None
        try:
            test_file = self.temp_dir / 'gzip_basic.txt'
            test_file.write_text('gzip basic test')
            archive_file = self.temp_dir / 'gzip_basic.gz'
            result = self._run_command([str(self.sevenz_exec), 'a', '-tgzip', str(archive_file), str(test_file)])
            if not result['success'] or not archive_file.exists():
                return {'status': 'failed', 'duration': time.time() - start_time, 'error': result.get('stderr', '')}

            extract_dir = self.temp_dir / 'gzip_extract'
            extract_dir.mkdir(exist_ok=True)
            extract_result = self._run_command([str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y'])
            extracted_file = extract_dir / test_file.name
            content_match = extract_result['success'] and extracted_file.exists() and extracted_file.read_text() == test_file.read_text()
            return {'status': 'passed' if content_match else 'failed', 'duration': time.time() - start_time}
        except Exception as exc:
            return {'status': 'error', 'duration': time.time() - start_time, 'error': str(exc)}
        finally:
            for path in [test_file, archive_file, extract_dir]:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()

    def test_integrity(self) -> Dict[str, Any]:
        start_time = time.time()
        test_file = None
        archive_file = None
        try:
            test_file = self.temp_dir / 'gzip_integrity.txt'
            test_file.write_text('gzip integrity test')
            archive_file = self.temp_dir / 'gzip_integrity.gz'
            result = self._run_command([str(self.sevenz_exec), 'a', '-tgzip', str(archive_file), str(test_file)])
            if not result['success'] or not archive_file.exists():
                return {'status': 'failed', 'duration': time.time() - start_time, 'error': result.get('stderr', '')}

            check_result = self._run_command([str(self.sevenz_exec), 't', str(archive_file)])
            return {'status': 'passed' if check_result['success'] else 'failed', 'duration': time.time() - start_time}
        except Exception as exc:
            return {'status': 'error', 'duration': time.time() - start_time, 'error': str(exc)}
        finally:
            for path in [test_file, archive_file]:
                if path and path.exists():
                    path.unlink()

    def test_extraction(self) -> Dict[str, Any]:
        start_time = time.time()
        extract_dir = None
        try:
            reference_dir = Path('test_data/reference')
            if not reference_dir.exists():
                return {'status': 'skipped', 'duration': time.time() - start_time, 'reason': 'reference_dir_missing'}
            archives = list(reference_dir.glob('*.gz'))
            if not archives:
                return {'status': 'skipped', 'duration': time.time() - start_time, 'reason': 'no_reference_gz'}

            archive_file = archives[0]
            extract_dir = self.temp_dir / 'gzip_reference_extract'
            extract_dir.mkdir(exist_ok=True)
            result = self._run_command([str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y'])
            files_extracted = len(list(extract_dir.rglob('*')))
            return {'status': 'passed' if result['success'] else 'failed', 'duration': time.time() - start_time, 'files_extracted': files_extracted}
        except Exception as exc:
            return {'status': 'error', 'duration': time.time() - start_time, 'error': str(exc)}
        finally:
            if extract_dir and extract_dir.exists():
                shutil.rmtree(extract_dir)

    def _run_command(self, cmd: List[str], cwd: Path | None = None) -> Dict[str, Any]:
        import subprocess
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
            return {'success': result.returncode == 0, 'stdout': result.stdout, 'stderr': result.stderr}
        except subprocess.TimeoutExpired:
            return {'success': False, 'stderr': 'Command timed out'}
        except Exception as exc:
            return {'success': False, 'stderr': str(exc)}
