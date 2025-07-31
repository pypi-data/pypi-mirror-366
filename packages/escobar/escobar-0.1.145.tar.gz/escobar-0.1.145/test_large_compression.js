/**
 * Test script to verify that the stack-safe compression can handle very large strings
 * This tests the specific issue where String.fromCharCode(...array) was failing on 10MB+ data
 */

// Import the compression functions (simulating the TypeScript implementation)
const fs = require('fs');
const zlib = require('zlib');

// Stack-safe version of uint8ArrayToString (matching the TypeScript implementation)
function uint8ArrayToString(bytes) {
    const CHUNK_SIZE = 8192; // Process in 8KB chunks to avoid stack overflow
    let result = '';

    for (let i = 0; i < bytes.length; i += CHUNK_SIZE) {
        const chunk = bytes.slice(i, i + CHUNK_SIZE);
        result += String.fromCharCode(...chunk);
    }

    return result;
}

// Stack-safe compression function (matching the TypeScript implementation)
function compressStringStackSafe(input) {
    try {
        // Convert string to UTF-8 bytes
        const utf8Bytes = Buffer.from(input, 'utf8');

        // Compress using gzip
        const compressed = zlib.gzipSync(utf8Bytes);

        // Convert to base64 using stack-safe method
        const base64 = Buffer.from(uint8ArrayToString(compressed), 'binary').toString('base64');

        return base64;
    } catch (error) {
        throw new Error(`Failed to compress string: ${error.message}`);
    }
}

// Old problematic version (for comparison)
function compressStringOld(input) {
    try {
        const utf8Bytes = Buffer.from(input, 'utf8');
        const compressed = zlib.gzipSync(utf8Bytes);

        // This will fail on large arrays due to call stack size
        const base64 = Buffer.from(String.fromCharCode(...compressed), 'binary').toString('base64');

        return base64;
    } catch (error) {
        throw new Error(`Failed to compress string: ${error.message}`);
    }
}

function testLargeStringCompression() {
    console.log('🧪 Testing Large String Compression (Stack Safety)');
    console.log('=' * 60);

    // Test with progressively larger strings
    const testSizes = [
        { name: '1MB', size: 1024 * 1024 },
        { name: '5MB', size: 5 * 1024 * 1024 },
        { name: '10MB', size: 10 * 1024 * 1024 },
        { name: '20MB', size: 20 * 1024 * 1024 }
    ];

    for (const testSize of testSizes) {
        console.log(`\n📏 Testing ${testSize.name} (${testSize.size.toLocaleString()} bytes)`);

        // Create a large string with some pattern (compressible)
        const pattern = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ';
        const repetitions = Math.ceil(testSize.size / pattern.length);
        const largeString = pattern.repeat(repetitions).substring(0, testSize.size);

        console.log(`   📝 Generated string: ${largeString.length.toLocaleString()} characters`);

        // Test old method (should fail on large sizes)
        console.log('   🔴 Testing OLD method (String.fromCharCode(...array)):');
        try {
            const startTime = Date.now();
            const compressedOld = compressStringOld(largeString);
            const endTime = Date.now();
            console.log(`      ✅ SUCCESS: Compressed to ${compressedOld.length} chars in ${endTime - startTime}ms`);
        } catch (error) {
            console.log(`      ❌ FAILED: ${error.message}`);
        }

        // Test new stack-safe method
        console.log('   🟢 Testing NEW method (stack-safe chunks):');
        try {
            const startTime = Date.now();
            const compressedNew = compressStringStackSafe(largeString);
            const endTime = Date.now();
            console.log(`      ✅ SUCCESS: Compressed to ${compressedNew.length} chars in ${endTime - startTime}ms`);

            // Verify decompression works
            const decompressed = zlib.gunzipSync(Buffer.from(compressedNew, 'base64')).toString('utf8');
            if (decompressed === largeString) {
                console.log(`      ✅ VERIFIED: Round-trip successful`);
            } else {
                console.log(`      ❌ FAILED: Round-trip verification failed`);
            }

        } catch (error) {
            console.log(`      ❌ FAILED: ${error.message}`);
        }
    }

    console.log('\n' + '=' * 60);
    console.log('🎯 Test completed! The stack-safe method should handle all sizes.');
}

// Run the test
testLargeStringCompression();
