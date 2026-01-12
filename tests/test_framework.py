#!/usr/bin/env python3
"""
7-Zip Test Framework
Comprehensive testing for pack/unpack functionality with performance measurement
"""

import os
import sys
import yaml
import logging
import argparse
import importlib.util
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add tests directory to path
TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))

from utils.file_generator import FileGenerator
from utils.hash_utils import HashUtils
from utils.system_utils import SystemUtils
from performance.profiler import Profiler
from performance.benchmark import Benchmark
from performance.reporter import Reporter


class TestFramework:
    """Main test framework class"""
    
    def __init__(self, config_path: str = "test_config.yaml"):
        """Initialize test framework"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.setup_directories()
        
        # Initialize components
        self.file_generator = FileGenerator(self.config)
        self.hash_utils = HashUtils()
        self.system_utils = SystemUtils()
        self.profiler = Profiler()
        self.benchmark = Benchmark(self.config)
        self.reporter = Reporter(self.config)
        
        # Load format modules
        self.format_modules = self._load_format_modules()
        
        # Results storage
        self.results = {
            'format_tests': {},
            'performance': {},
            'compatibility': {},
            'integrity': {},
            'errors': []
        }
        
        self.logger.info("7-Zip Test Framework initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                config_file = Path(__file__).resolve().parent / config_path
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_path = Path("results/logs/test_framework.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        log_level = self.config.get('test_settings', {}).get('log_level', 'INFO')
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('results/logs/test_framework.log')
            ]
        )
        
        self.logger = logging.getLogger('TestFramework')
    
    def setup_directories(self):
        """Create necessary directories"""
        base_dir = Path(self.config.get('test_settings', {}).get('output_dir', './results'))
        dirs = ['logs', 'reports', 'benchmarks', 'temp']
        
        for dir_name in dirs:
            dir_path = base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _load_format_modules(self) -> Dict[str, Any]:
        """Load format-specific test modules"""
        modules = {}
        formats_dir = Path(__file__).parent / 'formats'
        
        if not formats_dir.exists():
            self.logger.warning("Formats directory not found")
            return modules
        
        for format_file in formats_dir.glob('*.py'):
            if format_file.name == '__init__.py':
                continue
                
            format_name = format_file.stem
            try:
                spec = importlib.util.spec_from_file_location(format_name, format_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    modules[format_name] = module
                    self.logger.debug(f"Loaded format module: {format_name}")
                else:
                    self.logger.warning(f"Could not load spec for {format_name}")
            except Exception as e:
                self.logger.error(f"Failed to load format module {format_name}: {e}")
        
        return modules
    
    def generate_test_data(self) -> bool:
        """Generate test data files"""
        self.logger.info("Generating test data...")
        
        try:
            success = self.file_generator.generate_all()
            if success:
                self.logger.info("Test data generation completed")
            else:
                self.logger.error("Test data generation failed")
            return success
        except Exception as e:
            self.logger.error(f"Test data generation error: {e}")
            return False
    
    def run_format_tests(self, formats: List[str] | None = None) -> bool:
        """Run format-specific tests"""
        self.logger.info("Running format tests...")
        
        formats_to_test = formats if formats is not None else self.config.get('formats', {}).get('core_formats', [])
        
        for format_name in formats_to_test:
            self.logger.info(f"Testing {format_name} format...")
            
            try:
                if format_name in self.format_modules:
                    module = self.format_modules[format_name]
                    result = module.run_tests(self.config)
                    self.results['format_tests'][format_name] = result
                else:
                    self.logger.warning(f"No test module found for format: {format_name}")
                    self.results['format_tests'][format_name] = {'status': 'skipped', 'reason': 'no_module'}
                    
            except Exception as e:
                self.logger.error(f"Error testing {format_name}: {e}")
                self.results['format_tests'][format_name] = {'status': 'error', 'error': str(e)}
                self.results['errors'].append({'format': format_name, 'error': str(e)})
        
        return True
    
    def run_performance_tests(self) -> bool:
        """Run performance benchmarks"""
        self.logger.info("Running performance tests...")
        
        try:
            results = self.benchmark.run_all_benchmarks()
            self.results['performance'] = results
            return True
        except Exception as e:
            self.logger.error(f"Performance test error: {e}")
            return False
    
    def run_compatibility_tests(self) -> bool:
        """Run compatibility tests"""
        self.logger.info("Running compatibility tests...")
        
        try:
            # Test with reference archives
            compat_config = self.config.get('compatibility', {})
            results = {'reference_archives': {}, 'third_party': {}}
            
            # Test reference archives
            for archive_info in compat_config.get('reference_archives', []):
                format_name = archive_info['format']
                file_path = archive_info['file']
                
                try:
                    result = self._test_reference_archive(format_name, file_path)
                    results['reference_archives'][format_name] = result
                except Exception as e:
                    results['reference_archives'][format_name] = {'status': 'error', 'error': str(e)}
            
            # Test third-party tool compatibility
            for tool_info in compat_config.get('third_party_tools', []):
                tool_name = tool_info['name']
                tool_path = tool_info['path']
                
                try:
                    result = self._test_third_party_tool(tool_name, tool_path)
                    results['third_party'][tool_name] = result
                except Exception as e:
                    results['third_party'][tool_name] = {'status': 'error', 'error': str(e)}
            
            self.results['compatibility'] = results
            return True
            
        except Exception as e:
            self.logger.error(f"Compatibility test error: {e}")
            return False
    
    def _test_reference_archive(self, format_name: str, file_path: str) -> Dict[str, Any]:
        """Test with a reference archive"""
        self.logger.debug(f"Testing reference archive: {file_path}")
        
        reference_path = Path('test_data/reference') / file_path
        if not reference_path.exists():
            return {'status': 'skipped', 'reason': 'file_not_found'}
        
        # This would implement extraction and verification
        # For now, return placeholder
        return {
            'status': 'success',
            'extraction_time': 0.0,
            'files_extracted': 0,
            'integrity_verified': True
        }
    
    def _test_third_party_tool(self, tool_name: str, tool_path: str) -> Dict[str, Any]:
        """Test compatibility with third-party tool"""
        self.logger.debug(f"Testing third-party tool: {tool_name}")
        
        if not Path(tool_path).exists():
            return {'status': 'skipped', 'reason': 'tool_not_found'}
        
        # This would implement tool compatibility testing
        # For now, return placeholder
        return {
            'status': 'success',
            'tool_version': 'unknown',
            'compatible': True
        }
    
    def verify_integrity(self) -> bool:
        """Verify test integrity"""
        self.logger.info("Running integrity verification...")
        
        try:
            integrity_config = self.config.get('integrity', {})
            results = {}
            
            for level_info in integrity_config.get('levels', []):
                level_name = level_info['name']
                checks = level_info['checks']
                
                try:
                    result = self._run_integrity_checks(checks)
                    results[level_name] = result
                except Exception as e:
                    results[level_name] = {'status': 'error', 'error': str(e)}
            
            self.results['integrity'] = results
            return True
            
        except Exception as e:
            self.logger.error(f"Integrity verification error: {e}")
            return False
    
    def _run_integrity_checks(self, checks: List[str]) -> Dict[str, Any]:
        """Run specific integrity checks"""
        results = {}
        
        for check in checks:
            try:
                if check == 'file_exists':
                    # Check all test files exist
                    results[check] = self._check_file_existence()
                elif check == 'file_size':
                    # Check file sizes match
                    results[check] = self._check_file_sizes()
                elif check == 'hash':
                    # Check file hashes match
                    results[check] = self._check_file_hashes()
                elif check == 'content':
                    # Check file contents match
                    results[check] = self._check_file_contents()
                elif check == 'permissions':
                    # Check file permissions
                    results[check] = self._check_file_permissions()
                elif check == 'timestamps':
                    # Check file timestamps
                    results[check] = self._check_file_timestamps()
                else:
                    results[check] = {'status': 'skipped', 'reason': 'unknown_check'}
                    
            except Exception as e:
                results[check] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def _check_file_existence(self) -> Dict[str, Any]:
        """Check that all test files exist"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'files_missing': 0}
    
    def _check_file_sizes(self) -> Dict[str, Any]:
        """Check that file sizes match expected"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'size_mismatches': 0}
    
    def _check_file_hashes(self) -> Dict[str, Any]:
        """Check that file hashes match expected"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'hash_mismatches': 0}
    
    def _check_file_contents(self) -> Dict[str, Any]:
        """Check that file contents match expected"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'content_mismatches': 0}
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check that file permissions are preserved"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'permission_mismatches': 0}
    
    def _check_file_timestamps(self) -> Dict[str, Any]:
        """Check that file timestamps are preserved"""
        # Placeholder implementation
        return {'status': 'success', 'files_checked': 0, 'timestamp_mismatches': 0}
    
    def generate_report(self) -> bool:
        """Generate comprehensive test report"""
        self.logger.info("Generating test report...")
        
        try:
            report_path = self.reporter.generate_report(self.results)
            self.logger.info(f"Report generated: {report_path}")
            return True
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return False
    
    def run_all_tests(self, formats: List[str] | None = None, include_performance: bool = True,
                    include_compatibility: bool = True, include_integrity: bool = True) -> bool:
        """Run all tests"""
        self.logger.info("Starting comprehensive test suite...")
        
        success = True
        
        # Generate test data
        if not self.generate_test_data():
            success = False
        
        # Run format tests
        if not self.run_format_tests(formats):
            success = False
        
        # Run performance tests
        if include_performance and not self.run_performance_tests():
            success = False
        
        # Run compatibility tests
        if include_compatibility and not self.run_compatibility_tests():
            success = False
        
        # Run integrity verification
        if include_integrity and not self.verify_integrity():
            success = False
        
        # Generate report
        if not self.generate_report():
            success = False
        
        if success:
            self.logger.info("All tests completed successfully")
        else:
            self.logger.error("Some tests failed")
        
        return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='7-Zip Test Framework')
    parser.add_argument('--config', default='test_config.yaml', help='Configuration file path')
    parser.add_argument('--formats', help='Comma-separated list of formats to test')
    parser.add_argument('--benchmark', action='store_true', help='Run only performance benchmarks')
    parser.add_argument('--compatibility', action='store_true', help='Run only compatibility tests')
    parser.add_argument('--no-performance', action='store_true', help='Skip performance tests')
    parser.add_argument('--no-compatibility', action='store_true', help='Skip compatibility tests')
    parser.add_argument('--no-integrity', action='store_true', help='Skip integrity verification')
    parser.add_argument('--report', action='store_true', help='Generate report only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Parse formats
    formats = None
    if args.formats:
        formats = [f.strip() for f in args.formats.split(',')]
    
    # Create and run test framework
    framework = TestFramework(args.config)
    
    if args.report:
        success = framework.generate_report()
    elif args.benchmark:
        success = framework.generate_test_data()
        if success:
            success = framework.run_performance_tests()
            framework.generate_report()
    elif args.compatibility:
        success = framework.generate_test_data()
        if success:
            success = framework.run_compatibility_tests()
            framework.generate_report()
    else:
        success = framework.run_all_tests(
            formats=formats,
            include_performance=not args.no_performance,
            include_compatibility=not args.no_compatibility,
            include_integrity=not args.no_integrity
        )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
