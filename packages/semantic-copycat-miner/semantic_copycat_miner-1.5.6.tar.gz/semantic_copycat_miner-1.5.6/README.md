# Semantic Copycat Miner (CopycatM) v1.5.6

A comprehensive defensive security tool for detecting intellectual property contamination in AI-generated code. CopycatM extracts semantic signatures to identify when AI systems trained on proprietary codebases reproduce protected patterns, enabling organizations to assess IP risks and ensure legal compliance.

## Key Features

- **Enhanced Three-Tier Architecture**: Hybrid analysis with intelligent fallbacks
  - Tier 1: Baseline analysis with SWHID support (all files)
  - Tier 2: Traditional pattern matching with 60+ algorithm patterns
  - Tier 3: Semantic AI analysis with automatic fallback
- **Multi-language Support**: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust
- **Advanced Algorithm Detection**: 98.3% true positive rate
- **Cross-Language Normalization**: 84.2% file coverage
- **Signature Aggregation & Ranking**: 68.4% file coverage with 25% reduction
- **Dynamic Transformation Resistance**: ~64% average resistance
- **External Pattern Configuration**: JSON-based pattern definitions
- **Comprehensive Hashing**: Direct, fuzzy (TLSH), and semantic hashes
- **Multimedia Processing Detection**: Video, audio, image, and signal processing
- **Software Heritage ID Support**: Persistent identifiers for reproducible research

## Installation

### From PyPI
```bash
pip install semantic-copycat-miner
```

### From Source
```bash
git clone https://github.com/oscarvalenzuelab/semantic-copycat-miner
cd semantic-copycat-miner
pip install -e .
```

### Optional GNN Support
```bash
pip install -e .[gnn]
```

## Quick Start

### CLI Usage
```bash
# Single file analysis
copycatm src/algorithm.py -o results.json

# Directory analysis with parallel processing
copycatm ./codebase --parallel 4 -o results.json

# Enhanced configuration
copycatm algorithm.py --complexity-threshold 2 --min-lines 5 -o results.json

# Enable SWHID for persistent identification
copycatm algorithm.py --enable-swhid -o results.json
```

### Python API
```python
from copycatm import CopycatAnalyzer, AnalysisConfig

# Enhanced three-tier analysis (recommended)
analyzer = CopycatAnalyzer()
result = analyzer.analyze_file_enhanced("algorithm.py")

# Check for potential IP contamination
if result.get('algorithms'):
    for algo in result['algorithms']:
        if algo['confidence'] > 0.75:
            print(f"High-confidence pattern detected: {algo['algorithm_subtype']}")

# Custom configuration
config = AnalysisConfig(
    complexity_threshold=2,
    min_lines=5,
    enable_swhid=True
)
analyzer = CopycatAnalyzer(config)
result = analyzer.analyze_file_enhanced("algorithm.py")
```

## Documentation

For comprehensive documentation, see the **[Documentation Index](docs/index.md)**.

## Algorithm Detection

Detects 60+ algorithmic patterns across 8 major categories:

- **Core CS**: Sorting, searching, graph algorithms, dynamic programming
- **Security**: Encryption, hashing, authentication, anti-tampering
- **Multimedia**: Video/audio codecs, image processing, signal processing
- **System Level**: Drivers, firmware, bootloaders, kernel modules
- **Domain Specific**: ML, graphics, financial, medical, automotive

## Performance Metrics

- **Algorithm Detection F1-Score**: 0.857 (precision: 0.750, recall: 1.000)
- **Source Code Verification**: 100% success rate
- **Cross-Language Consistency**: 100% (JavaScript, Python, C)
- **Processing Speed**: ~0.061s average per file
- **Transformation Resistance**: ~64% average (dynamic calculation)

## Configuration

Create `copycatm.json` in your project directory:

```json
{
  "analysis": {
    "complexity_threshold": 3,
    "min_lines": 20,
    "confidence_threshold": 0.0
  },
  "hashing": {
    "algorithms": ["sha256", "tlsh", "minhash"]
  },
  "performance": {
    "parallel_workers": 4,
    "chunk_size": 100
  }
}
```

## Development

```bash
# Setup
pip install -e .[dev]

# Run tests
pytest tests/

# Code quality
black copycatm/
flake8 copycatm/
mypy copycatm/
```

## License

GNU Affero General Public License v3.0 - see LICENSE file for details.

## Acknowledgments

- Tree-sitter for robust parsing
- TLSH for fuzzy hashing
- DataSketch for MinHash implementation
- NetworkX for graph analysis