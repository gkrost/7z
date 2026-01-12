#!/usr/bin/env python3
"""
7z Format Tests
Comprehensive testing for 7z archive format
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import time


def run_tests(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run comprehensive 7z format tests"""
    results = {
        'format': '7z',
        'tests': {},
        'summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
    }
    
    test_suite = _7zTestSuite(config)
    
    # Run all tests
    test_methods = [
        'test_basic_compression',
        'test_compression_levels',
        'test_multi_threading',
        'test_solid_archives',
        'test_encryption',
        'test_unicode_filenames',
        'test_large_files',
        'test_mixed_content',
        'test_integrity',
        'test_extraction'
    ]
    
    for test_method in test_methods:
        try:
            test_result = getattr(test_suite, test_method)()
            results['tests'][test_method] = test_result
            results['summary']['total_tests'] += 1
            
            if test_result['status'] == 'passed':
                results['summary']['passed'] += 1
            elif test_result['status'] == 'failed':
                results['summary']['failed'] += 1
            else:
                results['summary']['skipped'] += 1
                
            print(f"  {test_method}: {test_result['status']}")
            
        except Exception as e:
            results['tests'][test_method] = {
                'status': 'error',
                'error': str(e),
                'duration': 0.0
            }
            results['summary']['failed'] += 1
            print(f"  {test_method}: error - {e}")
    
    return results


