# lean4url

[![PyPI version](https://badge.fury.io/py/lean4url.svg)](https://badge.fury.io/py/lean4url)
[![Python Version](https://img.shields.io/pypi/pyversions/lean4url.svg)](https://pypi.org/project/lean4url/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/rexwzh/lean4url/workflows/Tests/badge.svg)](https://github.com/rexwzh/lean4url/actions)
[![Coverage](https://codecov.io/gh/rexwzh/lean4url/branch/main/graph/badge.svg)](https://codecov.io/gh/rexwzh/lean4url)

A high-performance lzstring compression library fully compatible with JavaScript implementation.

## Features

✅ **Fully Compatible** - 100% compatible with [pieroxy/lz-string](https://github.com/pieroxy/lz-string) JavaScript implementation

✅ **Unicode Support** - Correctly handles all Unicode characters, including emoji and special symbols

✅ **URL Friendly** - Built-in URL encoding/decoding functionality

✅ **High Performance** - Optimized algorithm implementation

✅ **Type Safe** - Complete type annotation support

✅ **Thoroughly Tested** - Includes comparative tests with JavaScript version

## Background

Existing Python lzstring packages have issues with Unicode character handling. For example, for the character "𝔓":

- **Existing package output**: `sirQ`
- **JavaScript original output**: `qwbmRdo=`
- **lean4url output**: `qwbmRdo=` ✅

lean4url solves this problem by correctly simulating JavaScript's UTF-16 encoding behavior.

## Installation

```bash
pip install lean4url
```

## Quick Start

### Basic Compression/Decompression

```python
from lean4url import LZString

# Create instance
lz = LZString()

# Compress string
original = "Hello, 世界! 🌍"
compressed = lz.compress_to_base64(original)
print(f"Compressed: {compressed}")

# Decompress string
decompressed = lz.decompress_from_base64(compressed)
print(f"Decompressed: {decompressed}")
# Output: Hello, 世界! 🌍
```

### URL Encoding/Decoding

```python
from lean4url import encode_url, decode_url

# Encode data to URL
data = "This is data to be encoded"
url = encode_url(data, base_url="https://example.com/share")
print(f"Encoded URL: {url}")
# Output: https://example.com/share/#codez=BIUwNmD2A0AEDukBOYAmBMYAZhAY...

# Decode data from URL
result = decode_url(url)
print(f"Decoded result: {result['codez']}")
# Output: This is data to be encoded
```

### URL Encoding with Parameters

```python
from lean4url import encode_url, decode_url

# Add extra parameters when encoding
code = "function hello() { return 'world'; }"
url = encode_url(
    code, 
    base_url="https://playground.example.com",
    lang="javascript",
    theme="dark",
    url="https://docs.example.com"  # This parameter will be URL encoded
)

print(f"Complete URL: {url}")
# Output: https://playground.example.com/#codez=BIUwNmD2A0A...&lang=javascript&theme=dark&url=https%3A//docs.example.com

# Decode URL to get all parameters
params = decode_url(url)
print(f"Code: {params['codez']}")
print(f"Language: {params['lang']}")
print(f"Theme: {params['theme']}")
print(f"Documentation link: {params['url']}")
```

## API Reference

### LZString Class

```python
class LZString:
    def compress_to_base64(self, input_str: str) -> str:
        """Compress string to Base64 format"""
        
    def decompress_from_base64(self, input_str: str) -> str:
        """Decompress string from Base64 format"""
        
    def compress_to_utf16(self, input_str: str) -> str:
        """Compress string to UTF16 format"""
        
    def decompress_from_utf16(self, input_str: str) -> str:
        """Decompress string from UTF16 format"""
```

### URL Utility Functions

```python
def encode_url(data: str, base_url: str = None, **kwargs) -> str:
    """
    Encode input string and build complete URL.
    
    Args:
        data: Data to be encoded
        base_url: URL prefix
        **kwargs: Additional URL parameters
        
    Returns:
        Built complete URL
    """

def decode_url(url: str) -> dict:
    """
    Decode original data from URL.
    
    Args:
        url: Complete URL
        
    Returns:
        Dictionary containing all parameters, with codez decoded
    """
```

## Development

### Environment Setup

```bash
# Clone repository
git clone https://github.com/rexwzh/lean4url.git
cd lean4url

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Start JavaScript test service
cd tests/js_service
npm install
node server.js &
cd ../.. 

# Run Python tests
pytest

# Run tests with coverage
pytest --cov=lean4url --cov-report=html
```

### Code Formatting

```bash
# Format code
black src tests
isort src tests

# Type checking
mypy src

# Code checking
flake8 src tests
```

## Algorithm Principles

lean4url is based on a variant of the LZ78 compression algorithm, with core ideas:

1. **Dictionary Building** - Dynamically build character sequence dictionary
2. **Sequence Matching** - Find longest matching sequences
3. **UTF-16 Compatibility** - Simulate JavaScript's UTF-16 surrogate pair behavior
4. **Base64 Encoding** - Encode compression results in URL-safe format

### Unicode Handling

The key difference from existing Python packages is in Unicode character handling:

- **JavaScript**: Uses UTF-16 surrogate pairs, "𝔓" → `[0xD835, 0xDCD3]`
- **Existing Python packages**: Use Unicode code points, "𝔓" → `[0x1D4D3]`
- **lean4url**: Simulates JavaScript behavior, ensuring compatibility

## License

MIT License - See the [LICENSE](LICENSE) file for details.

## Contributing

Issues and Pull Requests are welcome!

## Changelog

### v1.0.0
- Initial version release
- Complete lzstring algorithm implementation
- JavaScript compatibility
- URL encoding/decoding functionality
- Complete test suite