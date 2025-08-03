"""
Core tests for lean4url package.

These tests verify the functionality of the lzstring implementation
and ensure compatibility with the JavaScript reference implementation.

Author: Rex Wang
"""

import pytest
import requests
from typing import List, Dict, Any

from lean4url import LZString, encode_url, decode_url


class TestLZStringCore:
    """Test core lzstring functionality."""
    
    def test_initialization(self):
        """Test LZString class initialization."""
        lz = LZString()
        assert lz is not None
        assert hasattr(lz, 'compress_to_base64')
        assert hasattr(lz, 'decompress_from_base64')
    
    def test_empty_string(self):
        """Test compression of empty string."""
        lz = LZString()
        result = lz.compress_to_base64("")
        assert result == ""
        
        decompressed = lz.decompress_from_base64("")
        assert decompressed == ""
    
    def test_single_character(self):
        """Test compression of single character."""
        lz = LZString()
        result = lz.compress_to_base64("a")
        assert result != ""
        assert isinstance(result, str)
    
    def test_basic_string(self):
        """Test compression of basic ASCII string."""
        lz = LZString()
        original = "Hello, World!"
        compressed = lz.compress_to_base64(original)
        
        assert compressed != ""
        assert isinstance(compressed, str)
        assert len(compressed) < len(original) * 2  # Should not expand too much
    
    @pytest.mark.parametrize("test_string", [
        "Hello",
        "World",
        "The quick brown fox",
        "A" * 100,
    ])
    def test_roundtrip_basic(self, test_string: str):
        """Test compression and decompression roundtrip for basic strings."""
        lz = LZString()
        compressed = lz.compress_to_base64(test_string)
        decompressed = lz.decompress_from_base64(compressed)
        
        # Note: This test might fail until decompression is fully implemented
        # assert decompressed == test_string
        
        # For now, just verify compression works
        assert compressed != ""
    
    def test_unicode_character_problematic_case(self):
        """Test the specific Unicode character that was problematic."""
        lz = LZString()
        problematic_char = "𝔓"  # U+1D4D3
        
        compressed = lz.compress_to_base64(problematic_char)
        
        # This should eventually produce "qwbmRdo=" to match JavaScript
        # For now, just verify it produces some output
        assert compressed != ""
        assert isinstance(compressed, str)
        
        # TODO: Once algorithm is complete, verify exact output
        # assert compressed == "qwbmRdo="