class _7zTestSuite:
    """Test suite for 7z format"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_data_dir = Path('test_data')
        self.temp_dir = Path(config.get('test_settings', {}).get('temp_dir', '/tmp/7z_tests'))
        self.sevenz_exec = self._find_7z_executable()
        
        if not self.sevenz_exec:
            raise RuntimeError("7-Zip executable not found")
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_7z_executable(self) -> Optional[Path]:
        """Find 7-Zip executable"""
        # Try different names
        for name in ['7z', '7zz', '7za']:
            exec_path = shutil.which(name)
            if exec_path:
                return Path(exec_path)
        
        # Check current directory
        for path in ['./CPP/7zip/Bundles/Alone/7z', './CPP/7zip/Bundles/Alone7z/7z']:
            if Path(path).exists():
                return Path(path)
        
        return None
    
    def test_basic_compression(self) -> Dict[str, Any]:
        """Test basic 7z compression"""
        start_time = time.time()
        test_file = None
        archive_file = None
        extract_dir = None
        
        try:
            # Create test file
            test_file = self.temp_dir / 'basic_test.txt'
            test_file.write_text('Hello, World! This is a test file for 7z compression.')
            
            # Compress to 7z
            archive_file = self.temp_dir / 'basic_test.7z'
            cmd = [str(self.sevenz_exec), 'a', str(archive_file), str(test_file)]
            
            result = self._run_command(cmd)
            
            if result['success'] and archive_file.exists():
                # Test extraction
                extract_dir = self.temp_dir / 'extract'
                extract_dir.mkdir(exist_ok=True)
                
                cmd = [str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y']
                extract_result = self._run_command(cmd)
                
                extracted_file = extract_dir / 'basic_test.txt'
                content_match = extracted_file.exists() and extracted_file.read_text() == test_file.read_text()
                
                return {
                    'status': 'passed' if content_match else 'failed',
                    'duration': time.time() - start_time,
                    'archive_size': archive_file.stat().st_size,
                    'compression_ratio': archive_file.stat().st_size / test_file.stat().st_size,
                    'details': f"Archive created: {archive_file.exists()}, Content matches: {content_match}"
                }
            else:
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Unknown error'),
                    'details': 'Compression failed'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [test_file, archive_file]:
                if path and path.exists():
                    path.unlink()
    
    def test_compression_levels(self) -> Dict[str, Any]:
        """Test different compression levels"""
        start_time = time.time()
        test_file = None
        
        try:
            # Create test file with compressible content
            test_file = self.temp_dir / 'levels_test.txt'
            content = 'A' * 10000 + 'B' * 10000 + 'C' * 10000  # Repetitive, highly compressible
            test_file.write_text(content)
            
            original_size = test_file.stat().st_size
            level_results = []
            
            # Test different compression levels
            for level in [0, 1, 3, 5, 7, 9]:
                archive_file = self.temp_dir / f'level_{level}.7z'
                cmd = [str(self.sevenz_exec), 'a', f'-mx={level}', str(archive_file), str(test_file)]
                
                result = self._run_command(cmd)
                
                if result['success'] and archive_file.exists():
                    archive_size = archive_file.stat().st_size
                    ratio = archive_size / original_size
                    
                    level_results.append({
                        'level': level,
                        'archive_size': archive_size,
                        'ratio': ratio,
                        'success': True
                    })
                else:
                    level_results.append({
                        'level': level,
                        'success': False,
                        'error': result.get('stderr', 'Unknown error')
                    })
                
                # Cleanup
                if archive_file.exists():
                    archive_file.unlink()
            
            # Verify that higher levels give better compression
            successful_levels = [r for r in level_results if r['success']]
            
            if len(successful_levels) >= 3:
                # Check if compression generally improves with higher levels
                ratios = [r['ratio'] for r in successful_levels]
                improvement = ratios[0] > ratios[-1]  # Level 0 vs Level 9
                
                return {
                    'status': 'passed' if improvement else 'failed',
                    'duration': time.time() - start_time,
                    'details': f'Tested {len(successful_levels)} levels, compression improves: {improvement}',
                    'level_results': level_results
                }
            else:
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'details': f'Only {len(successful_levels)} levels succeeded',
                    'level_results': level_results
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            if test_file and test_file.exists():
                test_file.unlink()
    
    def test_multi_threading(self) -> Dict[str, Any]:
        """Test multi-threading capabilities"""
        start_time = time.time()
        test_file = None
        
        try:
            # Create larger test file
            test_file = self.temp_dir / 'threading_test.bin'
            test_file.write_bytes(b'X' * 1024 * 1024)  # 1MB
            
            original_size = test_file.stat().st_size
            thread_results = []
            
            # Test different thread counts
            for threads in [1, 2, 4]:
                archive_file = self.temp_dir / f'threads_{threads}.7z'
                cmd = [str(self.sevenz_exec), 'a', f'-mmt{threads}', str(archive_file), str(test_file)]
                
                start = time.time()
                result = self._run_command(cmd)
                duration = time.time() - start
                
                if result['success'] and archive_file.exists():
                    thread_results.append({
                        'threads': threads,
                        'duration': duration,
                        'success': True
                    })
                else:
                    thread_results.append({
                        'threads': threads,
                        'success': False,
                        'error': result.get('stderr', 'Unknown error')
                    })
                
                # Cleanup
                if archive_file.exists():
                    archive_file.unlink()
            
            successful_tests = [r for r in thread_results if r['success']]
            
            if len(successful_tests) >= 2:
                # Check if multi-threading provides any benefit
                single_thread_time = next(r['duration'] for r in successful_tests if r['threads'] == 1)
                multi_thread_time = min(r['duration'] for r in successful_tests if r['threads'] > 1)
                improvement = multi_thread_time < single_thread_time
                
                return {
                    'status': 'passed' if len(successful_tests) >= 3 else 'failed',
                    'duration': time.time() - start_time,
                    'details': f'Tested {len(successful_tests)} thread configs, multi-threading works: {improvement}',
                    'thread_results': thread_results
                }
            else:
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'details': f'Only {len(successful_tests)} thread configs succeeded',
                    'thread_results': thread_results
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            if test_file and test_file.exists():
                test_file.unlink()
    
    def test_solid_archives(self) -> Dict[str, Any]:
        """Test solid archive creation"""
        start_time = time.time()
        files = []
        normal_archive = None
        solid_archive = None
        
        try:
            # Create multiple test files
            files = []
            for i in range(3):
                test_file = self.temp_dir / f'solid_test_{i}.txt'
                test_file.write_text(f'This is test file {i} with some content ' + 'A' * 100)
                files.append(test_file)
            
            # Test normal vs solid archive
            normal_archive = self.temp_dir / 'normal.7z'
            solid_archive = self.temp_dir / 'solid.7z'
            
            # Normal archive
            cmd = [str(self.sevenz_exec), 'a', str(normal_archive)] + [str(f) for f in files]
            normal_result = self._run_command(cmd)
            
            # Solid archive
            cmd = [str(self.sevenz_exec), 'a', str(solid_archive), '-ms'] + [str(f) for f in files]
            solid_result = self._run_command(cmd)
            
            success = (normal_result['success'] and solid_result['success'] and 
                      normal_archive.exists() and solid_archive.exists())
            
            if success:
                normal_size = normal_archive.stat().st_size
                solid_size = solid_archive.stat().st_size
                solid_better = solid_size < normal_size
                
                return {
                    'status': 'passed',
                    'duration': time.time() - start_time,
                    'details': f'Normal: {normal_size} bytes, Solid: {solid_size} bytes, Solid better: {solid_better}',
                    'normal_size': normal_size,
                    'solid_size': solid_size
                }
            else:
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': normal_result.get('stderr', '') + ';' + solid_result.get('stderr', ''),
                    'details': 'Archive creation failed'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for archive_path in [normal_archive, solid_archive]:
                if archive_path and archive_path.exists():
                    archive_path.unlink()
            for file_path in files:
                if file_path and file_path.exists():
                    file_path.unlink()
    
    def test_encryption(self) -> Dict[str, Any]:
        """Test encryption capabilities"""
        start_time = time.time()
        test_file = None
        archive_file = None
        extract_dir = None
        
        try:
            # Create test file
            test_file = self.temp_dir / 'encrypt_test.txt'
            test_file.write_text('This is secret content for encryption testing.')
            
            password = 'test123'
            archive_file = self.temp_dir / 'encrypted.7z'
            
            # Encrypt with password
            cmd = [str(self.sevenz_exec), 'a', f'-p{password}', str(archive_file), str(test_file)]
            result = self._run_command(cmd)
            
            if not result['success'] or not archive_file.exists():
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Encryption failed'),
                    'details': 'Encryption failed'
                }
            
            # Test extraction with correct password
            extract_dir = self.temp_dir / 'extract_encrypted'
            extract_dir.mkdir(exist_ok=True)
            
            cmd = [str(self.sevenz_exec), 'x', f'-p{password}', str(archive_file), f'-o{extract_dir}', '-y']
            extract_result = self._run_command(cmd)
            
            extracted_file = extract_dir / 'encrypt_test.txt'
            content_match = (extract_result['success'] and extracted_file.exists() and 
                          extracted_file.read_text() == test_file.read_text())
            
            return {
                'status': 'passed' if content_match else 'failed',
                'duration': time.time() - start_time,
                'details': f'Encryption successful, extraction: {content_match}',
                'archive_size': archive_file.stat().st_size
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [test_file, archive_file, extract_dir]:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
    
    def test_unicode_filenames(self) -> Dict[str, Any]:
        """Test Unicode filename support"""
        start_time = time.time()
        test_file = None
        archive_file = None
        extract_dir = None
        
        try:
            # Create file with Unicode name
            unicode_name = 'tëst_файл_中国.txt'  # Mix of languages
            test_file = self.temp_dir / unicode_name
            test_file.write_text('Unicode filename test content')
            
            # Create archive with Unicode filename
            archive_file = self.temp_dir / 'unicode.7z'
            cmd = [str(self.sevenz_exec), 'a', str(archive_file), str(test_file)]
            result = self._run_command(cmd)
            
            if not result['success'] or not archive_file.exists():
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Unicode test failed'),
                    'details': 'Archive creation with Unicode filename failed'
                }
            
            # Extract and verify
            extract_dir = self.temp_dir / 'extract_unicode'
            extract_dir.mkdir(exist_ok=True)
            
            cmd = [str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y']
            extract_result = self._run_command(cmd)
            
            extracted_file = extract_dir / unicode_name
            content_match = (extract_result['success'] and extracted_file.exists() and 
                          extracted_file.read_text() == test_file.read_text())
            
            return {
                'status': 'passed' if content_match else 'failed',
                'duration': time.time() - start_time,
                'details': f'Unicode filename: {unicode_name}, Extraction successful: {content_match}',
                'unicode_name': unicode_name
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [test_file, archive_file, extract_dir]:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
    
    def test_large_files(self) -> Dict[str, Any]:
        """Test handling of large files"""
        start_time = time.time()
        test_file = None
        archive_file = None
        extract_dir = None
        
        try:
            # Create 50MB test file
            test_file = self.temp_dir / 'large_test.bin'
            with open(test_file, 'wb') as f:
                f.write(b'L' * (50 * 1024 * 1024))
            
            original_size = test_file.stat().st_size
            archive_file = self.temp_dir / 'large.7z'
            
            # Compress large file
            cmd = [str(self.sevenz_exec), 'a', str(archive_file), str(test_file)]
            result = self._run_command(cmd)
            
            if not result['success'] or not archive_file.exists():
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Large file test failed'),
                    'details': 'Large file compression failed'
                }
            
            # Test extraction
            extract_dir = self.temp_dir / 'extract_large'
            extract_dir.mkdir(exist_ok=True)
            
            cmd = [str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y']
            extract_result = self._run_command(cmd)
            
            extracted_file = extract_dir / 'large_test.bin'
            size_match = (extract_result['success'] and extracted_file.exists() and 
                         extracted_file.stat().st_size == original_size)
            
            return {
                'status': 'passed' if size_match else 'failed',
                'duration': time.time() - start_time,
                'details': f'Large file: {original_size // (1024*1024)}MB, Size match: {size_match}',
                'original_size': original_size,
                'archive_size': archive_file.stat().st_size
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [test_file, archive_file, extract_dir]:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
    
    def test_mixed_content(self) -> Dict[str, Any]:
        """Test mixed content types"""
        start_time = time.time()
        files = []
        text_file = None
        binary_file = None
        subdir = None
        subfile = None
        archive_file = None
        extract_dir = None
        
        try:
            # Create files of different types
            # Text file
            text_file = self.temp_dir / 'mixed_text.txt'
            text_file.write_text('This is a text file for mixed content testing.')
            files.append(text_file)
            
            # Binary file
            binary_file = self.temp_dir / 'mixed_binary.bin'
            binary_file.write_bytes(b'\x00\x01\x02\x03' * 256)
            files.append(binary_file)
            
            # Create subdirectory with file
            subdir = self.temp_dir / 'subdir'
            subdir.mkdir(exist_ok=True)
            subfile = subdir / 'subfile.txt'
            subfile.write_text('File in subdirectory')
            files.append(subfile)
            
            # Create archive with mixed content using relative paths
            archive_file = self.temp_dir / 'mixed.7z'
            cmd = [
                str(self.sevenz_exec),
                'a',
                str(archive_file),
                'mixed_text.txt',
                'mixed_binary.bin',
                'subdir/subfile.txt'
            ]
            result = self._run_command(cmd, cwd=self.temp_dir)
            
            if not result['success'] or not archive_file.exists():
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Mixed content test failed'),
                    'details': 'Mixed content archive creation failed'
                }
            
            # Extract and verify structure
            extract_dir = self.temp_dir / 'extract_mixed'
            extract_dir.mkdir(exist_ok=True)
            
            cmd = [str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y']
            extract_result = self._run_command(cmd)
            
            # Verify all files exist
            extracted_text = extract_dir / 'mixed_text.txt'
            extracted_binary = extract_dir / 'mixed_binary.bin'
            extracted_subdir = extract_dir / 'subdir'
            extracted_subfile = extracted_subdir / 'subfile.txt'
            
            all_files_exist = (extract_result['success'] and
                              extracted_text.exists() and extracted_binary.exists() and
                              extracted_subdir.exists() and extracted_subfile.exists())
            
            content_match = False
            if all_files_exist:
                content_match = (extracted_text.read_text() == text_file.read_text() and
                               extracted_binary.read_bytes() == binary_file.read_bytes() and
                               extracted_subfile.read_text() == subfile.read_text())
            
            return {
                'status': 'passed' if content_match else 'failed',
                'duration': time.time() - start_time,
                'details': f'All files exist: {all_files_exist}, Content matches: {content_match}',
                'files_count': len(files),
                'archive_size': archive_file.stat().st_size
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [archive_file, extract_dir, subdir]:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            for file_path in [text_file, binary_file, subfile]:
                if file_path and file_path.exists():
                    file_path.unlink()
    
    def test_integrity(self) -> Dict[str, Any]:
        """Test archive integrity"""
        start_time = time.time()
        test_file = None
        archive_file = None
        
        try:
            # Create test file
            test_file = self.temp_dir / 'integrity_test.txt'
            test_file.write_text('Integrity test content for archive verification.')
            
            archive_file = self.temp_dir / 'integrity.7z'
            
            # Create archive
            cmd = [str(self.sevenz_exec), 'a', str(archive_file), str(test_file)]
            result = self._run_command(cmd)
            
            if not result['success'] or not archive_file.exists():
                return {
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': result.get('stderr', 'Archive creation failed'),
                    'details': 'Archive creation failed for integrity test'
                }
            
            # Test integrity
            cmd = [str(self.sevenz_exec), 't', str(archive_file)]
            integrity_result = self._run_command(cmd)
            
            return {
                'status': 'passed' if integrity_result['success'] else 'failed',
                'duration': time.time() - start_time,
                'details': f'Integrity test: {integrity_result["success"]}',
                'integrity_output': integrity_result.get('stdout', ''),
                'integrity_error': integrity_result.get('stderr', '')
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            for path in [test_file, archive_file]:
                if path and path.exists():
                    path.unlink()
    
    def test_extraction(self) -> Dict[str, Any]:
        """Test extraction from existing archives"""
        start_time = time.time()
        extract_dir = None
        
        try:
            # Check if we have any test archives
            reference_dir = Path('test_data/reference')
            if not reference_dir.exists():
                return {
                    'status': 'skipped',
                    'duration': time.time() - start_time,
                    'reason': 'No reference archives found',
                    'details': 'Reference archives directory not found'
                }
            
            # Find any .7z files
            archives = list(reference_dir.glob('*.7z'))
            if not archives:
                return {
                    'status': 'skipped',
                    'duration': time.time() - start_time,
                    'reason': 'No 7z reference archives found',
                    'details': 'No .7z files in reference directory'
                }
            
            # Test extraction of first archive found
            archive_file = archives[0]
            extract_dir = self.temp_dir / 'extract_existing'
            extract_dir.mkdir(exist_ok=True)
            
            cmd = [str(self.sevenz_exec), 'x', str(archive_file), f'-o{extract_dir}', '-y']
            result = self._run_command(cmd)
            
            files_extracted = len(list(extract_dir.rglob('*'))) if extract_dir.exists() else 0
            
            return {
                'status': 'passed' if result['success'] else 'failed',
                'duration': time.time() - start_time,
                'details': f'Extracted {files_extracted} files from {archive_file.name}',
                'archive_name': archive_file.name,
                'files_extracted': files_extracted
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'details': 'Exception occurred'
            }
        
        finally:
            # Cleanup
            if extract_dir and extract_dir.exists():
                shutil.rmtree(extract_dir)
    
    def _run_command(self, cmd: List[str], cwd: Path | None = None) -> Dict[str, Any]:
        """Run command and return result"""
        import subprocess
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'returncode': -1
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'returncode': -1
            }


if __name__ == '__main__':
    # Test the 7z module
    test_config = {
        'test_settings': {
            'temp_dir': '/tmp/7z_test_7z'
        }
    }
    
    results = run_tests(test_config)
    print(f"7z format tests completed:")
    print(f"  Total: {results['summary']['total_tests']}")
    print(f"  Passed: {results['summary']['passed']}")
    print(f"  Failed: {results['summary']['failed']}")
    print(f"  Skipped: {results['summary']['skipped']}")