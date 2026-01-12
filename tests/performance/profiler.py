#!/usr/bin/env python3
"""
Performance Profiler for CPU and Memory Measurement
"""

import time
import threading
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import json


@dataclass
class ProfileResult:
    """Result of profiling session"""
    duration: float
    cpu_percent: float
    memory_mb: float
    peak_memory_mb: float
    samples: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None


class Profiler:
    """Profiles CPU and memory usage during execution"""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        self.samples = []
        self.peak_memory = 0
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        self.monitoring = True
        self.samples = []
        self.peak_memory = 0
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> ProfileResult:
        """Stop monitoring and return results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        if not self.samples:
            return ProfileResult(
                duration=0.0, cpu_percent=0.0, memory_mb=0.0,
                peak_memory_mb=0.0, samples=[], success=False,
                error="No samples collected"
            )
        
        # Calculate metrics
        duration = self.samples[-1]['timestamp'] - self.samples[0]['timestamp']
        cpu_values = [s['cpu_percent'] for s in self.samples if 'cpu_percent' in s]
        memory_values = [s['memory_mb'] for s in self.samples if 'memory_mb' in s]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
        
        return ProfileResult(
            duration=duration,
            cpu_percent=avg_cpu,
            memory_mb=avg_memory,
            peak_memory_mb=self.peak_memory,
            samples=self.samples,
            success=True
        )
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        start_time = time.time()
        
        while self.monitoring:
            try:
                current_time = time.time()
                
                # Get CPU usage
                try:
                    cpu_percent = self.process.cpu_percent()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cpu_percent = 0.0
                
                # Get memory usage
                try:
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    self.peak_memory = max(self.peak_memory, memory_mb)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    memory_mb = 0.0
                
                # Get system-wide info
                try:
                    system_cpu = psutil.cpu_percent()
                    system_memory = psutil.virtual_memory()
                except:
                    system_cpu = 0.0
                    system_memory = None
                
                sample = {
                    'timestamp': current_time - start_time,
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_mb,
                    'system_cpu_percent': system_cpu,
                    'system_memory_percent': system_memory.percent if system_memory else 0,
                    'threads': self.process.num_threads()
                }
                
                self.samples.append(sample)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(self.sample_interval)
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a function call"""
        result = None
        error = None
        
        # Start monitoring
        self.start_monitoring()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = str(e)
            raise
        finally:
            # Stop monitoring
            end_time = time.time()
            profile_result = self.stop_monitoring()
            
            # Update duration with actual execution time
            profile_result.duration = end_time - start_time
            
            if error:
                profile_result.success = False
                profile_result.error = error
            
            return {
                'result': result,
                'profile': profile_result,
                'execution_time': profile_result.duration
            }
    
    def profile_command(self, command: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Profile system command execution"""
        import subprocess
        
        # Start monitoring
        self.start_monitoring()
        start_time = time.time()
        result = None
        success = False
        stdout = ""
        stderr = ""
        error = None
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            error = None
            
        except subprocess.TimeoutExpired as e:
            success = False
            stdout = e.stdout if e.stdout else ""
            stderr = e.stderr if e.stderr else ""
            error = "Command timed out"
            
        except Exception as e:
            success = False
            stdout = ""
            stderr = ""
            error = str(e)
        
        finally:
            # Stop monitoring
            end_time = time.time()
            profile_result = self.stop_monitoring()
            
            # Update duration
            profile_result.duration = end_time - start_time
            
            if not success:
                profile_result.success = False
                profile_result.error = error
            
            returncode = result.returncode if result else -1
            return {
                'command': ' '.join(command),
                'success': success,
                'stdout': stdout,
                'stderr': stderr,
                'returncode': returncode,
                'profile': profile_result
            }
    
    def get_system_snapshot(self) -> Dict[str, Any]:
        """Get current system snapshot"""
        try:
            return {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('.')._asdict(),
                'process': {
                    'cpu_percent': self.process.cpu_percent(),
                    'memory_mb': self.process.memory_info().rss / (1024 * 1024),
                    'num_threads': self.process.num_threads(),
                    'create_time': self.process.create_time()
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def save_profile_data(self, profile_result: ProfileResult, filepath: Path):
        """Save profile data to file"""
        data = {
            'summary': {
                'duration': profile_result.duration,
                'cpu_percent': profile_result.cpu_percent,
                'memory_mb': profile_result.memory_mb,
                'peak_memory_mb': profile_result.peak_memory_mb,
                'success': profile_result.success,
                'error': profile_result.error
            },
            'samples': profile_result.samples
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def compare_profiles(self, profile1: ProfileResult, profile2: ProfileResult) -> Dict[str, Any]:
        """Compare two profile results"""
        return {
            'duration_ratio': profile2.duration / profile1.duration if profile1.duration > 0 else 0,
            'cpu_ratio': profile2.cpu_percent / profile1.cpu_percent if profile1.cpu_percent > 0 else 0,
            'memory_ratio': profile2.memory_mb / profile1.memory_mb if profile1.memory_mb > 0 else 0,
            'peak_memory_ratio': profile2.peak_memory_mb / profile1.peak_memory_mb if profile1.peak_memory_mb > 0 else 0,
            'profile1_better_cpu': profile1.cpu_percent < profile2.cpu_percent,
            'profile1_better_memory': profile1.memory_mb < profile2.memory_mb,
            'profile1_better_duration': profile1.duration < profile2.duration
        }


if __name__ == '__main__':
    # Test the profiler
    def test_function():
        """Test function for profiling"""
        total = 0
        for i in range(1000000):
            total += i * i
        return total
    
    profiler = Profiler(sample_interval=0.05)
    
    print("Profiling test function...")
    result = profiler.profile_function(test_function)
    
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"CPU usage: {result['profile'].cpu_percent:.1f}%")
    print(f"Memory usage: {result['profile'].memory_mb:.1f}MB")
    print(f"Peak memory: {result['profile'].peak_memory_mb:.1f}MB")
    
    # Save profile data
    profile_file = Path('test_profile.json')
    profiler.save_profile_data(result['profile'], profile_file)
    print(f"Profile data saved to {profile_file}")