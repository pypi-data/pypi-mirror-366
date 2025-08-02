"""
Directory structure analysis for project fingerprinting.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import re


class DirectoryStructureAnalyzer:
    """Analyze directory structure to generate project signatures."""
    
    def __init__(self):
        # Common file patterns to track
        self.build_files = {
            'python': ['setup.py', 'setup.cfg', 'pyproject.toml', 'requirements.txt', 'Pipfile'],
            'javascript': ['package.json', 'package-lock.json', 'yarn.lock', 'tsconfig.json'],
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle'],
            'c': ['Makefile', 'CMakeLists.txt', 'configure', 'configure.ac'],
            'cpp': ['Makefile', 'CMakeLists.txt', 'configure', 'configure.ac'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'go': ['go.mod', 'go.sum']
        }
        
        # Common directory patterns
        self.common_dirs = {
            'source': ['src', 'lib', 'source', 'sources'],
            'test': ['test', 'tests', 'spec', 'specs', '__tests__', 'test_*'],
            'docs': ['docs', 'doc', 'documentation'],
            'config': ['config', 'configs', '.config', 'configuration'],
            'build': ['build', 'dist', 'out', 'target', 'bin'],
            'assets': ['assets', 'static', 'public', 'resources'],
            'vendor': ['vendor', 'vendors', 'third_party', 'external', 'node_modules']
        }
        
        # File extension categories
        self.extension_categories = {
            'source': {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.cc', '.h', '.hpp', '.rs', '.go'},
            'test': {'.test.py', '.spec.js', '.test.js', '.spec.ts', '.test.ts', '_test.go'},
            'config': {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'},
            'docs': {'.md', '.rst', '.txt', '.adoc', '.tex'},
            'data': {'.csv', '.json', '.xml', '.sql', '.db', '.sqlite'}
        }
    
    def analyze_directory(self, directory_path: str, max_depth: int = 5) -> Dict[str, any]:
        """Analyze directory structure and generate signatures."""
        directory = Path(directory_path)
        
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        # Collect structure information
        structure_info = {
            'root_path': str(directory),
            'total_files': 0,
            'total_dirs': 0,
            'max_depth': 0,
            'file_extensions': defaultdict(int),
            'directory_patterns': defaultdict(int),
            'build_files': [],
            'language_indicators': defaultdict(int),
            'tree_structure': {},
            'path_patterns': []
        }
        
        # Walk directory tree
        self._walk_directory(directory, structure_info, current_depth=0, max_depth=max_depth)
        
        # Generate signatures
        signatures = self._generate_signatures(structure_info)
        
        return {
            'structure_info': structure_info,
            'signatures': signatures
        }
    
    def _walk_directory(self, directory: Path, info: Dict, current_depth: int, max_depth: int,
                       parent_path: str = ""):
        """Recursively walk directory tree."""
        if current_depth > max_depth:
            return
        
        info['max_depth'] = max(info['max_depth'], current_depth)
        
        try:
            items = list(directory.iterdir())
        except PermissionError:
            return
        
        dirs = []
        files = []
        
        for item in items:
            if item.is_dir():
                # Skip common vendor directories
                if item.name in ['node_modules', '.git', '__pycache__', '.venv', 'venv']:
                    continue
                dirs.append(item)
            elif item.is_file():
                files.append(item)
        
        # Update counts
        info['total_dirs'] += len(dirs)
        info['total_files'] += len(files)
        
        # Analyze files
        for file in files:
            self._analyze_file(file, info, parent_path)
        
        # Analyze subdirectories
        for dir in dirs:
            dir_name = dir.name.lower()
            
            # Track directory patterns
            for category, patterns in self.common_dirs.items():
                if any(pattern in dir_name for pattern in patterns):
                    info['directory_patterns'][category] += 1
            
            # Record path pattern
            rel_path = os.path.join(parent_path, dir.name)
            info['path_patterns'].append(rel_path)
            
            # Recurse
            self._walk_directory(dir, info, current_depth + 1, max_depth, rel_path)
    
    def _analyze_file(self, file: Path, info: Dict, parent_path: str):
        """Analyze individual file."""
        # Track extension
        ext = file.suffix.lower()
        if ext:
            info['file_extensions'][ext] += 1
        
        # Check for build files
        filename = file.name.lower()
        for lang, build_files in self.build_files.items():
            if filename in [bf.lower() for bf in build_files]:
                info['build_files'].append(file.name)
                info['language_indicators'][lang] += 1
        
        # Track special file patterns
        if filename == 'readme.md' or filename == 'readme.txt':
            info['language_indicators']['has_readme'] = True
        elif filename == 'license' or filename == 'license.txt':
            info['language_indicators']['has_license'] = True
        elif filename.startswith('.'):
            info['language_indicators']['has_dotfiles'] = True
    
    def _generate_signatures(self, info: Dict) -> Dict[str, any]:
        """Generate various signatures from structure information."""
        signatures = {}
        
        # 1. Extension distribution hash
        ext_distribution = []
        total_files = sum(info['file_extensions'].values())
        if total_files > 0:
            for ext, count in sorted(info['file_extensions'].items()):
                ratio = count / total_files
                ext_distribution.append(f"{ext}:{ratio:.2f}")
        
        ext_sig = hashlib.sha256('|'.join(ext_distribution).encode()).hexdigest()[:16]
        signatures['extension_signature'] = ext_sig
        
        # 2. Directory pattern signature
        dir_patterns = []
        for category, count in sorted(info['directory_patterns'].items()):
            dir_patterns.append(f"{category}:{count}")
        
        dir_sig = hashlib.sha256('|'.join(dir_patterns).encode()).hexdigest()[:16]
        signatures['directory_signature'] = dir_sig
        
        # 3. Path pattern signature (normalized)
        normalized_paths = self._normalize_paths(info['path_patterns'])
        path_sig = hashlib.sha256('|'.join(sorted(normalized_paths)).encode()).hexdigest()[:16]
        signatures['path_signature'] = path_sig
        
        # 4. Build system signature
        build_sig = hashlib.sha256('|'.join(sorted(info['build_files'])).encode()).hexdigest()[:16]
        signatures['build_signature'] = build_sig
        
        # 5. Project type classification
        signatures['project_type'] = self._classify_project_type(info)
        
        # 6. Structural complexity
        signatures['structural_complexity'] = {
            'depth': info['max_depth'],
            'breadth': info['total_dirs'],
            'file_count': info['total_files'],
            'diversity': len(info['file_extensions'])
        }
        
        # 7. Language confidence scores
        signatures['language_confidence'] = self._calculate_language_confidence(info)
        
        return signatures
    
    def _normalize_paths(self, paths: List[str]) -> List[str]:
        """Normalize path patterns for comparison."""
        normalized = []
        
        for path in paths:
            # Replace version numbers with placeholder
            path = re.sub(r'\d+\.\d+\.\d+', 'X.X.X', path)
            path = re.sub(r'v\d+', 'vX', path)
            
            # Normalize common variations
            path = path.replace('tests', 'test')
            path = path.replace('docs', 'doc')
            path = path.replace('sources', 'src')
            
            normalized.append(path)
        
        return normalized
    
    def _classify_project_type(self, info: Dict) -> str:
        """Classify project type based on structure."""
        # Check for common project types
        if 'node_modules' in str(info.get('path_patterns', [])):
            return 'node_project'
        elif any('setup.py' in f for f in info['build_files']):
            return 'python_package'
        elif any('pom.xml' in f for f in info['build_files']):
            return 'maven_project'
        elif any('cargo.toml' in f.lower() for f in info['build_files']):
            return 'rust_crate'
        elif any('go.mod' in f for f in info['build_files']):
            return 'go_module'
        elif info['directory_patterns'].get('source', 0) > 0:
            return 'source_library'
        else:
            return 'generic_project'
    
    def _calculate_language_confidence(self, info: Dict) -> Dict[str, float]:
        """Calculate confidence scores for each language."""
        scores = defaultdict(float)
        
        # Score based on build files
        for lang, count in info['language_indicators'].items():
            if lang not in ['has_readme', 'has_license', 'has_dotfiles']:
                scores[lang] += count * 0.3
        
        # Score based on file extensions
        lang_extensions = {
            'python': {'.py', '.pyx', '.pyi'},
            'javascript': {'.js', '.jsx', '.ts', '.tsx'},
            'java': {'.java', '.class', '.jar'},
            'c': {'.c', '.h'},
            'cpp': {'.cpp', '.cc', '.cxx', '.hpp', '.h'},
            'rust': {'.rs'},
            'go': {'.go'}
        }
        
        total_source_files = 0
        lang_file_counts = defaultdict(int)
        
        for ext, count in info['file_extensions'].items():
            for lang, exts in lang_extensions.items():
                if ext in exts:
                    lang_file_counts[lang] += count
                    total_source_files += count
        
        # Calculate normalized scores
        if total_source_files > 0:
            for lang, count in lang_file_counts.items():
                scores[lang] += (count / total_source_files) * 0.7
        
        # Normalize to 0-1 range
        max_score = max(scores.values()) if scores else 1
        normalized_scores = {
            lang: score / max_score 
            for lang, score in scores.items()
        }
        
        # Sort by score and return top languages
        sorted_scores = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_scores[:3])  # Top 3 languages
    
    def compare_structures(self, structure1: Dict, structure2: Dict) -> Dict[str, float]:
        """Compare two directory structures and calculate similarity scores."""
        sig1 = structure1['signatures']
        sig2 = structure2['signatures']
        
        similarities = {}
        
        # 1. Extension signature similarity
        similarities['extension_similarity'] = self._signature_similarity(
            sig1['extension_signature'], sig2['extension_signature']
        )
        
        # 2. Directory pattern similarity
        similarities['directory_similarity'] = self._signature_similarity(
            sig1['directory_signature'], sig2['directory_signature']
        )
        
        # 3. Path pattern similarity
        similarities['path_similarity'] = self._signature_similarity(
            sig1['path_signature'], sig2['path_signature']
        )
        
        # 4. Build system similarity
        similarities['build_similarity'] = self._signature_similarity(
            sig1['build_signature'], sig2['build_signature']
        )
        
        # 5. Project type match
        similarities['project_type_match'] = 1.0 if sig1['project_type'] == sig2['project_type'] else 0.0
        
        # 6. Structural complexity similarity
        comp1 = sig1['structural_complexity']
        comp2 = sig2['structural_complexity']
        
        complexity_sim = 0.0
        for metric in ['depth', 'breadth', 'file_count', 'diversity']:
            if comp1[metric] > 0 or comp2[metric] > 0:
                min_val = min(comp1[metric], comp2[metric])
                max_val = max(comp1[metric], comp2[metric])
                complexity_sim += min_val / max_val if max_val > 0 else 0
        
        similarities['complexity_similarity'] = complexity_sim / 4
        
        # 7. Language overlap
        lang1 = set(sig1['language_confidence'].keys())
        lang2 = set(sig2['language_confidence'].keys())
        
        if lang1 or lang2:
            similarities['language_overlap'] = len(lang1.intersection(lang2)) / len(lang1.union(lang2))
        else:
            similarities['language_overlap'] = 0.0
        
        # Calculate overall similarity
        similarities['overall'] = sum(similarities.values()) / len(similarities)
        
        return similarities
    
    def _signature_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between two hash signatures."""
        if sig1 == sig2:
            return 1.0
        
        # Calculate character-wise similarity
        matches = sum(c1 == c2 for c1, c2 in zip(sig1, sig2))
        return matches / max(len(sig1), len(sig2))