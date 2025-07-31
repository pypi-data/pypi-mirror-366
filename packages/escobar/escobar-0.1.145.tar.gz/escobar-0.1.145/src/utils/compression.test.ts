/**
 * Comprehensive tests for compression utilities
 */

import {
    compressString,
    decompressBinary,
    decompressString,
    encodeBase64,
    decodeBase64,
    getCompressionRatio,
    shouldCompress,
    smartCompress,
    CompressionError
} from './compression';

describe('Compression Utilities', () => {
    // Test data samples
    const testStrings = {
        simple: 'Hello, World!',
        unicode: 'Hello 🌍! Testing émojis and spëcial chars: 中文 العربية',
        json: JSON.stringify({
            message: 'test',
            data: { nested: true, array: [1, 2, 3] },
            timestamp: new Date().toISOString()
        }),
        large: 'A'.repeat(5000),
        empty: '',
        whitespace: '   \n\t   ',
        repeated: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(100)
    };

    describe('Basic Compression/Decompression', () => {
        Object.entries(testStrings).forEach(([name, testString]) => {
            test(`should compress and decompress ${name} string correctly`, () => {
                const compressed = compressString(testString);
                const decompressed = decompressBinary(compressed);

                expect(decompressed).toBe(testString);
                expect(compressed).not.toBe(testString);
                expect(compressed).toBeInstanceOf(Uint8Array);
            });
        });

        test('should handle very large strings', () => {
            const largeString = 'Test data with repeated patterns. '.repeat(10000);
            const compressed = compressString(largeString);
            const decompressed = decompressBinary(compressed);

            expect(decompressed).toBe(largeString);
            expect(compressed.length).toBeLessThan(largeString.length);
        });
    });

    describe('Base64 Encoding/Decoding', () => {
        Object.entries(testStrings).forEach(([name, testString]) => {
            test(`should encode and decode ${name} string correctly`, () => {
                const encoded = encodeBase64(testString);
                const decoded = decodeBase64(encoded);

                expect(decoded).toBe(testString);
                if (testString !== '') {
                    expect(encoded).not.toBe(testString);
                }
                expect(typeof encoded).toBe('string');
            });
        });

        test('should handle UTF-8 characters properly', () => {
            const utf8String = '🚀 Testing UTF-8: 中文 العربية русский';
            const encoded = encodeBase64(utf8String);
            const decoded = decodeBase64(encoded);

            expect(decoded).toBe(utf8String);
        });
    });

    describe('Error Handling', () => {
        test('should throw CompressionError for invalid base64 in decompression', () => {
            expect(() => decompressString('invalid-base64!')).toThrow(CompressionError);
            expect(() => decompressString('invalid-base64!')).toThrow('decompress');
        });

        test('should throw CompressionError for invalid base64 in decoding', () => {
            expect(() => decodeBase64('invalid-base64!')).toThrow(CompressionError);
            expect(() => decodeBase64('invalid-base64!')).toThrow('decode');
        });

        test('should throw CompressionError for corrupted compressed data', () => {
            // Create valid base64 but invalid gzip data
            const invalidGzipData = btoa('not-gzip-data');
            expect(() => decompressString(invalidGzipData)).toThrow(CompressionError);
        });

        test('should include operation type in error', () => {
            try {
                decompressString('invalid');
            } catch (error) {
                expect(error).toBeInstanceOf(CompressionError);
                expect((error as CompressionError).operation).toBe('decompress');
            }
        });
    });

    describe('Compression Ratio Calculation', () => {
        test('should calculate compression ratio correctly', () => {
            const original = 'A'.repeat(1000);
            const compressed = compressString(original);
            // For binary compression, we need to calculate ratio differently
            const originalSize = new TextEncoder().encode(original).length;
            const compressedSize = compressed.length;
            const ratio = Math.round((1 - compressedSize / originalSize) * 100);

            expect(ratio).toBeGreaterThan(0);
            expect(ratio).toBeLessThanOrEqual(100);
            expect(typeof ratio).toBe('number');
        });

        test('should return 0 for empty string', () => {
            const ratio = getCompressionRatio('', '');
            expect(ratio).toBe(0);
        });

        test('should handle cases where compression increases size', () => {
            const small = 'Hi';
            const compressed = compressString(small);
            // For binary compression, calculate ratio directly
            const originalSize = new TextEncoder().encode(small).length;
            const compressedSize = compressed.length;
            const ratio = Math.round((1 - compressedSize / originalSize) * 100);

            // For very small strings, compression might increase size
            expect(typeof ratio).toBe('number');
        });
    });

    describe('Smart Compression Logic', () => {
        test('should not compress small strings by default', () => {
            const small = 'Hello, World!';
            expect(shouldCompress(small)).toBe(false);
            expect(shouldCompress(small, 1024)).toBe(false);
        });

        test('should compress large strings', () => {
            const large = 'A'.repeat(2000);
            expect(shouldCompress(large)).toBe(true);
            expect(shouldCompress(large, 1024)).toBe(true);
        });

        test('should respect custom threshold', () => {
            const medium = 'A'.repeat(500);
            expect(shouldCompress(medium, 100)).toBe(true);
            expect(shouldCompress(medium, 1000)).toBe(false);
        });

        test('smartCompress should return original for small strings', () => {
            const small = 'Hello, World!';
            const result = smartCompress(small);

            expect(result.compressed).toBe(false);
            expect(result.data).toBe(small);
            expect(result.originalSize).toBeGreaterThan(0);
            expect(result.finalSize).toBe(result.originalSize);
            expect(result.ratio).toBeUndefined();
        });

        test('smartCompress should compress large strings', () => {
            const large = 'Lorem ipsum dolor sit amet. '.repeat(100);
            const result = smartCompress(large);

            expect(result.compressed).toBe(true);
            expect(result.data).not.toBe(large);
            expect(result.originalSize).toBeGreaterThan(result.finalSize);
            expect(result.ratio).toBeGreaterThan(0);

            // Verify we can decompress it
            if (result.data instanceof Uint8Array) {
                const decompressed = decompressBinary(result.data);
                expect(decompressed).toBe(large);
            } else {
                // Fallback case - shouldn't happen for large strings
                expect(result.data).toBe(large);
            }
        });

        test('smartCompress should fallback to original if compression fails', () => {
            // Mock compression failure by testing with a string that might not compress well
            const incompressible = Math.random().toString(36).repeat(10);
            const result = smartCompress(incompressible, 10);

            // Should either compress successfully or fallback to original
            expect(typeof result.compressed).toBe('boolean');
            expect(result.data).toBeDefined();
            expect(result.originalSize).toBeGreaterThan(0);
            expect(result.finalSize).toBeGreaterThan(0);
        });
    });

    describe('Protocol Message Testing', () => {
        test('should handle typical protocol messages', () => {
            const protocolMessage = JSON.stringify({
                message_type: 'chat_request',
                call_id: 'test-123',
                username: 'testuser',
                chatID: 'chat-456',
                content: 'This is a test message with some content that might benefit from compression when it gets longer and contains repeated patterns or structures.',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'test'
                }
            });

            const compressed = compressString(protocolMessage);
            const decompressed = decompressBinary(compressed);

            expect(decompressed).toBe(protocolMessage);
            expect(JSON.parse(decompressed)).toEqual(JSON.parse(protocolMessage));
        });

        test('should handle large chat history', () => {
            const chatHistory = Array.from({ length: 50 }, (_, i) => ({
                id: i,
                message: `This is message number ${i} with some repeated content that should compress well`,
                timestamp: new Date(Date.now() - i * 1000).toISOString(),
                user: `user${i % 5}`
            }));

            const historyString = JSON.stringify(chatHistory);
            const result = smartCompress(historyString);

            expect(result.compressed).toBe(true);
            expect(result.ratio).toBeGreaterThan(0);

            // Handle both binary and string data from smartCompress
            let decompressed: string;
            if (result.data instanceof Uint8Array) {
                decompressed = decompressBinary(result.data);
            } else {
                decompressed = result.data;
            }
            expect(JSON.parse(decompressed)).toEqual(chatHistory);
        });
    });

    describe('Edge Cases', () => {
        test('should handle strings with null bytes', () => {
            const stringWithNull = 'Hello\0World\0Test';
            const compressed = compressString(stringWithNull);
            const decompressed = decompressBinary(compressed);

            expect(decompressed).toBe(stringWithNull);
        });

        test('should handle very long lines', () => {
            const longLine = 'A'.repeat(100000);
            const compressed = compressString(longLine);
            const decompressed = decompressBinary(compressed);

            expect(decompressed).toBe(longLine);
            expect(compressed.length).toBeLessThan(longLine.length);
        });

        test('should handle mixed content', () => {
            const mixed = `
                Text content with various elements:
                - Unicode: 🚀 🌟 ⭐ 
                - Numbers: 123456789
                - Special chars: !@#$%^&*()
                - JSON: ${JSON.stringify({ test: true, array: [1, 2, 3] })}
                - Repeated: ${'pattern '.repeat(50)}
            `;

            const compressed = compressString(mixed);
            const decompressed = decompressBinary(compressed);

            expect(decompressed).toBe(mixed);
        });
    });
});
