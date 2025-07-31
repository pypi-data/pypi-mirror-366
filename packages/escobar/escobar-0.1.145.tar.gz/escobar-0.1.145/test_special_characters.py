#!/usr/bin/env python3
"""
Comprehensive test for special character handling in the compression pipeline.
This verifies that all types of special characters are processed properly.
"""

import base64
import gzip
import json
import unicodedata


def decompress_gzip_base64(compressed_data: str) -> str:
    """Decompress base64-encoded gzip data."""
    compressed_bytes = base64.b64decode(compressed_data)
    decompressed_bytes = gzip.decompress(compressed_bytes)
    return decompressed_bytes.decode('utf-8')


def analyze_character(char):
    """Analyze a character and return detailed information."""
    try:
        return {
            'char': char,
            'unicode_name': unicodedata.name(char, 'UNKNOWN'),
            'category': unicodedata.category(char),
            'codepoint': f'U+{ord(char):04X}',
            'utf8_bytes': char.encode('utf-8').hex(),
            'byte_length': len(char.encode('utf-8'))
        }
    except Exception as e:
        return {
            'char': char,
            'error': str(e),
            'utf8_bytes': char.encode('utf-8').hex(),
            'byte_length': len(char.encode('utf-8'))
        }


def test_special_characters():
    """Test comprehensive special character handling."""
    
    print("🔍 SPECIAL CHARACTER PROCESSING TEST")
    print("=" * 70)
    print("Testing that special characters are processed properly through:")
    print("JavaScript compression → Python decompression")
    print("=" * 70)
    
    # Load the actual test data to see what special characters we have
    with open('compression_test_data.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Find the Unicode test case
    unicode_case = next(case for case in test_data['testCases'] if 'Unicode String' in case['name'])
    
    original = unicode_case['original']
    compressed = unicode_case['compressed']
    decompressed = decompress_gzip_base64(compressed)
    
    print(f"📝 Test String: {repr(original)}")
    print(f"📝 Decompressed: {repr(decompressed)}")
    print(f"✅ Strings Match: {original == decompressed}")
    print()
    
    # Analyze each special character
    print("🔍 CHARACTER-BY-CHARACTER ANALYSIS:")
    print("-" * 70)
    
    special_chars = []
    for char in original:
        if ord(char) > 127:  # Non-ASCII characters
            special_chars.append(char)
    
    # Remove duplicates while preserving order
    unique_special_chars = []
    for char in special_chars:
        if char not in unique_special_chars:
            unique_special_chars.append(char)
    
    for i, char in enumerate(unique_special_chars, 1):
        info = analyze_character(char)
        print(f"{i}. Character: '{char}'")
        print(f"   Unicode Name: {info.get('unicode_name', 'N/A')}")
        print(f"   Category: {info.get('category', 'N/A')}")
        print(f"   Codepoint: {info.get('codepoint', 'N/A')}")
        print(f"   UTF-8 Bytes: {info['utf8_bytes']}")
        print(f"   Byte Length: {info['byte_length']}")
        
        # Check if this character survived the round-trip
        if char in decompressed:
            print(f"   ✅ PRESERVED: Character found in decompressed string")
        else:
            print(f"   ❌ LOST: Character missing from decompressed string")
        print()
    
    # Byte-level comparison
    print("🔢 BYTE-LEVEL VERIFICATION:")
    print("-" * 70)
    
    original_bytes = original.encode('utf-8')
    decompressed_bytes = decompressed.encode('utf-8')
    
    print(f"Original UTF-8 bytes:     {original_bytes.hex()}")
    print(f"Decompressed UTF-8 bytes: {decompressed_bytes.hex()}")
    print(f"Bytes identical:          {original_bytes == decompressed_bytes}")
    print()
    
    if original_bytes != decompressed_bytes:
        print("❌ BYTE DIFFERENCE DETECTED:")
        for i, (orig, decomp) in enumerate(zip(original_bytes, decompressed_bytes)):
            if orig != decomp:
                print(f"   Position {i}: {orig:02x} → {decomp:02x}")
    
    # Test additional challenging special characters
    print("🧪 ADDITIONAL SPECIAL CHARACTER TESTS:")
    print("-" * 70)
    
    challenging_strings = [
        "Emoji: 🚀🌟⭐🎉🔥💯",
        "Math: ∑∏∫∆∇∂√∞≠≤≥±×÷",
        "Arrows: ←→↑↓↔↕⇐⇒⇑⇓",
        "Currency: $€£¥₹₽₿¢",
        "Accents: àáâãäåæçèéêëìíîïñòóôõöøùúûüý",
        "Greek: αβγδεζηθικλμνξοπρστυφχψω",
        "Cyrillic: абвгдежзийклмнопрстуфхцчшщъыьэюя",
        "Arabic: العربية اللغة العربية",
        "Chinese: 中文汉字简体繁體",
        "Japanese: ひらがな カタカナ 漢字",
        "Korean: 한글 조선글",
        "Mixed: Hello🌍世界مرحبا🚀Test",
        "Control chars: \t\n\r\x00\x01\x02",
        "Quotes: \"'`''""«»‹›",
        "Symbols: ©®™§¶†‡•…‰‱°′″‴",
    ]
    
    all_passed = True
    
    for i, test_string in enumerate(challenging_strings, 1):
        print(f"{i}. Testing: {repr(test_string)}")
        
        try:
            # Simulate JavaScript compression (using Node.js zlib which is equivalent)
            import subprocess
            import tempfile
            import os
            
            # Create a temporary Node.js script to compress the string
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(f'''
const zlib = require('zlib');
const input = {json.dumps(test_string)};
const utf8Bytes = Buffer.from(input, 'utf8');
const compressed = zlib.gzipSync(utf8Bytes);
const base64 = compressed.toString('base64');
console.log(base64);
''')
                temp_file = f.name
            
            # Run Node.js to get compressed data
            result = subprocess.run(['node', temp_file], capture_output=True, text=True)
            os.unlink(temp_file)
            
            if result.returncode == 0:
                compressed_data = result.stdout.strip()
                
                # Decompress using Python
                decompressed_result = decompress_gzip_base64(compressed_data)
                
                if decompressed_result == test_string:
                    print(f"   ✅ PASS: Round-trip successful")
                else:
                    print(f"   ❌ FAIL: Round-trip failed")
                    print(f"      Expected: {repr(test_string)}")
                    print(f"      Got:      {repr(decompressed_result)}")
                    all_passed = False
            else:
                print(f"   ❌ FAIL: Compression failed: {result.stderr}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("🎉 ALL SPECIAL CHARACTERS PROCESSED CORRECTLY!")
        print("✅ Every special character survived the JavaScript → Python round-trip")
    else:
        print("❌ SOME SPECIAL CHARACTERS FAILED PROCESSING")
    
    return all_passed


if __name__ == '__main__':
    success = test_special_characters()
    exit(0 if success else 1)
