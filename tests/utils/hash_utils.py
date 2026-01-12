#!/usr/bin/env python3
"""
Hash Utilities for File Integrity Verification
"""

import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional


class HashUtils:
    """Utilities for calculating and verifying file hashes"""
    
    SUPPORTED_ALGORITHMS = {
        'MD5': hashlib.md5,
        'SHA1': hashlib.sha1,
        'SHA256': hashlib.sha256,
        'SHA512': hashlib.sha512,
        'CRC32': None  # Special case
    }
    
    def __init__(self):
        self.algorithm = 'SHA256'
    
    def set_algorithm(self, algorithm: str) -> bool:
        """Set the hash algorithm"""
        if algorithm.upper() in self.SUPPORTED_ALGORITHMS:
            self.algorithm = algorithm.upper()
            return True
        return False
    
    def calculate_file_hash(self, filepath: Path, algorithm: Optional[str] = None) -> str:
        """Calculate hash of a file"""
        algo = algorithm or self.algorithm
        
        if algo == 'CRC32':
            return self._calculate_crc32(filepath)
        
        hash_func = self.SUPPORTED_ALGORITHMS.get(algo)
        if not hash_func:
            raise ValueError(f"Unsupported algorithm: {algo}")
        
        hasher = hash_func()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def calculate_string_hash(self, data: str, algorithm: Optional[str] = None) -> str:
        """Calculate hash of a string"""
        algo = algorithm or self.algorithm
        
        if algo == 'CRC32':
            return self._calculate_crc32_string(data)
        
        hash_func = self.SUPPORTED_ALGORITHMS.get(algo)
        if not hash_func:
            raise ValueError(f"Unsupported algorithm: {algo}")
        
        hasher = hash_func()
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    def _calculate_crc32(self, filepath: Path) -> str:
        """Calculate CRC32 of a file"""
        crc = 0
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                crc = self._update_crc32(crc, chunk)
        
        return f"{crc:08x}"
    
    def _calculate_crc32_string(self, data: str) -> str:
        """Calculate CRC32 of a string"""
        crc = 0
        chunk = data.encode('utf-8')
        crc = self._update_crc32(crc, chunk)
        return f"{crc:08x}"
    
    def _update_crc32(self, crc: int, data: bytes) -> int:
        """Update CRC32 with new data"""
        import zlib
        return zlib.crc32(data, crc) & 0xffffffff
    
    def verify_file_hash(self, filepath: Path, expected_hash: str, algorithm: Optional[str] = None) -> bool:
        """Verify file hash matches expected value"""
        try:
            actual_hash = self.calculate_file_hash(filepath, algorithm)
            return actual_hash.lower() == expected_hash.lower()
        except Exception:
            return False
    
    def verify_directory_hashes(self, directory: Path, hash_db: Dict[str, Any], algorithm: Optional[str] = None) -> Dict[str, Any]:
        """Verify all files in directory against hash database"""
        results = {
            'total_files': 0,
            'verified': 0,
            'failed': 0,
            'missing': 0,
            'errors': []
        }
        
        for rel_path, file_info in hash_db.items():
            filepath = directory / rel_path
            results['total_files'] += 1
            
            if not filepath.exists():
                results['missing'] += 1
                results['errors'].append({'file': str(rel_path), 'error': 'file_missing'})
                continue
            
            try:
                actual_hash = self.calculate_file_hash(filepath, algorithm)
                expected_hash = file_info['sha256'] if algorithm is None else file_info.get(algorithm.lower(), '')
                
                if actual_hash.lower() == expected_hash.lower():
                    results['verified'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'file': str(rel_path), 
                        'error': 'hash_mismatch',
                        'expected': expected_hash,
                        'actual': actual_hash
                    })
            except Exception as e:
                results['errors'].append({'file': str(rel_path), 'error': str(e)})
        
        return results
    
    def create_hash_database(self, directory: Path, algorithm: Optional[str] = None) -> Dict[str, Any]:
        """Create hash database for all files in directory"""
        algo = algorithm or self.algorithm
        hash_db = {}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    rel_path = file_path.relative_to(directory)
                    file_hash = self.calculate_file_hash(file_path, algo)
                    
                    hash_db[str(rel_path)] = {
                        algo.lower(): file_hash,
                        'size': file_path.stat().st_size,
                        'mtime': file_path.stat().st_mtime
                    }
                except Exception as e:
                    print(f"Error hashing {file_path}: {e}")
        
        return hash_db
    
    def compare_directories(self, dir1: Path, dir2: Path, algorithm: Optional[str] = None) -> Dict[str, Any]:
        """Compare two directories for identical files"""
        hash_db1 = self.create_hash_database(dir1, algorithm)
        hash_db2 = self.create_hash_database(dir2, algorithm)
        
        results = {
            'only_in_dir1': [],
            'only_in_dir2': [],
            'different': [],
            'identical': []
        }
        
        files1 = set(hash_db1.keys())
        files2 = set(hash_db2.keys())
        
        # Files only in dir1
        results['only_in_dir1'] = list(files1 - files2)
        
        # Files only in dir2
        results['only_in_dir2'] = list(files2 - files1)
        
        # Files in both - compare hashes
        common_files = files1 & files2
        for filename in common_files:
            hash1 = hash_db1[filename][algorithm.lower() if algorithm else 'sha256']
            hash2 = hash_db2[filename][algorithm.lower() if algorithm else 'sha256']
            
            if hash1 == hash2:
                results['identical'].append(filename)
            else:
                results['different'].append({'file': filename, 'hash1': hash1, 'hash2': hash2})
        
        return results