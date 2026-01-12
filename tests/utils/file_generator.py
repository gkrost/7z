#!/usr/bin/env python3
"""
File Generator for Test Data
Creates diverse test data files for format comparison
"""

import os
import random
import string
from pathlib import Path
from typing import Dict, Any, Tuple
import hashlib
import json


class FileGenerator:
    """Generates various types of test data files"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_data_dir = Path('test_data')
        self.temp_dir = Path(config.get('test_settings', {}).get('temp_dir', '/tmp/7z_tests'))
        
    def generate_all(self) -> bool:
        """Generate all test data files"""
        try:
            if self._is_test_data_complete():
                return True
            self._create_directories()
            self._generate_binary_files()
            self._generate_text_files()
            self._generate_mixed_content()
            self._create_hash_database()
            return True
        except Exception as e:
            print(f"Error generating test data: {e}")
            return False

    def _is_test_data_complete(self) -> bool:
        """Check whether test data already exists"""
        if not self.test_data_dir.exists():
            return False
        expected = [
            self.test_data_dir / 'binary',
            self.test_data_dir / 'text',
            self.test_data_dir / 'mixed',
            self.test_data_dir / 'file_hashes.json'
        ]
        return all(path.exists() for path in expected)
    
    def _create_directories(self):
        """Create necessary directories"""
        for subdir in ['binary', 'text', 'mixed', 'reference']:
            (self.test_data_dir / subdir).mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_binary_files(self):
        """Generate binary test files of various sizes"""
        binary_dir = self.test_data_dir / 'binary'
        
        test_sizes = self.config.get('test_data', {}).get('file_sizes', [])
        max_generate_size = self.config.get('test_data', {}).get('max_generate_size', '100MB')
        max_generate_bytes = self._parse_size(max_generate_size)
        
        for size_info in test_sizes:
            name = size_info['name']
            size_str = size_info['size']
            size_bytes = self._parse_size(size_str)
            if size_bytes > max_generate_bytes:
                continue
            
            # Random binary data
            filename = f"random_{name}_{size_str}.bin"
            filepath = binary_dir / filename
            self._generate_random_binary_file(filepath, size_bytes)
            
            # Compressed-looking data (less compressible)
            filename = f"compressed_{name}_{size_str}.bin"
            filepath = binary_dir / filename
            self._generate_compressed_binary_file(filepath, size_bytes)
            
            # Repeating pattern data (highly compressible)
            filename = f"pattern_{name}_{size_str}.bin"
            filepath = binary_dir / filename
            self._generate_pattern_binary_file(filepath, size_bytes)
    
    def _generate_text_files(self):
        """Generate text test files"""
        text_dir = self.test_data_dir / 'text'
        
        # Plain text
        self._generate_plain_text(text_dir)
        
        # JSON data
        self._generate_json_data(text_dir)
        
        # XML data  
        self._generate_xml_data(text_dir)
        
        # CSV data
        self._generate_csv_data(text_dir)
        
        # HTML data
        self._generate_html_data(text_dir)
        
        # Unicode text
        self._generate_unicode_text(text_dir)
    
    def _generate_mixed_content(self):
        """Generate mixed content directories"""
        mixed_dir = self.test_data_dir / 'mixed'
        
        # Small mixed directory
        small_mixed = mixed_dir / 'small_project'
        small_mixed.mkdir(exist_ok=True)
        self._create_project_structure(small_mixed, 'small')
        
        # Medium mixed directory
        medium_mixed = mixed_dir / 'medium_project'
        medium_mixed.mkdir(exist_ok=True)
        self._create_project_structure(medium_mixed, 'medium')
        
        # Large file collection
        large_collection = mixed_dir / 'large_collection'
        large_collection.mkdir(exist_ok=True)
        self._create_large_file_collection(large_collection)
    
    def _create_project_structure(self, base_dir: Path, size: str):
        """Create a realistic project directory structure"""
        # Source code files
        src_dir = base_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        
        if size == 'small':
            self._write_file(src_dir / 'main.c', self._generate_c_code())
            self._write_file(src_dir / 'utils.py', self._generate_python_code())
        elif size == 'medium':
            for i in range(10):
                self._write_file(src_dir / f'module_{i}.c', self._generate_c_code())
                self._write_file(src_dir / f'utils_{i}.py', self._generate_python_code())
        
        # Documentation
        docs_dir = base_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        self._write_file(docs_dir / 'README.md', self._generate_markdown())
        self._write_file(docs_dir / 'CHANGELOG.md', self._generate_markdown())
        
        # Configuration files
        self._write_file(base_dir / 'config.yaml', self._generate_yaml())
        self._write_file(base_dir / 'Makefile', self._generate_makefile())
        
        # Build artifacts
        build_dir = base_dir / 'build'
        build_dir.mkdir(exist_ok=True)
        self._generate_random_binary_file(build_dir / 'binary.o', 1024)
    
    def _create_large_file_collection(self, base_dir: Path):
        """Create a large collection of various file types"""
        file_types = [
            ('document', '.txt', self._generate_text_content),
            ('data', '.csv', self._generate_csv_content),
            ('config', '.json', self._generate_json_content),
            ('script', '.py', self._generate_python_code),
            ('binary', '.bin', lambda: self._generate_random_data(4096))
        ]
        
        for i in range(100):
            for prefix, ext, generator in file_types:
                filename = f"{prefix}_{i:03d}{ext}"
                filepath = base_dir / filename
                self._write_file(filepath, generator())
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '1KB', '10MB', '1GB' to bytes"""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        elif size_str.endswith('B'):
            return int(size_str[:-1])
        else:
            return int(size_str)
    
    def _generate_random_binary_file(self, filepath: Path, size: int):
        """Generate a file with random binary data"""
        with open(filepath, 'wb') as f:
            # Generate in chunks for large files
            chunk_size = 64 * 1024  # 64KB chunks
            remaining = size
            
            while remaining > 0:
                chunk = bytes(random.getrandbits(8) for _ in range(min(chunk_size, remaining)))
                f.write(chunk)
                remaining -= len(chunk)
    
    def _generate_compressed_binary_file(self, filepath: Path, size: int):
        """Generate a file that looks like compressed data (less compressible)"""
        with open(filepath, 'wb') as f:
            for i in range(size):
                # Generate data with high entropy
                byte = random.randint(0, 255)
                f.write(bytes([byte]))
    
    def _generate_pattern_binary_file(self, filepath: Path, size: int):
        """Generate a file with repeating patterns (highly compressible)"""
        pattern = b'A' * 100 + b'B' * 100 + b'C' * 100 + b'D' * 100 + b'E' * 100
        
        with open(filepath, 'wb') as f:
            remaining = size
            while remaining > 0:
                chunk = pattern[:min(len(pattern), remaining)]
                f.write(chunk)
                remaining -= len(chunk)
    
    def _generate_plain_text(self, base_dir: Path):
        """Generate plain text files"""
        self._write_file(base_dir / 'lorem_ipsum.txt', self._generate_lorem_ipsum())
        self._write_file(base_dir / 'english_text.txt', self._generate_english_text())
        self._write_file(base_dir / 'code_comments.txt', self._generate_code_comments())
    
    def _generate_json_data(self, base_dir: Path):
        """Generate JSON data files"""
        self._write_file(base_dir / 'small_data.json', self._generate_json_content())
        
        # Large JSON array
        large_data = [self._generate_json_object() for _ in range(1000)]
        self._write_file(base_dir / 'large_data.json', json.dumps(large_data, indent=2))
    
    def _generate_xml_data(self, base_dir: Path):
        """Generate XML data files"""
        self._write_file(base_dir / 'config.xml', self._generate_xml_content())
        self._write_file(base_dir / 'data.xml', self._generate_large_xml())
    
    def _generate_csv_data(self, base_dir: Path):
        """Generate CSV data files"""
        self._write_file(base_dir / 'small_data.csv', self._generate_csv_content())
        
        # Large CSV file
        lines = ['id,name,age,city']
        for i in range(10000):
            lines.append(f"{i},Person_{i},{random.randint(18, 80)},City_{random.randint(1, 100)}")
        
        self._write_file(base_dir / 'large_data.csv', '\n'.join(lines))
    
    def _generate_html_data(self, base_dir: Path):
        """Generate HTML data files"""
        self._write_file(base_dir / 'page.html', self._generate_html_content())
        self._write_file(base_dir / 'documentation.html', self._generate_large_html())
    
    def _generate_unicode_text(self, base_dir: Path):
        """Generate Unicode text files"""
        unicode_text = self._generate_unicode_content()
        self._write_file(base_dir / 'unicode.txt', unicode_text, encoding='utf-8')
        self._write_file(base_dir / 'unicode_bom.txt', '\ufeff' + unicode_text, encoding='utf-8-sig')
    
    def _generate_lorem_ipsum(self) -> str:
        """Generate Lorem Ipsum text"""
        words = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit',
                'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore',
                'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis', 'nostrud']
        
        sentences = []
        for _ in range(50):
            sentence_words = random.sample(words, random.randint(5, 15))
            sentence = ' '.join(sentence_words).capitalize() + '.'
            sentences.append(sentence)
        
        return '\n'.join(sentences)
    
    def _generate_english_text(self) -> str:
        """Generate English text"""
        return """
The quick brown fox jumps over the lazy dog. This pangram sentence contains every letter of the English alphabet.
It is commonly used for testing typefaces, font rendering, and other applications where all
letters need to be displayed. The sentence is short, memorable, and includes common letter
combinations that appear in English text.

In addition to testing purposes, pangrams serve as interesting linguistic examples. They demonstrate
how a relatively short sentence can encompass the entire character set of a language.
The English alphabet has 26 letters, and this particular pangram has been in use since the
late 19th century.

Modern variations exist, but the "quick brown fox" version remains the most widely recognized
and used pangram in the English language. It serves as an excellent test case for compression
algorithms, text processing systems, and cryptographic analyses.
        """.strip()
    
    def _generate_code_comments(self) -> str:
        """Generate code comment text"""
        return """
/*
 * This is a sample C source file comment block.
 * It demonstrates various comment styles and documentation patterns.
 * 
 * Functions:
 * - initialize(): Sets up initial conditions
 * - process(): Main processing loop
 * - cleanup(): Resource cleanup
 *
 * Author: Test Generator
 * Date: 2024
 * License: MIT
 */

/**
 * Main function entry point
 * @param argc Argument count
 * @param argv Argument vector
 * @return Exit status
 */
int main(int argc, char *argv[]) {
    // Initialize system
    if (initialize() != 0) {
        fprintf(stderr, "Initialization failed\\n");
        return 1;
    }
    
    // Process data
    while (process() == 0) {
        // Continue processing
    }
    
    // Clean up resources
    cleanup();
    return 0;
}
        """.strip()
    
    def _generate_text_content(self) -> str:
        """Generate generic text content"""
        return self._generate_lorem_ipsum()
    
    def _generate_json_content(self) -> str:
        """Generate JSON content"""
        data = {
            "name": "Test Data",
            "version": "1.0.0",
            "items": [
                {"id": 1, "type": "text", "content": "Sample text"},
                {"id": 2, "type": "binary", "size": 1024},
                {"id": 3, "type": "mixed", "files": ["a.txt", "b.bin"]}
            ],
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "modified": "2024-01-02T12:34:56Z",
                "tags": ["test", "sample", "data"]
            }
        }
        return json.dumps(data, indent=2)
    
    def _generate_json_object(self) -> Dict[str, Any]:
        """Generate a single JSON object"""
        return {
            "id": random.randint(1, 10000),
            "name": f"Object_{random.randint(1, 1000)}",
            "value": random.uniform(0.0, 1000.0),
            "active": random.choice([True, False]),
            "tags": [f"tag_{i}" for i in random.sample(range(1, 100), random.randint(1, 5))]
        }
    
    def _generate_xml_content(self) -> str:
        """Generate XML content"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <settings>
        <option name="compression" value="lzma2" />
        <option name="level" value="9" />
        <option name="threads" value="4" />
    </settings>
    
    <filters>
        <filter type="include" pattern="*.txt" />
        <filter type="exclude" pattern="*.tmp" />
        <filter type="exclude" pattern="*.log" />
    </filters>
    
    <metadata>
        <author>Test Generator</author>
        <created>2024-01-01</created>
        <description>Test configuration file</description>
    </metadata>
</configuration>'''
    
    def _generate_large_xml(self) -> str:
        """Generate large XML content"""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
        
        for i in range(1000):
            lines.append(f'    <item id="{i}">')
            lines.append(f'        <name>Item_{i}</name>')
            lines.append(f'        <value>{random.uniform(0, 100):.2f}</value>')
            lines.append(f'        <active>{"true" if random.choice([True, False]) else "false"}</active>')
            lines.append('    </item>')
        
        lines.append('</data>')
        return '\n'.join(lines)
    
    def _generate_csv_content(self) -> str:
        """Generate CSV content"""
        lines = ['id,name,value,category,active']
        
        for i in range(100):
            lines.append(f"{i},Item_{i},{random.uniform(0, 1000):.2f},Category_{random.randint(1, 10)},{random.choice(['Y', 'N'])}")
        
        return '\n'.join(lines)
    
    def _generate_html_content(self) -> str:
        """Generate HTML content"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>7-Zip Test Data</h1>
    <p>This is a test HTML file for compression testing.</p>
    
    <h2>Sections</h2>
    <ul>
        <li>Binary data</li>
        <li>Text files</li>
        <li>Mixed content</li>
    </ul>
    
    <h2>Performance Metrics</h2>
    <table>
        <tr><th>Format</th><th>Ratio</th><th>Speed</th></tr>
        <tr><td>7z</td><td>85%</td><td>50 MB/s</td></tr>
        <tr><td>ZIP</td><td>78%</td><td>75 MB/s</td></tr>
        <tr><td>GZIP</td><td>72%</td><td>90 MB/s</td></tr>
    </table>
