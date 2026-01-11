#!/usr/bin/env python3
"""
Report Generator for Test Results
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import statistics


class Reporter:
    """Generates comprehensive test reports"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get('test_settings', {}).get('output_dir', './results'))
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, results: Dict[str, Any]) -> Path:
        """Generate comprehensive test report"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Generate different report formats
        report_files = []
        
        # HTML report
        html_file = self.reports_dir / f'7z_test_report_{timestamp}.html'
        self._generate_html_report(results, html_file)
        report_files.append(html_file)
        
        # JSON report
        json_file = self.reports_dir / f'7z_test_report_{timestamp}.json'
        self._generate_json_report(results, json_file)
        report_files.append(json_file)
        
        # CSV report for performance data
        csv_file = self.reports_dir / f'7z_performance_{timestamp}.csv'
        self._generate_csv_report(results, csv_file)
        report_files.append(csv_file)
        
        # Text summary
        txt_file = self.reports_dir / f'7z_summary_{timestamp}.txt'
        self._generate_text_summary(results, txt_file)
        report_files.append(txt_file)
        
        print(f"Reports generated:")
        for report_file in report_files:
            print(f"  {report_file}")
        
        return html_file  # Return HTML as primary report
    
    def _generate_html_report(self, results: Dict[str, Any], output_path: Path):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>7-Zip Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 4px solid #007cba; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>7-Zip Comprehensive Test Report</h1>
        <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    {self._generate_summary_section(results)}
    {self._generate_format_tests_section(results)}
    {self._generate_performance_section(results)}
    {self._generate_integrity_section(results)}
    {self._generate_compatibility_section(results)}
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_summary_section(self, results: Dict[str, Any]) -> str:
        """Generate summary section"""
        format_tests = results.get('format_tests', {})
        performance = results.get('performance', {})
        integrity = results.get('integrity', {})
        compatibility = results.get('compatibility', {})
        
        # Calculate statistics
        total_format_tests = len(format_tests)
        successful_formats = len([f for f in format_tests.values() if f.get('status') == 'success'])
        
        performance_tests = performance.get('compression_benchmarks', [])
        successful_performance = len([p for p in performance_tests if p.get('success', False)])
        
        html = f"""
    <div class="section">
        <h2>Test Summary</h2>
        <div class="metric">
            <strong>Format Tests:</strong> {successful_formats}/{total_format_tests} successful
        </div>
        <div class="metric">
            <strong>Performance Tests:</strong> {successful_performance}/{len(performance_tests)} successful
        </div>
        <div class="metric">
            <strong>Total Errors:</strong> {len(results.get('errors', []))}
        </div>
    </div>
        """
        
        return html
    
    def _generate_format_tests_section(self, results: Dict[str, Any]) -> str:
        """Generate format tests section"""
        format_tests = results.get('format_tests', {})
        
        if not format_tests:
            return ""
        
        html = '<div class="section"><h2>Format Tests</h2><table>'
        html += '<tr><th>Format</th><th>Status</th><th>Details</th></tr>'
        
        for format_name, result in format_tests.items():
            status = result.get('status', 'unknown')
            status_class = status if status in ['success', 'error', 'skipped'] else 'warning'
            
            html += f'<tr>'
            html += f'<td>{format_name}</td>'
            html += f'<td class="{status_class}">{status}</td>'
            html += f'<td>{result.get("reason", result.get("error", ""))}</td>'
            html += '</tr>'
        
        html += '</table></div>'
        
        return html
    
    def _generate_performance_section(self, results: Dict[str, Any]) -> str:
        """Generate performance section"""
        performance = results.get('performance', {})
        summary = performance.get('summary', {})
        
        if not summary:
            return ""
        
        html = '<div class="section"><h2>Performance Results</h2>'
        
        # Best performers
        if 'best_compression_ratio' in summary:
            best = summary['best_compression_ratio']
            html += f'''
        <div class="metric">
            <strong>Best Compression:</strong> {best['format']} (Level {best.get('level', 'N/A')})
            - Ratio: {best['ratio']:.3f}
        </div>
            '''
        
        if 'fastest_compression' in summary:
            fastest = summary['fastest_compression']
            html += f'''
        <div class="metric">
            <strong>Fastest Compression:</strong> {fastest['format']} (Level {fastest.get('level', 'N/A')})
            - {fastest['throughput']:.1f} MB/s
        </div>
            '''
        
        # Performance comparison table
        if 'compression' in summary:
            html += '<h3>Compression Performance</h3><table>'
            html += '<tr><th>Format</th><th>Avg Throughput (MB/s)</th><th>Best Ratio</th><th>Avg Duration (s)</th></tr>'
            
            for key, stats in summary['compression'].items():
                html += f'<tr>'
                html += f'<td>{key}</td>'
                html += f'<td>{stats["avg_throughput"]:.1f}</td>'
                html += f'<td>{stats["best_compression_ratio"]:.3f}</td>'
                html += f'<td>{stats["avg_duration"]:.2f}</td>'
                html += '</tr>'
            
            html += '</table>'
        
        html += '</div>'
        
        return html
    
    def _generate_integrity_section(self, results: Dict[str, Any]) -> str:
        """Generate integrity verification section"""
        integrity = results.get('integrity', {})
        
        if not integrity:
            return ""
        
        html = '<div class="section"><h2>Integrity Verification</h2><table>'
        html += '<tr><th>Level</th><th>Status</th><th>Details</th></tr>'
        
        for level_name, result in integrity.items():
            status = result.get('status', 'unknown')
            status_class = 'success' if status == 'success' else 'error'
            
            html += f'<tr>'
            html += f'<td>{level_name}</td>'
            html += f'<td class="{status_class}">{status}</td>'
            html += f'<td>{str(result)}</td>'
            html += '</tr>'
        
        html += '</table></div>'
        
        return html
    
    def _generate_compatibility_section(self, results: Dict[str, Any]) -> str:
        """Generate compatibility section"""
        compatibility = results.get('compatibility', {})
        
        if not compatibility:
            return ""
        
        html = '<div class="section"><h2>Compatibility Tests</h2>'
        
        # Reference archives
        ref_archives = compatibility.get('reference_archives', {})
        if ref_archives:
            html += '<h3>Reference Archives</h3><table>'
            html += '<tr><th>Format</th><th>Status</th><th>Details</th></tr>'
            
            for format_name, result in ref_archives.items():
                status = result.get('status', 'unknown')
                status_class = 'success' if status == 'success' else 'error'
                
                html += f'<tr>'
                html += f'<td>{format_name}</td>'
                html += f'<td class="{status_class}">{status}</td>'
                html += f'<td>{str(result)}</td>'
                html += '</tr>'
            
            html += '</table>'
        
        # Third-party tools
        third_party = compatibility.get('third_party', {})
        if third_party:
            html += '<h3>Third-Party Compatibility</h3><table>'
            html += '<tr><th>Tool</th><th>Status</th><th>Details</th></tr>'
            
            for tool_name, result in third_party.items():
                status = result.get('status', 'unknown')
                status_class = 'success' if status == 'success' else 'error'
                
                html += f'<tr>'
                html += f'<td>{tool_name}</td>'
                html += f'<td class="{status_class}">{status}</td>'
                html += f'<td>{str(result)}</td>'
                html += '</tr>'
            
            html += '</table>'
        
        html += '</div>'
        
        return html
    
    def _generate_json_report(self, results: Dict[str, Any], output_path: Path):
        """Generate JSON report"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _generate_csv_report(self, results: Dict[str, Any], output_path: Path):
        """Generate CSV report for performance data"""
        performance = results.get('performance', {})
        compression_tests = performance.get('compression_benchmarks', [])
        
        if not compression_tests:
            return
        
        # CSV header
        csv_lines = [
            'Format,Method,Level,Threads,Operation,FileSize,ArchiveSize,CompressionRatio,Duration,Throughput,CPU,Memory,Success,Error'
        ]
        
        # Data rows
        for result in compression_tests:
            line = f'{result.get("format_name", "")},{result.get("method", "")},{result.get("level", "")},{result.get("threads", "")},{result.get("operation", "")},{result.get("file_size", 0)},{result.get("archive_size", 0)},{result.get("compression_ratio", 0):.6f},{result.get("duration", 0):.3f},{result.get("throughput", 0):.2f},{result.get("cpu_percent", 0):.1f},{result.get("memory_mb", 0):.2f},{result.get("success", False)},{result.get("error", "")}'
            csv_lines.append(line)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(csv_lines))
    
    def _generate_text_summary(self, results: Dict[str, Any], output_path: Path):
        """Generate text summary"""
        lines = [
            "7-Zip Test Report Summary",
            "=" * 50,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Format tests
        format_tests = results.get('format_tests', {})
        if format_tests:
            lines.append("Format Tests:")
            lines.append("-" * 20)
            
            for format_name, result in format_tests.items():
                status = result.get('status', 'unknown')
                lines.append(f"  {format_name:10s}: {status}")
                
                if status == 'error' and 'error' in result:
                    lines.append(f"    Error: {result['error']}")
            
            lines.append("")
        
        # Performance summary
        performance = results.get('performance', {})
        summary = performance.get('summary', {})
        if summary and 'compression' in summary:
            lines.append("Performance Summary:")
            lines.append("-" * 25)
            
            for key, stats in summary['compression'].items():
                lines.append(f"  {key:20s}:")
                lines.append(f"    Avg Throughput: {stats['avg_throughput']:.1f} MB/s")
                lines.append(f"    Best Ratio:     {stats['best_compression_ratio']:.3f}")
                lines.append(f"    Avg Duration:   {stats['avg_duration']:.2f} s")
            
            lines.append("")
        
        # Errors
        errors = results.get('errors', [])
        if errors:
            lines.append("Errors:")
            lines.append("-" * 10)
            
            for error in errors:
                lines.append(f"  {error}")
            
            lines.append("")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
    
    def generate_comparison_report(self, benchmark_files: List[Path], output_path: Path):
        """Generate comparison report from multiple benchmark files"""
        all_results = []
        
        for file_path in benchmark_files:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['source_file'] = str(file_path)
                    all_results.append(data)
        
        if not all_results:
            print("No valid benchmark files found")
            return
        
        # Generate comparison HTML
        html_content = self._generate_comparison_html(all_results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Comparison report generated: {output_path}")
    
    def _generate_comparison_html(self, all_results: List[Dict[str, Any]]) -> str:
        """Generate HTML comparison"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>7-Zip Performance Comparison</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .better {{ background-color: #d4edda; }}
        .worse {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <h1>7-Zip Performance Comparison</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <table>
        <tr>
            <th>Source</th>
            <th>Best Compression Ratio</th>
            <th>Fastest Compression</th>
            <th>Fastest Decompression</th>
        </tr>
        """
        
        for result in all_results:
            summary = result.get('summary', {})
            best_ratio = summary.get('best_compression_ratio', {})
            fastest_comp = summary.get('fastest_compression', {})
            fastest_decomp = summary.get('fastest_decompression', {})
            
            html += f'''
        <tr>
            <td>{Path(result.get('source_file', '')).name}</td>
            <td>{best_ratio.get('format', 'N/A')} ({best_ratio.get('ratio', 0):.3f})</td>
            <td>{fastest_comp.get('format', 'N/A')} ({fastest_comp.get('throughput', 0):.1f} MB/s)</td>
            <td>{fastest_decomp.get('format', 'N/A')} ({fastest_decomp.get('throughput', 0):.1f} MB/s)</td>
        </tr>
            '''
        
        html += '''
    </table>
</body>
</html>
        '''
        
        return html


if __name__ == '__main__':
    # Test reporter
    test_results = {
        'format_tests': {
            '7z': {'status': 'success'},
            'zip': {'status': 'success'},
            'gz': {'status': 'error', 'error': 'Test error'}
        },
        'performance': {
            'summary': {
                'compression': {
                    '7z_lzma2': {
                        'avg_throughput': 45.2,
                        'best_compression_ratio': 0.65,
                        'avg_duration': 12.3
                    }
                }
            }
        },
        'errors': ['Test error 1', 'Test error 2']
    }
    
    config = {'test_settings': {'output_dir': './results'}}
    reporter = Reporter(config)
    report_path = reporter.generate_report(test_results)
    print(f"Test report generated: {report_path}")