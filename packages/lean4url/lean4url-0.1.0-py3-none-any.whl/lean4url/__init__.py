"""
lean4url: High-performance lzstring compression library compatible with JavaScript implementation.

A Python implementation of lzstring compression that is 100% compatible with the 
JavaScript pieroxy/lz-string library, correctly handling Unicode characters including
emojis and special symbols.

Author: Rex Wang
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Rex Wang"
__email__ = "1073853456@qq.com"
__license__ = "MIT"

from .core import LZString
from .url_utils import encode_url, decode_url
from .constants import DEFAULT_SHARE_URL

__all__ = [
    "LZString",
    "encode_url", 
    "decode_url",
    "DEFAULT_SHARE_URL",
    "__version__",
]
