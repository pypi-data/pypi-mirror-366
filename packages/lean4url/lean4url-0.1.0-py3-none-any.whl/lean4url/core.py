"""
Core lzstring compression implementation with JavaScript compatibility.

This module provides the LZString class that implements the lzstring compression
algorithm with full compatibility to the JavaScript pieroxy/lz-string library.
The key difference from existing Python implementations is the correct handling
of Unicode characters by mimicking JavaScript's UTF-16 surrogate pair behavior.

Author: Rex Wang
"""

import struct
import math
from typing import Dict, List, Optional, Union
from .constants import BASE64_CHARS


class LZString:
    """
    LZString compression implementation compatible with JavaScript pieroxy/lz-string.
    
    This implementation correctly handles Unicode characters by mimicking JavaScript's
    UTF-16 encoding behavior, ensuring 100% compatibility with the original JavaScript
    implementation.
    """
    
    def __init__(self):
        """Initialize LZString compressor."""
        self._base64_chars = BASE64_CHARS
        self._base64_map = {char: i for i, char in enumerate(self._base64_chars)}
    
    def compress_to_base64(self, input_str: str) -> str:
        """
        Compress string to Base64 format, compatible with JavaScript implementation.
        
        Args:
            input_str: Input string to compress
            
        Returns:
            Base64-encoded compressed string
            
        Example:
            >>> lz = LZString()
            >>> lz.compress_to_base64("𝔓")
            'qwbmRdo='
        """
        if input_str is None:
            return ""
        if input_str == "":
            return ""
            
        # Convert to UTF-16 representation to match JavaScript behavior
        utf16_string = self._to_utf16_string(input_str)
        
        # Use the corrected compression algorithm
        res = self._compress(utf16_string, 6, lambda a: self._base64_chars[a])
        
        # Add proper Base64 padding
        end = len(res) % 4
        if end > 0:
            res += "=" * (4 - end)
        return res
    
    def decompress_from_base64(self, input_str: str) -> str:
        """
        Decompress Base64-encoded string.
        
        Args:
            input_str: Base64-encoded compressed string
            
        Returns:
            Decompressed original string
        """
        if input_str is None:
            return ""
        if input_str == "":
            return ""
            
        try:
            # Decompress to UTF-16 string
            utf16_result = self._decompress(len(input_str), 32, 
                                          lambda index: self._get_base_value(input_str[index]))
            if utf16_result is None:
                return ""
            
            # Convert from UTF-16 representation back to proper string
            return self._from_utf16_string(utf16_result)
        except Exception:
            return ""
    
    def compress_to_utf16(self, input_str: str) -> str:
        """
        Compress string to UTF16 format.
        
        Args:
            input_str: Input string to compress
            
        Returns:
            UTF16-encoded compressed string
        """
        if input_str is None:
            return ""
        if input_str == "":
            return ""
            
        # Convert to UTF-16 representation to match JavaScript behavior
        utf16_string = self._to_utf16_string(input_str)
        
        return self._compress(utf16_string, 15, lambda a: chr(a + 32)) + " "
    
    def decompress_from_utf16(self, input_str: str) -> str:
        """
        Decompress UTF16-encoded string.
        
        Args:
            input_str: UTF16-encoded compressed string
            
        Returns:
            Decompressed original string
        """
        if input_str is None:
            return ""
        if input_str == "":
            return ""
            
        try:
            utf16_result = self._decompress(len(input_str), 16384, 
                                          lambda index: ord(input_str[index]) - 32)
            if utf16_result is None:
                return ""
            
            return self._from_utf16_string(utf16_result)
        except Exception:
            return ""
    
    def _to_utf16_string(self, input_str: str) -> str:
        """
        Convert Python string to UTF-16 character sequence to match JavaScript behavior.
        
        This is the key method that ensures compatibility with JavaScript.
        JavaScript treats strings as sequences of UTF-16 code units, so characters
        outside the Basic Multilingual Plane (BMP) are represented as surrogate pairs.
        
        Args:
            input_str: Input string
            
        Returns:
            String where each character represents a UTF-16 code unit
        """
        # Encode string as UTF-16 Big Endian (without BOM)
        encoded_bytes = input_str.encode('utf-16be')
        
        # Convert bytes to 16-bit unsigned integers
        code_units = []
        for i in range(0, len(encoded_bytes), 2):
            high_byte = encoded_bytes[i]
            low_byte = encoded_bytes[i + 1]
            code_unit = (high_byte << 8) | low_byte
            code_units.append(code_unit)
        
        # Convert code units to characters (this mimics JavaScript behavior)
        return ''.join(chr(unit) for unit in code_units)
    
    def _from_utf16_string(self, utf16_string: str) -> str:
        """
        Convert UTF-16 character sequence back to proper Python string.
        
        Args:
            utf16_string: String where each character represents a UTF-16 code unit
            
        Returns:
            Reconstructed proper Unicode string
        """
        # Convert characters back to code units
        code_units = [ord(c) for c in utf16_string]
        
        # Pack as bytes
        utf16_bytes = b''
        for unit in code_units:
            utf16_bytes += struct.pack('>H', unit)
        
        # Decode as UTF-16 BE
        return utf16_bytes.decode('utf-16be')
    
    def _get_base_value(self, character: str) -> int:
        """Get the base value for a Base64 character."""
        if character in self._base64_map:
            return self._base64_map[character]
        return 0
    
    def _compress(self, uncompressed: str, bits_per_char: int, get_char_from_int) -> str:
        """
        Core compression algorithm based on the existing lzstring package.
        
        This implements the LZ78-based compression algorithm used by lzstring.
        
        Args:
            uncompressed: Input string (already converted to UTF-16 representation)
            bits_per_char: Number of bits per character
            get_char_from_int: Function to convert integer to character
            
        Returns:
            Compressed string
        """
        if uncompressed is None:
            return ""
            
        context_dictionary = {}
        context_dictionary_to_create = {}
        context_c = ""
        context_wc = ""
        context_w = ""
        context_enlarge_in = 2  # Compensate for the first entry which should not count
        context_dict_size = 3
        context_num_bits = 2
        context_data = []
        context_data_val = 0
        context_data_position = 0

        for ii in range(len(uncompressed)):
            context_c = uncompressed[ii]
            if context_c not in context_dictionary:
                context_dictionary[context_c] = context_dict_size
                context_dict_size += 1
                context_dictionary_to_create[context_c] = True

            context_wc = context_w + context_c
            if context_wc in context_dictionary:
                context_w = context_wc
            else:
                if context_w in context_dictionary_to_create:
                    if ord(context_w[0]) < 256:
                        for i in range(context_num_bits):
                            context_data_val = (context_data_val << 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                        value = ord(context_w[0])
                        for i in range(8):
                            context_data_val = (context_data_val << 1) | (value & 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = value >> 1

                    else:
                        value = 1
                        for i in range(context_num_bits):
                            context_data_val = (context_data_val << 1) | value
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = 0
                        value = ord(context_w[0])
                        for i in range(16):
                            context_data_val = (context_data_val << 1) | (value & 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = value >> 1
                    context_enlarge_in -= 1
                    if context_enlarge_in == 0:
                        context_enlarge_in = int(math.pow(2, context_num_bits))
                        context_num_bits += 1
                    del context_dictionary_to_create[context_w]
                else:
                    value = context_dictionary[context_w]
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1

                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = int(math.pow(2, context_num_bits))
                    context_num_bits += 1
                
                # Add wc to the dictionary.
                context_dictionary[context_wc] = context_dict_size
                context_dict_size += 1
                context_w = str(context_c)

        # Output the code for w.
        if context_w != "":
            if context_w in context_dictionary_to_create:
                if ord(context_w[0]) < 256:
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                    value = ord(context_w[0])
                    for i in range(8):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                else:
                    value = 1
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1) | value
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = 0
                    value = ord(context_w[0])
                    for i in range(16):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = int(math.pow(2, context_num_bits))
                    context_num_bits += 1
                del context_dictionary_to_create[context_w]
            else:
                value = context_dictionary[context_w]
                for i in range(context_num_bits):
                    context_data_val = (context_data_val << 1) | (value & 1)
                    if context_data_position == bits_per_char - 1:
                        context_data_position = 0
                        context_data.append(get_char_from_int(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = value >> 1

        context_enlarge_in -= 1
        if context_enlarge_in == 0:
            context_enlarge_in = int(math.pow(2, context_num_bits))
            context_num_bits += 1

        # Mark the end of the stream
        value = 2
        for i in range(context_num_bits):
            context_data_val = (context_data_val << 1) | (value & 1)
            if context_data_position == bits_per_char - 1:
                context_data_position = 0
                context_data.append(get_char_from_int(context_data_val))
                context_data_val = 0
            else:
                context_data_position += 1
            value = value >> 1

        # Flush the last char
        while True:
            context_data_val = (context_data_val << 1)
            if context_data_position == bits_per_char - 1:
                context_data.append(get_char_from_int(context_data_val))
                break
            else:
               context_data_position += 1

        return "".join(context_data)
    
    def _decompress(self, length: int, reset_value: int, get_next_value) -> str:
        """
        Core decompression algorithm based on the existing lzstring package.
        
        Args:
            length: Length of the compressed data
            reset_value: Reset value for bit reading
            get_next_value: Function to get next value from compressed data
            
        Returns:
            Decompressed UTF-16 string
        """
        dictionary = {}
        enlarge_in = 4
        dict_size = 4
        num_bits = 3
        entry = ""
        result = []

        class DataObject:
            def __init__(self, val, position, index):
                self.val = val
                self.position = position
                self.index = index

        data = DataObject(
            val=get_next_value(0),
            position=reset_value,
            index=1
        )

        for i in range(3):
            dictionary[i] = i

        bits = 0
        maxpower = int(math.pow(2, 2))
        power = 1

        while power != maxpower:
            resb = data.val & data.position
            data.position >>= 1
            if data.position == 0:
                data.position = reset_value
                data.val = get_next_value(data.index)
                data.index += 1

            bits |= power if resb > 0 else 0
            power <<= 1

        next_val = bits
        if next_val == 0:
            bits = 0
            maxpower = int(math.pow(2, 8))
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1
            c = chr(bits)
        elif next_val == 1:
            bits = 0
            maxpower = int(math.pow(2, 16))
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1
            c = chr(bits)
        elif next_val == 2:
            return ""
        else:
            return ""

        dictionary[3] = c
        w = c
        result.append(c)
        counter = 0
        while True:
            counter += 1
            if data.index > length:
                return ""

            bits = 0
            maxpower = int(math.pow(2, num_bits))
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1

            c = bits
            if c == 0:
                bits = 0
                maxpower = int(math.pow(2, 8))
                power = 1
                while power != maxpower:
                    resb = data.val & data.position
                    data.position >>= 1
                    if data.position == 0:
                        data.position = reset_value
                        data.val = get_next_value(data.index)
                        data.index += 1
                    bits |= power if resb > 0 else 0
                    power <<= 1

                dictionary[dict_size] = chr(bits)
                dict_size += 1
                c = dict_size - 1
                enlarge_in -= 1
            elif c == 1:
                bits = 0
                maxpower = int(math.pow(2, 16))
                power = 1
                while power != maxpower:
                    resb = data.val & data.position
                    data.position >>= 1
                    if data.position == 0:
                        data.position = reset_value
                        data.val = get_next_value(data.index)
                        data.index += 1
                    bits |= power if resb > 0 else 0
                    power <<= 1
                dictionary[dict_size] = chr(bits)
                dict_size += 1
                c = dict_size - 1
                enlarge_in -= 1
            elif c == 2:
                return "".join(result)

            if enlarge_in == 0:
                enlarge_in = int(math.pow(2, num_bits))
                num_bits += 1

            if c in dictionary:
                entry = dictionary[c]
            else:
                if c == dict_size:
                    entry = w + w[0]
                else:
                    return ""
                    
            result.append(entry)

            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            enlarge_in -= 1

            w = entry
            if enlarge_in == 0:
                enlarge_in = int(math.pow(2, num_bits))
                num_bits += 1

        return "".join(result)
