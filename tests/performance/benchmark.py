#!/usr/bin/env python3
"""
Benchmark Suite for 7-Zip Performance Testing
"""

import time
import statistics
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import yaml

TESTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTS_DIR))

from performance.profiler import Profiler
from utils.system_utils import SystemUtils


@dataclass
class BenchmarkResult:
    """Result of a single benchmark"""
    format_name: str
    method: str
    level: int
    threads: int
    operation: str  # 'compress' or 'decompress'
    file_size: int
    archive_size: int
    compression_ratio: float
    duration: float
    throughput: float  # MB/s
    cpu_percent: float
    memory_mb: float
    success: bool
    error: Optional[str] = None


class Benchmark:
    """Performance benchmarking for compression formats"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.profiler = Profiler()
        self.temp_dir = Path(config.get('test_settings', {}).get('temp_dir', '/tmp/7z_bench'))
        self.test_data_dir = Path('test_data')
        self.sevenz_exec = self._find_7z_executable()
        
        if not self.sevenz_exec:
            raise RuntimeError("7-Zip executable not found")
    
    def _find_7z_executable(self) -> Optional[Path]:
        """Find 7-Zip executable"""
        sys_utils = SystemUtils()
        
        # Try different executable names
        names = ['7z', '7zz', '7za']
        
        for name in names:
            exec_path = sys_utils.find_executable(name)
            if exec_path:
                return exec_path
        
        # Check common paths
        common_paths = [
            '/usr/bin/7z',
            '/usr/local/bin/7z',
            '/usr/bin/7zz',
            './CPP/7zip/Bundles/Alone/7z',
            './CPP/7zip/Bundles/Alone7z/7z'
        ]
        
        for path_str in common_paths:
            path = Path(path_str)
            if path.exists():
                return path
        
        return None
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        print("Starting comprehensive benchmark suite...")
        
        results = {
            'metadata': self._get_benchmark_metadata(),
            'compression_benchmarks': [],
            'decompression_benchmarks': [],
            'summary': {}
        }
        
        # Get test files
        test_files = self._get_test_files()
        if not test_files:
            print("No test files found!")
            return results
        
        # Run compression benchmarks
        compression_results = self._run_compression_benchmarks(test_files)
        results['compression_benchmarks'] = compression_results
        
        # Run decompression benchmarks  
        decompression_results = self._run_decompression_benchmarks(compression_results)
        results['decompression_benchmarks'] = decompression_results
        
        # Generate summary
        results['summary'] = self._generate_summary(compression_results, decompression_results)
        
        print(f"Benchmark completed: {len(compression_results)} compression, {len(decompression_results)} decompression tests")
        return results
    
    def _get_benchmark_metadata(self) -> Dict[str, Any]:
        """Get benchmark metadata"""
        sys_utils = SystemUtils()
        
        return {
            'timestamp': time.time(),
            '7z_version': self._get_7z_version(),
            'system_info': sys_utils.get_system_info(),
            'benchmark_config': {
                'iterations': self.config.get('performance', {}).get('iterations', 3),
                'timeout': self.config.get('performance', {}).get('benchmark_duration', 60)
            }
        }
    
    def _get_7z_version(self) -> str:
        """Get 7-Zip version"""
        if not self.sevenz_exec:
            return "unknown"
        
        sys_utils = SystemUtils()
        result = sys_utils.run_command([str(self.sevenz_exec)])
        
        if result['success'] and result['stdout']:
            # Extract version from output
            for line in result['stdout'].split('\n'):
                if '7-Zip' in line:
                    return line.strip()
        
        return "unknown"
    
    def _get_test_files(self) -> List[Path]:
        """Get test files for benchmarking"""
        files = []
        max_file_size_config = self.config.get('performance', {}).get('max_file_size', 100 * 1024 * 1024)
        max_file_size = self._parse_size(max_file_size_config)
        max_files = self.config.get('performance', {}).get('max_files', 30)
        
        # Binary files
        binary_dir = self.test_data_dir / 'binary'
        if binary_dir.exists():
            files.extend(list(binary_dir.glob('*.bin')))
        
        # Text files
        text_dir = self.test_data_dir / 'text'
        if text_dir.exists():
            files.extend(text_dir.glob('*.txt'))
            files.extend(text_dir.glob('*.json'))
            files.extend(text_dir.glob('*.csv'))
        
        # Mixed content directories
        mixed_dir = self.test_data_dir / 'mixed'
        if mixed_dir.exists():
            files.extend([path for path in mixed_dir.glob('**/*') if path.is_file()])
        
        # Filter for files only and reasonable size
        test_files = []
        for file_path in files:
            if file_path.is_file() and file_path.stat().st_size > 0:
                if file_path.stat().st_size <= max_file_size:
                    test_files.append(file_path)
        
        test_files = sorted(test_files, key=lambda f: f.stat().st_size)
        return test_files[:max_files]

    def _get_methods_for_format(self, format_name: str, methods: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Get allowed methods for a format"""
        allowed_methods = {
            '7z': ['lzma2', 'lzma', 'ppmd', 'bzip2'],
            'zip': ['deflate', 'deflate64', 'bzip2', 'lzma', 'ppmd'],
            'gz': ['deflate'],
            'bz2': ['bzip2'],
            'xz': ['lzma2'],
            'cab': ['lzma', 'lzx'],
            'tar': []
        }
        
        format_methods = {}
        for method_name in allowed_methods.get(format_name, []):
            method_configs = methods.get(method_name)
            if method_configs:
                format_methods[method_name] = method_configs
        
        if format_name in ['gz', 'bz2'] and not format_methods:
            default_method = 'deflate' if format_name == 'gz' else 'bzip2'
            format_methods[default_method] = [{'level': 5, 'threads': 1}]
        
        return format_methods

    def _parse_size(self, size_value: int | str) -> int:
        """Parse size string like '100MB' to bytes"""
        if isinstance(size_value, int):
            return size_value
        
        size_str = str(size_value).upper().strip()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        if size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        if size_str.endswith('B'):
            return int(size_str[:-1])
        return int(size_str)
    
    def _run_compression_benchmarks(self, test_files: List[Path]) -> List[BenchmarkResult]:
        """Run compression benchmarks"""
        results = []
        
        formats_to_test = self.config.get('formats', {}).get('core_formats', ['7z', 'zip', 'gz'])
        methods = self.config.get('compression_methods', {})
        iterations = self.config.get('performance', {}).get('iterations', 1)
        
        for format_name in formats_to_test:
            methods_to_test = self._get_methods_for_format(format_name, methods)
            if not methods_to_test:
                print(f"Skipping methods for format: {format_name}")
                continue
            
            for method_name, method_configs in methods_to_test.items():
                for method_config in method_configs:
                    level = method_config.get('level', 5)
                    threads = method_config.get('threads', 1)
                    
                    print(f"Testing {format_name}/{method_name} level={level} threads={threads}")
                    
                    for test_file in test_files:
                        for iteration in range(iterations):
                            result = self._benchmark_compression(
                                test_file, format_name, method_name, level, threads
                            )
                            
                            if result.success:
                                results.append(result)
                                print(f"  {test_file.name}: {result.throughput:.1f} MB/s, ratio={result.compression_ratio:.3f}")
                            else:
                                print(f"  {test_file.name}: FAILED - {result.error}")
        
        return results
    
    def _run_decompression_benchmarks(self, compression_results: List[BenchmarkResult]) -> List[BenchmarkResult]:
        """Run decompression benchmarks"""
        results = []
        
        # Group compression results by archive
        archives = {}
        for result in compression_results:
            if result.success:
                archive_path = Path(f"temp_{result.format_name}_{result.method}_l{result.level}.archive")
                archives.setdefault((result.format_name, result.method, result.level, result.threads), []).append(result)
        
        # Benchmark decompression for each unique archive configuration
        for (format_name, method, level, threads), comp_results in archives.items():
            # Use the first successful compression result
            comp_result = comp_results[0]
            
            print(f"Testing decompression: {format_name}/{method} level={level}")
            
            for iteration in range(self.config.get('performance', {}).get('iterations', 1)):
                result = self._benchmark_decompression(comp_result)
                
                if result.success:
                    results.append(result)
                    print(f"  Decompression: {result.throughput:.1f} MB/s")
                else:
                    print(f"  Decompression: FAILED - {result.error}")
        
        return results
    
    def _benchmark_compression(self, input_file: Path, format_name: str, 
                           method: str, level: int, threads: int) -> BenchmarkResult:
        """Benchmark compression of a single file"""
        
        # Create temporary archive name
        temp_archive = self.temp_dir / f"bench_{int(time.time())}.{format_name}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build 7z command
            cmd = [str(self.sevenz_exec)]
            
            # Add format and method options
            if format_name == '7z':
                cmd.extend(['-t7z', f'-m0={method}'])
            elif format_name == 'zip':
                cmd.extend(['-tzip', f'-m0={method}'])
            elif format_name == 'gz':
                cmd.extend(['-tgzip', f'-m0={method}'])
            elif format_name == 'bz2':
                cmd.extend(['-tbzip2', f'-m0={method}'])
            else:
                cmd.extend([f'-t{format_name}'])
            
            # Add compression level
            cmd.extend([f'-mx={level}'])
            
            # Add threads
            if threads > 1:
                cmd.extend([f'-mmt{threads}'])
            
            # Add output and input
            cmd.extend(['a', str(temp_archive), str(input_file)])
            
            # Run benchmark with profiling
            profile_result = self.profiler.profile_command(cmd)
            
            if not profile_result['success']:
                error = profile_result.get('error') or profile_result.get('stderr') or 'Command failed'
                return BenchmarkResult(
                    format_name=format_name, method=method, level=level, threads=threads,
                    operation='compress', file_size=input_file.stat().st_size,
                    archive_size=0, compression_ratio=0.0, duration=0.0,
                    throughput=0.0, cpu_percent=0.0, memory_mb=0.0,
                    success=False, error=error
                )
            
            # Get archive size
            archive_size = temp_archive.stat().st_size if temp_archive.exists() else 0
            compression_ratio = archive_size / input_file.stat().st_size if input_file.stat().st_size > 0 else 0
            
            profile = profile_result['profile']
            throughput = input_file.stat().st_size / (1024 * 1024) / profile.duration if profile.duration > 0 else 0
            
            return BenchmarkResult(
                format_name=format_name, method=method, level=level, threads=threads,
                operation='compress', file_size=input_file.stat().st_size,
                archive_size=archive_size, compression_ratio=compression_ratio,
                duration=profile.duration, throughput=throughput,
                cpu_percent=profile.cpu_percent, memory_mb=profile.memory_mb,
                success=True
            )
            
        except Exception as e:
            return BenchmarkResult(
                format_name=format_name, method=method, level=level, threads=threads,
                operation='compress', file_size=input_file.stat().st_size,
                archive_size=0, compression_ratio=0.0, duration=0.0,
                throughput=0.0, cpu_percent=0.0, memory_mb=0.0,
                success=False, error=str(e)
            )
        
        finally:
            # Cleanup
            if temp_archive.exists():
                temp_archive.unlink()
    
    def _benchmark_decompression(self, compression_result: BenchmarkResult) -> BenchmarkResult:
        """Benchmark decompression using compression result"""
        
        # Create temporary archive and test output
        temp_archive = self.temp_dir / f"decomp_bench.{compression_result.format_name}"
        temp_output = self.temp_dir / "decomp_output"
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        temp_output.mkdir(exist_ok=True)
        
        try:
            # Recreate archive (since we cleaned it up)
            # For now, assume we have the archive or use a placeholder
            if not temp_archive.exists():
                # Create a dummy file for testing
                temp_archive.write_bytes(b'dummy archive data')
            
            # Build decompression command
            cmd = [str(self.sevenz_exec), 'x', str(temp_archive), f'-o{temp_output}', '-y']
            
            # Run with profiling
            profile_result = self.profiler.profile_command(cmd)
            
            if not profile_result['success']:
                return BenchmarkResult(
                    format_name=compression_result.format_name,
                    method=compression_result.method,
                    level=compression_result.level, threads=compression_result.threads,
                    operation='decompress', file_size=compression_result.archive_size,
                    archive_size=0, compression_ratio=0.0, duration=0.0,
                    throughput=0.0, cpu_percent=0.0, memory_mb=0.0,
                    success=False, error=profile_result.get('error', 'Decompression failed')
                )
            
            profile = profile_result['profile']
            throughput = compression_result.archive_size / (1024 * 1024) / profile.duration if profile.duration > 0 else 0
            
            return BenchmarkResult(
                format_name=compression_result.format_name,
                method=compression_result.method,
                level=compression_result.level, threads=compression_result.threads,
                operation='decompress', file_size=compression_result.archive_size,
                archive_size=compression_result.archive_size,
                compression_ratio=1.0 / compression_result.compression_ratio if compression_result.compression_ratio > 0 else 0,
                duration=profile.duration, throughput=throughput,
                cpu_percent=profile.cpu_percent, memory_mb=profile.memory_mb,
                success=True
            )
            
        except Exception as e:
            return BenchmarkResult(
                format_name=compression_result.format_name,
                method=compression_result.method,
                level=compression_result.level, threads=compression_result.threads,
                operation='decompress', file_size=compression_result.archive_size,
                archive_size=0, compression_ratio=0.0, duration=0.0,
                throughput=0.0, cpu_percent=0.0, memory_mb=0.0,
                success=False, error=str(e)
            )
        
        finally:
            # Cleanup
            if temp_archive.exists():
                temp_archive.unlink()
            if temp_output.exists():
                import shutil
                shutil.rmtree(temp_output)
    
    def _generate_summary(self, compression_results: List[BenchmarkResult], 
                        decompression_results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        # Group by format and method
        comp_by_format = {}
        decomp_by_format = {}
        
        for result in compression_results:
            if result.success:
                key = f"{result.format_name}_{result.method}"
                comp_by_format.setdefault(key, []).append(result)
        
        for result in decompression_results:
            if result.success:
                key = f"{result.format_name}_{result.method}"
                decomp_by_format.setdefault(key, []).append(result)
        
        # Calculate statistics
        summary = {
            'compression': {},
            'decompression': {},
            'best_compression_ratio': {},
            'fastest_compression': {},
            'fastest_decompression': {}
        }
        
        # Compression summary
        for key, results in comp_by_format.items():
            throughputs = [r.throughput for r in results]
            ratios = [r.compression_ratio for r in results]
            durations = [r.duration for r in results]
            
            summary['compression'][key] = {
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs),
                'avg_compression_ratio': statistics.mean(ratios),
                'best_compression_ratio': min(ratios),
                'avg_duration': statistics.mean(durations),
                'test_count': len(results)
            }
        
        # Decompression summary  
        for key, results in decomp_by_format.items():
            throughputs = [r.throughput for r in results]
            durations = [r.duration for r in results]
            
            summary['decompression'][key] = {
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs),
                'avg_duration': statistics.mean(durations),
                'test_count': len(results)
            }
        
        # Find best performers
        all_comp_results = [r for results in comp_by_format.values() for r in results]
        if all_comp_results:
            best_ratio = min(all_comp_results, key=lambda r: r.compression_ratio)
            fastest_comp = max(all_comp_results, key=lambda r: r.throughput)
            
            summary['best_compression_ratio'] = {
                'format': f"{best_ratio.format_name}_{best_ratio.method}",
                'level': best_ratio.level,
                'ratio': best_ratio.compression_ratio
            }
            
            summary['fastest_compression'] = {
                'format': f"{fastest_comp.format_name}_{fastest_comp.method}",
                'level': fastest_comp.level,
                'throughput': fastest_comp.throughput
            }
        
        # Find fastest decompression
        all_decomp_results = [r for results in decomp_by_format.values() for r in results]
        if all_decomp_results:
            fastest_decomp = max(all_decomp_results, key=lambda r: r.throughput)
            
            summary['fastest_decompression'] = {
                'format': f"{fastest_decomp.format_name}_{fastest_decomp.method}",
                'throughput': fastest_decomp.throughput
            }
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filepath: Path):
        """Save benchmark results to file"""
        with open(filepath, 'w') as f:
            # Convert BenchmarkResult objects to dicts
            results['compression_benchmarks'] = [
                {
                    'format_name': r.format_name,
                    'method': r.method,
                    'level': r.level,
                    'threads': r.threads,
                    'operation': r.operation,
                    'file_size': r.file_size,
                    'archive_size': r.archive_size,
                    'compression_ratio': r.compression_ratio,
                    'duration': r.duration,
                    'throughput': r.throughput,
                    'cpu_percent': r.cpu_percent,
                    'memory_mb': r.memory_mb,
                    'success': r.success,
                    'error': r.error
                } for r in results['compression_benchmarks']
            ]
            
            results['decompression_benchmarks'] = [
                {
                    'format_name': r.format_name,
                    'method': r.method,
                    'level': r.level,
                    'threads': r.threads,
                    'operation': r.operation,
                    'file_size': r.file_size,
                    'archive_size': r.archive_size,
                    'compression_ratio': r.compression_ratio,
                    'duration': r.duration,
                    'throughput': r.throughput,
                    'cpu_percent': r.cpu_percent,
                    'memory_mb': r.memory_mb,
                    'success': r.success,
                    'error': r.error
                } for r in results['decompression_benchmarks']
            ]
            
            json.dump(results, f, indent=2)
        
        print(f"Benchmark results saved to {filepath}")


if __name__ == '__main__':
    # Test benchmark module
    config = {
        'test_settings': {'temp_dir': '/tmp/7z_test'},
        'formats': {'core_formats': ['7z', 'zip']},
        'compression_methods': {
            'lzma2': [{'level': 5, 'threads': 1}],
            'deflate': [{'level': 6, 'threads': 1}]
        },
        'performance': {'iterations': 1}
    }
    
    benchmark = Benchmark(config)
    results = benchmark.run_all_benchmarks()
    benchmark.save_results(results, Path('benchmark_results.json'))
    
    print("Benchmark completed successfully!")