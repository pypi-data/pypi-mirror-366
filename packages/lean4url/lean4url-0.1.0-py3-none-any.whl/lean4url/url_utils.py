"""
URL encoding and decoding utilities for lean4url.

This module provides convenient functions for encoding data into URLs and
decoding data from URLs using lzstring compression.

Author: Rex Wang
"""

from typing import Dict, Optional, Any
from urllib.parse import quote, unquote, urlparse
from .core import LZString
from .constants import DEFAULT_SHARE_URL


def encode_url(data: str, base_url: Optional[str] = None, **kwargs: Any) -> str:
    """
    Encode input string and build a complete URL.
    
    Args:
        data: Data that needs to be encoded.
        base_url: URL prefix. If None, uses DEFAULT_SHARE_URL.
        **kwargs: Additional URL parameters.
        
    Returns:
        Complete constructed URL.
        
    Example:
        >>> encode_url("Hello World", "https://example.com")
        'https://example.com/#codez=BIUwNmD2A0AEDukBOYAmBMYAZhAY...'
        
        >>> encode_url("code", "https://playground.com", lang="python", theme="dark")
        'https://playground.com/#codez=...&lang=python&theme=dark'
    """
    if base_url is None:
        base_url = DEFAULT_SHARE_URL
    
    # Compress the data
    lz = LZString()
    compressed = lz.compress_to_base64(data)
    
    # Build parameter dictionary
    params = {'codez': compressed}
    
    # Add additional parameters
    for key, value in kwargs.items():
        if key == 'url':
            # URL encode the 'url' parameter value
            params[key] = quote(str(value))
        else:
            params[key] = str(value)
    
    # Construct parameter string
    param_str = '&'.join(f"{k}={v}" for k, v in params.items())
    
    # Build final URL
    return f"{base_url.rstrip('/')}/#{param_str}"


def decode_url(url: str) -> Dict[str, str]:
    """
    Decode original data from URL.
    
    Args:
        url: Complete URL containing encoded data.
        
    Returns:
        Dictionary containing all parameters with codez decoded.
        Returns empty dict if URL is invalid or decoding fails.
        
    Example:
        >>> result = decode_url("https://example.com/#codez=BIUwNmD2A0AE...&lang=python")
        >>> print(result['codez'])  # Original data
        >>> print(result['lang'])   # 'python'
    """
    try:
        # Parse URL to get fragment part
        parsed = urlparse(url)
        fragment = parsed.fragment
        
        if not fragment:
            return {}
        
        # Split all parameters by &
        params = fragment.split('&')
        result = {}
        
        # Parse each parameter
        for param in params:
            if '=' not in param:
                continue
                
            key, val = param.split('=', 1)
            
            if key == 'url':
                # URL decode the 'url' parameter
                result[key] = unquote(val)
            elif key == 'codez':
                # Decompress the 'codez' parameter
                lz = LZString()
                decompressed = lz.decompress_from_base64(val)
                result[key] = decompressed
            else:
                # Keep other parameters as-is
                result[key] = val
        
        return result
        
    except Exception:
        # Return empty dict on any error
        return {}
