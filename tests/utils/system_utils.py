#!/usr/bin/env python3
"""
System Utilities for Test Framework
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class SystemUtils:
    """System utility functions for testing"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'platform': self.platform,
            'architecture': self.architecture,
            'python_version': sys.version,
            'cpu_count': os.cpu_count(),
            'memory_info': self._get_memory_info(),
            'disk_info': self._get_disk_info(),
            'environment': dict(os.environ)
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            if self.platform == 'linux':
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                
                mem_total = 0
                mem_available = 0
                
                for line in meminfo.split('\n'):
                    if 'MemTotal:' in line:
                        mem_total = int(line.split()[1]) * 1024  # Convert KB to bytes
                    elif 'MemAvailable:' in line:
                        mem_available = int(line.split()[1]) * 1024
                
                return {
                    'total': mem_total,
                    'available': mem_available,
                    'used': mem_total - mem_available
                }
            
            elif self.platform == 'windows':
                import psutil
                memory = psutil.virtual_memory()
                return {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used
                }
            
            else:
                return {'error': 'Memory info not available on this platform'}
        
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        try:
            current_path = Path.cwd()
            stat = shutil.disk_usage(current_path)
            
            return {
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'path': str(current_path)
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def find_executable(self, name: str) -> Optional[Path]:
        """Find executable in system PATH"""
        executable_path = shutil.which(name)
        return Path(executable_path) if executable_path else None
    
    def run_command(self, command: List[str], timeout: Optional[int] = None, 
                   capture_output: bool = True, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run system command and return result"""
        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                cwd=cwd
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(command)
            }
        
        except subprocess.TimeoutExpired as e:
            return {
                'success': False,
                'error': 'timeout',
                'timeout': timeout,
                'command': ' '.join(command)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(command)
            }
    
    def get_file_info(self, filepath: Path) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            stat = filepath.stat()
            
            return {
                'exists': True,
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'ctime': stat.st_ctime,
                'atime': stat.st_atime,
                'mode': stat.st_mode,
                'is_file': filepath.is_file(),
                'is_dir': filepath.is_dir(),
                'is_symlink': filepath.is_symlink(),
                'absolute_path': str(filepath.absolute())
            }
        
        except Exception as e:
            return {
                'exists': False,
                'error': str(e),
                'path': str(filepath)
            }
    
    def create_temp_directory(self, prefix: str = "7z_test_") -> Path:
        """Create temporary directory"""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return temp_dir
    
    def cleanup_temp_directory(self, temp_dir: Path) -> bool:
        """Clean up temporary directory"""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return True
        except Exception:
            return False
    
    def measure_time(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure execution time of a function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def get_cpu_usage(self, duration: float = 1.0) -> Dict[str, Any]:
        """Get CPU usage over specified duration"""
        try:
            if self.platform == 'linux':
                # Simple CPU usage measurement
                with open('/proc/stat', 'r') as f:
                    first_line = f.readline().strip()
                
                time.sleep(duration)
                
                with open('/proc/stat', 'r') as f:
                    second_line = f.readline().strip()
                
                # Parse CPU times
                first_times = list(map(int, first_line.split()[1:]))
                second_times = list(map(int, second_line.split()[1:]))
                
                total_diff = sum(second_times[i] - first_times[i] for i in range(len(first_times)))
                idle_diff = second_times[3] - first_times[3]
                
                if total_diff > 0:
                    usage = (total_diff - idle_diff) / total_diff * 100
                else:
                    usage = 0
                
                return {
                    'usage_percent': usage,
                    'duration': duration,
                    'method': 'proc_stat'
                }
            
            elif self.platform == 'windows':
                import psutil
                usage = psutil.cpu_percent(interval=duration)
                return {
                    'usage_percent': usage,
                    'duration': duration,
                    'method': 'psutil'
                }
            
            else:
                return {'error': 'CPU usage measurement not available on this platform'}
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        try:
            if self.platform == 'linux':
                with open('/proc/self/status', 'r') as f:
                    status = f.read()
                
                for line in status.split('\n'):
                    if line.startswith('VmRSS:'):
                        rss_kb = int(line.split()[1])
                        return {
                            'rss_bytes': rss_kb * 1024,
                            'rss_kb': rss_kb,
                            'method': 'proc_self_status'
                        }
                
                return {'error': 'VmRSS not found in /proc/self/status'}
            
            elif self.platform == 'windows':
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                
                return {
                    'rss_bytes': memory_info.rss,
                    'vms_bytes': memory_info.vms,
                    'method': 'psutil'
                }
            
            return {'error': 'Memory usage measurement not available on this platform'}
        
        except Exception as e:
            return {'error': str(e)}
    
    def check_disk_space(self, path: Path, required_bytes: int) -> bool:
        """Check if enough disk space is available"""
        try:
            stat = shutil.disk_usage(path)
            return stat.free >= required_bytes
        except Exception:
            return False
    
    def copy_file_with_progress(self, src: Path, dst: Path, 
                               progress_callback=None) -> Dict[str, Any]:
        """Copy file with optional progress callback"""
        bytes_copied = 0
        try:
            file_size = src.stat().st_size
            
            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                while True:
                    chunk = fsrc.read(64 * 1024)  # 64KB chunks
                    if not chunk:
                        break
                    
                    fdst.write(chunk)
                    bytes_copied += len(chunk)
                    
                    if progress_callback:
                        progress = bytes_copied / file_size
                        progress_callback(progress, bytes_copied, file_size)
            
            return {
                'success': True,
                'bytes_copied': bytes_copied,
                'file_size': file_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'bytes_copied': bytes_copied
            }
    
    def is_process_running(self, process_name: str) -> bool:
        """Check if a process is running"""
        try:
            if self.platform == 'linux':
                result = self.run_command(['pgrep', '-f', process_name])
                return result['success'] and result['stdout'].strip()
            
            elif self.platform == 'windows':
                result = self.run_command(['tasklist', '/FI', f'IMAGENAME eq {process_name}'])
                return result['success'] and process_name in result['stdout']
            
            else:
                return False
        
        except Exception:
            return False
    
    def kill_process(self, process_name: str) -> bool:
        """Kill a process by name"""
        try:
            if self.platform == 'linux':
                result = self.run_command(['pkill', '-f', process_name])
                return result['success']
            
            elif self.platform == 'windows':
                result = self.run_command(['taskkill', '/F', '/IM', process_name])
                return result['success']
            
            else:
                return False
        
        except Exception:
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'method': 'socket'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def validate_path(self, path: Path, must_exist: bool = True, 
                     must_be_file: bool = False, must_be_dir: bool = False) -> Dict[str, Any]:
        """Validate path meets specified criteria"""
        result = {
            'valid': True,
            'path': str(path),
            'exists': path.exists(),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'is_absolute': path.is_absolute(),
            'errors': []
        }
        
        if must_exist and not path.exists():
            result['valid'] = False
            result['errors'].append('Path must exist')
        
        if must_be_file and not path.is_file():
            result['valid'] = False
            result['errors'].append('Path must be a file')
        
        if must_be_dir and not path.is_dir():
            result['valid'] = False
            result['errors'].append('Path must be a directory')
        
        return result