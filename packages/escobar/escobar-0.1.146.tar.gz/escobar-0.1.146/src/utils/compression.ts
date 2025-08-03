/**
 * Compression utilities for handling large messages
 * Uses pako for gzip compression and browser's native base64 encoding
 */

import * as pako from 'pako';

/**
 * Error class for compression-related errors
 */
export class CompressionError extends Error {
    constructor(message: string, public readonly operation: string) {
        super(message);
        this.name = 'CompressionError';
    }
}


/**
 * Compress a string using gzip and return binary data
 * @param input The string to compress
 * @returns Compressed binary data as Uint8Array
 * @throws CompressionError if compression fails
 */
export function compressString(input: string): Uint8Array {
    const timestamp = new Date().toISOString();
    console.log(`[compressString] ${timestamp} Starting BINARY compression:`, {
        inputLength: input.length,
        inputType: typeof input,
        inputPreview: input.substring(0, 100) + (input.length > 100 ? '...' : ''),
        inputCharCodes: input.substring(0, 20).split('').map(c => c.charCodeAt(0))
    });

    try {
        // Step 1: Convert string to UTF-8 bytes
        console.log(`[compressString] ${timestamp} Step 1: Converting to UTF-8 bytes`);
        const utf8Bytes = new TextEncoder().encode(input);

        console.log(`[compressString] ${timestamp} UTF-8 conversion complete:`, {
            originalStringLength: input.length,
            utf8BytesLength: utf8Bytes.length,
            utf8BytesType: utf8Bytes.constructor.name,
            firstFewBytes: Array.from(utf8Bytes.slice(0, 20)),
            compressionPotential: utf8Bytes.length > 1024 ? 'Good (>1KB)' : 'Poor (<1KB)'
        });

        // Step 2: Compress using gzip (final step - no base64!)
        console.log(`[compressString] ${timestamp} Step 2: Compressing with pako.gzip (FINAL STEP)`);
        const compressed = pako.gzip(utf8Bytes);

        console.log(`[compressString] ${timestamp} BINARY Compression SUCCESS:`, {
            originalStringLength: input.length,
            originalBytesLength: utf8Bytes.length,
            compressedBytesLength: compressed.length,
            compressedType: compressed.constructor.name,
            compressionRatio: ((1 - compressed.length / utf8Bytes.length) * 100).toFixed(2) + '%',
            compressionEffective: compressed.length < utf8Bytes.length,
            firstFewCompressedBytes: Array.from(compressed.slice(0, 20)),
            pipeline: 'string → UTF-8 → gzip (BINARY OUTPUT)',
            sizeSavings: `${utf8Bytes.length} → ${compressed.length} bytes`
        });

        return compressed;
    } catch (error) {
        console.error(`[compressString] ${timestamp} FATAL ERROR:`, {
            error,
            errorMessage: error instanceof Error ? error.message : 'Unknown error',
            errorStack: error instanceof Error ? error.stack : 'No stack trace',
            inputLength: input.length,
            operation: 'compress'
        });

        throw new CompressionError(
            `Failed to compress string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'compress'
        );
    }
}

/**
 * Encode a string as base64
 * @param input The string to encode
 * @returns Base64-encoded string
 * @throws CompressionError if encoding fails
 */
export function encodeBase64(input: string): string {
    try {
        // Handle UTF-8 properly by first encoding to bytes then to base64
        const utf8Bytes = new TextEncoder().encode(input);

        // Convert bytes to binary string for btoa
        let binaryString = '';
        for (let i = 0; i < utf8Bytes.length; i++) {
            binaryString += String.fromCharCode(utf8Bytes[i]);
        }

        const base64 = btoa(binaryString);
        return base64;
    } catch (error) {
        throw new CompressionError(
            `Failed to encode string as base64: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'encode'
        );
    }
}

/**
 * Decompress binary gzip data
 * @param input Compressed binary data as Uint8Array
 * @returns Decompressed original string
 * @throws CompressionError if decompression fails
 */
export function decompressBinary(input: Uint8Array): string {
    try {
        // Decompress using gzip
        const decompressed = pako.ungzip(input);

        // Convert back to string
        const result = new TextDecoder().decode(decompressed);

        return result;
    } catch (error) {
        throw new CompressionError(
            `Failed to decompress binary data: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'decompress'
        );
    }
}

/**
 * Decompress a base64-encoded gzip string (legacy function)
 * @param input Base64-encoded compressed string
 * @returns Decompressed original string
 * @throws CompressionError if decompression fails
 */
export function decompressString(input: string): string {
    try {
        // Decode from base64
        const binaryString = atob(input);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Decompress using gzip
        const decompressed = pako.ungzip(bytes);

        // Convert back to string
        const result = new TextDecoder().decode(decompressed);

        return result;
    } catch (error) {
        throw new CompressionError(
            `Failed to decompress string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'decompress'
        );
    }
}

/**
 * Decode a base64-encoded string
 * @param input Base64-encoded string
 * @returns Decoded original string
 * @throws CompressionError if decoding fails
 */
export function decodeBase64(input: string): string {
    try {
        // Decode from base64
        const binaryString = atob(input);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Convert back to string
        const result = new TextDecoder().decode(bytes);

        return result;
    } catch (error) {
        throw new CompressionError(
            `Failed to decode base64 string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'decode'
        );
    }
}

/**
 * Calculate compression ratio for a given string
 * @param original The original string
 * @param compressed The compressed base64 string
 * @returns Compression ratio as a percentage (0-100)
 */
export function getCompressionRatio(original: string, compressed: string): number {
    const originalSize = new TextEncoder().encode(original).length;
    const compressedSize = new TextEncoder().encode(compressed).length;

    if (originalSize === 0) {
        return 0;
    }

    return Math.round((1 - compressedSize / originalSize) * 100);
}

/**
 * Utility function to determine if compression would be beneficial
 * @param input The string to potentially compress
 * @param threshold Minimum size in bytes to consider compression (default: 1024)
 * @returns True if compression is recommended
 */
export function shouldCompress(input: string, threshold: number = 1024): boolean {
    const size = new TextEncoder().encode(input).length;
    return size >= threshold;
}

/**
 * Compress string only if it would be beneficial
 * @param input The string to potentially compress
 * @param threshold Minimum size in bytes to consider compression (default: 1024)
 * @returns Object with compressed data and metadata
 */
export function smartCompress(input: string, threshold: number = 1024): {
    data: string | Uint8Array;
    compressed: boolean;
    originalSize: number;
    finalSize: number;
    ratio?: number;
} {
    const originalSize = new TextEncoder().encode(input).length;

    if (!shouldCompress(input, threshold)) {
        return {
            data: input,
            compressed: false,
            originalSize,
            finalSize: originalSize
        };
    }

    try {
        const compressed = compressString(input);
        const finalSize = compressed.length; // Binary data length
        const ratio = Math.round((1 - finalSize / originalSize) * 100);

        // Only use compression if it actually reduces size significantly
        if (finalSize < originalSize * 0.9) {
            return {
                data: compressed,
                compressed: true,
                originalSize,
                finalSize,
                ratio
            };
        } else {
            // Compression didn't help much, return original
            return {
                data: input,
                compressed: false,
                originalSize,
                finalSize: originalSize
            };
        }
    } catch (error) {
        // If compression fails, return original
        return {
            data: input,
            compressed: false,
            originalSize,
            finalSize: originalSize
        };
    }
}
