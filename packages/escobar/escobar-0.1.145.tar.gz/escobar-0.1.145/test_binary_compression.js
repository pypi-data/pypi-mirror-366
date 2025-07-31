/**
 * Test the new binary compression with a large payload to see the benefits
 */

const fs = require('fs');
const zlib = require('zlib');

// Simulate the new binary compression (matching TypeScript implementation)
function compressBinary(input) {
    const utf8Bytes = Buffer.from(input, 'utf8');
    const compressed = zlib.gzipSync(utf8Bytes);
    return compressed; // Return binary directly
}

// Old base64 compression (for comparison)
function compressBase64(input) {
    const utf8Bytes = Buffer.from(input, 'utf8');
    const compressed = zlib.gzipSync(utf8Bytes);
    const base64 = compressed.toString('base64');
    return base64;
}

function testBinaryVsBase64Compression() {
    console.log('🔬 Binary vs Base64 Compression Comparison');
    console.log('=' * 60);

    // Create a large JSON payload similar to what you might send
    const largePayload = JSON.stringify({
        message_type: 'chat_request',
        call_id: 'test-' + Date.now(),
        username: 'testuser',
        chatID: 'chat-' + Math.random(),
        content: 'This is a large message with lots of content. '.repeat(50000), // ~2.5MB
        metadata: {
            timestamp: new Date().toISOString(),
            source: 'test',
            history: Array.from({ length: 1000 }, (_, i) => ({
                id: i,
                message: `Previous message ${i} with some content that repeats patterns`,
                timestamp: new Date(Date.now() - i * 1000).toISOString()
            }))
        }
    });

    console.log(`📊 Original payload size: ${largePayload.length.toLocaleString()} characters`);
    console.log(`📊 Original UTF-8 bytes: ${Buffer.from(largePayload, 'utf8').length.toLocaleString()} bytes`);

    // Test binary compression
    console.log('\n🔵 Testing BINARY compression:');
    const binaryStart = Date.now();
    const binaryCompressed = compressBinary(largePayload);
    const binaryTime = Date.now() - binaryStart;

    console.log(`   📦 Compressed size: ${binaryCompressed.length.toLocaleString()} bytes`);
    console.log(`   ⏱️  Compression time: ${binaryTime}ms`);
    console.log(`   📈 Compression ratio: ${((1 - binaryCompressed.length / Buffer.from(largePayload, 'utf8').length) * 100).toFixed(2)}%`);

    // Test base64 compression
    console.log('\n🔴 Testing BASE64 compression:');
    const base64Start = Date.now();
    const base64Compressed = compressBase64(largePayload);
    const base64Time = Date.now() - base64Start;

    console.log(`   📦 Compressed size: ${base64Compressed.length.toLocaleString()} characters`);
    console.log(`   📦 Compressed bytes: ${Buffer.from(base64Compressed, 'utf8').length.toLocaleString()} bytes`);
    console.log(`   ⏱️  Compression time: ${base64Time}ms`);
    console.log(`   📈 Compression ratio: ${((1 - Buffer.from(base64Compressed, 'utf8').length / Buffer.from(largePayload, 'utf8').length) * 100).toFixed(2)}%`);

    // Comparison
    console.log('\n🏆 COMPARISON:');
    const sizeSavings = Buffer.from(base64Compressed, 'utf8').length - binaryCompressed.length;
    const sizeSavingsPercent = (sizeSavings / Buffer.from(base64Compressed, 'utf8').length * 100).toFixed(2);

    console.log(`   💾 Size savings: ${sizeSavings.toLocaleString()} bytes (${sizeSavingsPercent}% smaller)`);
    console.log(`   ⚡ Speed difference: ${Math.abs(base64Time - binaryTime)}ms ${binaryTime < base64Time ? 'faster' : 'slower'}`);

    // Verify decompression works
    console.log('\n✅ Verification:');
    try {
        const decompressed = zlib.gunzipSync(binaryCompressed).toString('utf8');
        const matches = decompressed === largePayload;
        console.log(`   🔄 Round-trip successful: ${matches}`);
        if (!matches) {
            console.log(`   ❌ Length mismatch: ${decompressed.length} vs ${largePayload.length}`);
        }
    } catch (error) {
        console.log(`   ❌ Decompression failed: ${error.message}`);
    }

    console.log('\n' + '=' * 60);
    console.log('🎯 RESULT: Binary compression eliminates base64 overhead!');
    console.log(`   Your 11MB payload will now be ~${(binaryCompressed.length / 1024 / 1024 * 11).toFixed(1)}MB instead of ~11MB`);
}

testBinaryVsBase64Compression();