</body>
</html>'''
    
    def _generate_large_html(self) -> str:
        """Generate large HTML content"""
        lines = ['<!DOCTYPE html>', '<html><head><title>Large Test Page</title></head><body>']
        
        for section in range(50):
            lines.append(f'<section id="section{section}">')
            lines.append(f'<h2>Section {section}</h2>')
            
            for paragraph in range(5):
                text = ' '.join(['Lorem ipsum dolor sit amet'] * 20)
                lines.append(f'<p>{text}</p>')
            
            lines.append('</section>')
        
        lines.extend(['</body></html>'])
        return '\n'.join(lines)
    
    def _generate_unicode_content(self) -> str:
        """Generate Unicode text with various characters"""
        # Include various Unicode ranges
        unicode_chars = []
        
        # Basic Latin
        unicode_chars.extend(string.ascii_letters + string.digits + string.punctuation)
        
        # Latin Extended
        unicode_chars.extend(['á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü', 'ö', 'ä', 'ß'])
        
        # Cyrillic
        unicode_chars.extend(['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й'])
        
        # Greek
        unicode_chars.extend(['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ'])
        
        # CJK (few examples)
        unicode_chars.extend(['中', '文', '字', '測', '試', '日', '本', '語'])
        
        # Arabic
        unicode_chars.extend(['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر'])
        
        # Hebrew
        unicode_chars.extend(['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'])
        
        # Emojis
        unicode_chars.extend(['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃'])
        
        # Mix them together
        text = ''
        for i in range(1000):
            text += random.choice(unicode_chars)
            if i % 50 == 0:
                text += '\n'
        
        return text
    
    def _generate_c_code(self) -> str:
        """Generate C source code"""
        return '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int counter = 0;

int increment(int value) {
    return value + 1;
}

void print_message(const char* msg) {
    printf("Message: %s\\n", msg);
}

int main(int argc, char* argv[]) {
    counter = 0;
    
    for (int i = 0; i < 10; i++) {
        counter = increment(counter);
        print_message("Processing...");
    }
    
    printf("Final counter: %d\\n", counter);
    return 0;
}'''
    
    def _generate_python_code(self) -> str:
        """Generate Python source code"""
        return '''#!/usr/bin/env python3
"""
Sample Python module for testing purposes
"""

import random
import sys
from typing import List, Dict


class DataProcessor:
    """Simple data processing class"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(1, 1000)
        random.seed(self.seed)
        self.data = []
    
    def generate_data(self, count: int) -> List[int]:
        """Generate random data"""
        self.data = [random.randint(1, 1000) for _ in range(count)]
        return self.data
    
    def calculate_stats(self) -> Dict[str, float]:
        """Calculate statistics"""
        if not self.data:
            return {}
        
        return {
            'mean': sum(self.data) / len(self.data),
            'min': min(self.data),
            'max': max(self.data),
            'count': len(self.data)
        }
    
    def __str__(self) -> str:
        return f"DataProcessor(seed={self.seed}, items={len(self.data)})"


def main():
    """Main function"""
    processor = DataProcessor()
    data = processor.generate_data(100)
    stats = processor.calculate_stats()
    
    print(f"Generated {len(data)} items")
    print(f"Statistics: {stats}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())'''
    
    def _generate_markdown(self) -> str:
        """Generate Markdown content"""
        return '''# Project Documentation

## Overview

This is a test project for 7-Zip compression testing.

## Installation

```bash
make
make install
```

## Usage

```bash
./program --input file.txt --output archive.7z
```

## Features

- High compression ratio
- Fast compression speed
- Multi-threading support
- Cross-platform compatibility

## Configuration

Edit `config.yaml` to customize settings:

```yaml
compression:
  method: "lzma2"
  level: 9
  threads: 4

output:
  format: "7z"
  encryption: true
```

## License

MIT License - see LICENSE file for details.
'''
    
    def _generate_yaml(self) -> str:
        """Generate YAML content"""
        return '''# Configuration File

project:
  name: "test_project"
  version: "1.0.0"
  author: "Test Generator"

build:
  compiler: "gcc"
  flags:
    - "-O2"
    - "-Wall"
    - "-Wextra"
  output: "program"

compression:
  format: "7z"
  method: "lzma2"
  level: 9
  threads: 4
  
filters:
  - name: "source"
    pattern: "*.c"
    action: "include"
  - name: "objects"
    pattern: "*.o"
    action: "exclude"
  - name: "temporary"
    pattern: "*.tmp"
    action: "exclude"

logging:
  level: "info"
  file: "build.log"
  format: "%(asctime)s - %(levelname)s - %(message)s"
'''
    
    def _generate_makefile(self) -> str:
        """Generate Makefile content"""
        return '''# Makefile for test project

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lm

SRCDIR = src
OBJDIR = obj
BINDIR = bin

SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
TARGET = $(BINDIR)/program

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(OBJECTS) | $(BINDIR)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR):
	mkdir -p $(OBJDIR)

$(BINDIR):
	mkdir -p $(BINDIR)

clean:
	rm -rf $(OBJDIR) $(BINDIR)

install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

test: $(TARGET)
	./$(TARGET)
'''
    
    def _generate_random_data(self, size: int) -> bytes:
        """Generate random binary data"""
        return bytes(random.getrandbits(8) for _ in range(size))
    
    def _write_file(self, filepath: Path, content: str | bytes, encoding: str = 'utf-8'):
        """Write content to file"""
        if isinstance(content, (bytes, bytearray)):
            with open(filepath, 'wb') as f:
                f.write(content)
            return
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
    
    def _create_hash_database(self):
        """Create hash database for integrity verification"""
        hash_db = {}
        
        for file_path in self.test_data_dir.rglob('*'):
            if file_path.is_file():
                file_hash = self._calculate_file_hash(file_path)
                relative_path = file_path.relative_to(self.test_data_dir)
                hash_db[str(relative_path)] = {
                    'sha256': file_hash,
                    'size': file_path.stat().st_size,
                    'mtime': file_path.stat().st_mtime
                }
        
        # Save hash database
        hash_file = self.test_data_dir / 'file_hashes.json'
        with open(hash_file, 'w') as f:
            json.dump(hash_db, f, indent=2)
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


if __name__ == '__main__':
    # Test the generator
    config = {
        'test_data': {
            'file_sizes': [
                {'name': 'tiny', 'size': '1KB'},
                {'name': 'small', 'size': '100KB'}
            ]
        },
        'test_settings': {
            'temp_dir': '/tmp/7z_tests'
        }
    }
    
    generator = FileGenerator(config)
    success = generator.generate_all()
    print(f"Generation {'successful' if success else 'failed'}")