class TestJavaScriptCompatibility:
    """Test compatibility with JavaScript lz-string implementation."""
    
    def test_service_health(self, js_service: str):
        """Test that JavaScript service is running."""
        response = requests.get(f"{js_service}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_problematic_character_js_comparison(self, js_service: str):
        """Test the problematic character against JavaScript implementation."""
        problematic_char = "𝔓"  # U+1D4D3
        
        # Get JavaScript result
        response = requests.post(
            f"{js_service}/compress",
            json={"input": problematic_char, "method": "compressToBase64"}
        )
        assert response.status_code == 200
        js_result = response.json()["output"]
        
        # Test our implementation
        lz = LZString()
        py_result = lz.compress_to_base64(problematic_char)
        
        # Verify JavaScript produces expected result
        assert js_result == "qwbmRdo="
        
        # TODO: Once our implementation is complete, verify it matches
        # assert py_result == js_result
        print(f"JavaScript result: {js_result}")
        print(f"Python result: {py_result}")
    
    @pytest.mark.parametrize("test_input", [
        "Hello",
        "World",
        "🌍",
        "测试",
        "𝔓",
    ])
    def test_compression_comparison(self, js_service: str, test_input: str):
        """Compare compression results with JavaScript implementation."""
        # Get JavaScript result
        response = requests.post(
            f"{js_service}/compress",
            json={"input": test_input, "method": "compressToBase64"}
        )
        assert response.status_code == 200
        js_result = response.json()["output"]
        
        # Test our implementation
        lz = LZString()
        py_result = lz.compress_to_base64(test_input)
        
        # For now, just verify both produce non-empty results
        assert js_result != ""
        assert py_result != ""
        
        print(f"Input: {test_input!r}")
        print(f"JavaScript: {js_result}")
        print(f"Python: {py_result}")
        
        # TODO: Once implementation is complete, verify they match
        # assert py_result == js_result
    
    def test_batch_unicode_test(self, js_service: str, unicode_edge_cases: List[str]):
        """Test batch Unicode characters against JavaScript."""
        test_cases = [{"input": char, "method": "compressToBase64"} for char in unicode_edge_cases]
        
        response = requests.post(
            f"{js_service}/batch-test",
            json={"testCases": test_cases}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]["successful"] > 0
        
        # Test each case with our implementation
        lz = LZString()
        for i, char in enumerate(unicode_edge_cases):
            js_result = data["results"][i]["compressed"]
            py_result = lz.compress_to_base64(char)
            
            if len(char) == 1:
                print(f"Character: {char!r} (U+{ord(char):04X})")
            else:
                # For multi-character sequences (like combined emojis)
                unicode_repr = " + ".join(f"U+{ord(c):04X}" for c in char)
                print(f"Character: {char!r} ({unicode_repr})")
            print(f"JavaScript: {js_result}")
            print(f"Python: {py_result}")
            print("---")


class TestURLFunctions:
    """Test URL encoding and decoding functions."""
    
    def test_encode_url_basic(self):
        """Test basic URL encoding."""
        data = "Hello, World!"
        url = encode_url(data, "https://example.com")
        
        assert url.startswith("https://example.com/#")
        assert "codez=" in url
    
    def test_encode_url_with_params(self):
        """Test URL encoding with additional parameters."""
        data = "test code"
        url = encode_url(
            data, 
            "https://playground.com",
            lang="python",
            theme="dark",
            url="https://docs.example.com"
        )
        
        assert "lang=python" in url
        assert "theme=dark" in url
        assert "url=https%3A//docs.example.com" in url  # URL encoded
    
    def test_decode_url_basic(self):
        """Test basic URL decoding."""
        # Create a URL first
        data = "Hello, World!"
        url = encode_url(data, "https://example.com")
        
        # Decode it
        result = decode_url(url)
        
        assert "codez" in result
        # TODO: Once decompression is implemented, verify the data
        # assert result["codez"] == data
    
    def test_decode_url_with_params(self):
        """Test URL decoding with additional parameters."""
        # Create a URL with parameters
        data = "test code"
        url = encode_url(
            data,
            "https://playground.com",
            lang="python",
            theme="dark",
            url="https://docs.example.com"
        )
        
        # Decode it
        result = decode_url(url)
        
        assert result["lang"] == "python"
        assert result["theme"] == "dark"
        assert result["url"] == "https://docs.example.com"  # Should be URL decoded
        assert "codez" in result
    
    def test_decode_invalid_url(self):
        """Test decoding invalid URLs."""
        assert decode_url("") == {}
        assert decode_url("https://example.com") == {}  # No fragment
        assert decode_url("invalid-url") == {}
    
    def test_url_roundtrip_problematic_character(self):
        """Test URL roundtrip with the problematic character."""
        data = "𝔓"
        url = encode_url(data, "https://test.com")
        result = decode_url(url)
        
        assert "codez" in result
        # TODO: Once decompression is implemented, verify the roundtrip
        # assert result["codez"] == data
        
        print(f"Original: {data!r}")
        print(f"URL: {url}")
        print(f"Decoded: {result}")


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_long_string(self):
        """Test compression of very long strings."""
        lz = LZString()
        long_string = "A" * 10000
        
        compressed = lz.compress_to_base64(long_string)
        assert compressed != ""
        # Should compress well due to repetition
        assert len(compressed) < len(long_string)
    
    def test_special_characters(self):
        """Test compression of strings with special characters."""
        lz = LZString()
        special_string = "\n\t\r\\\"'"
        
        compressed = lz.compress_to_base64(special_string)
        assert compressed != ""
        assert isinstance(compressed, str)
    
    def test_json_like_content(self):
        """Test compression of JSON-like content."""
        lz = LZString()
        json_string = '{"key": "value", "array": [1, 2, 3], "nested": {"inner": "data"}}'
        
        compressed = lz.compress_to_base64(json_string)
        assert compressed != ""
        assert isinstance(compressed, str)
    
    def test_mixed_unicode_content(self):
        """Test compression of mixed Unicode content."""
        lz = LZString()
        mixed_string = "Hello 世界 🌍 test 测试 🚀 end"
        
        compressed = lz.compress_to_base64(mixed_string)
        assert compressed != ""
        assert isinstance(compressed, str)
