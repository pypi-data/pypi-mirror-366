"""
Constants used throughout the lean4url package.
"""

# Default base URL for sharing functionality
DEFAULT_SHARE_URL = "https://lean4url.example.com/share"

# Base64 character set used by lzstring
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

# UTF-16 constants
UTF16_HIGH_SURROGATE_START = 0xD800
UTF16_HIGH_SURROGATE_END = 0xDBFF
UTF16_LOW_SURROGATE_START = 0xDC00
UTF16_LOW_SURROGATE_END = 0xDFFF

# Compression algorithm constants
COMPRESSION_DICT_SIZE_INITIAL = 4
COMPRESSION_DICT_SIZE_INCREMENT = 1
COMPRESSION_MAX_DICT_SIZE = 16384
