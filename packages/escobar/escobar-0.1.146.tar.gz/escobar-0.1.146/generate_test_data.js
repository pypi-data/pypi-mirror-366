
// Auto-generated Node.js script to create test data for Python verification
const fs = require('fs');

// Mock pako for Node.js environment (simplified gzip implementation)
const zlib = require('zlib');

// Simulate TypeScript compression functions
function compressString(input) {
    try {
        // Convert string to UTF-8 bytes
        const utf8Bytes = Buffer.from(input, 'utf8');
        
        // Compress using gzip
        const compressed = zlib.gzipSync(utf8Bytes);
        
        // Convert to base64
        const base64 = compressed.toString('base64');
        
        return base64;
    } catch (error) {
        throw new Error(`Failed to compress string: ${error.message}`);
    }
}

function encodeBase64(input) {
    try {
        // Convert string to UTF-8 bytes then to base64
        const utf8Bytes = Buffer.from(input, 'utf8');
        const base64 = utf8Bytes.toString('base64');
        
        return base64;
    } catch (error) {
        throw new Error(`Failed to encode string as base64: ${error.message}`);
    }
}

// Test cases
const testCases = [
    {
        name: 'Simple String',
        original: 'Hello, World!',
        description: 'Basic ASCII string'
    },
    {
        name: 'Unicode String',
        original: 'Hello 🌍! Testing émojis and spëcial chars: 中文 العربية',
        description: 'String with Unicode characters, emojis, and special chars'
    },
    {
        name: 'JSON Data',
        original: '{"message_type": "chat_request", "call_id": "test-123", "username": "testuser", "chatID": "chat-456", "content": "This is a test message with some content.", "metadata": {"timestamp": "2025-01-23T20:30:00.000Z", "source": "test"}}',
        description: 'JSON protocol message'
    },
    {
        name: 'Large Repeated String',
        original: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ',
        description: 'Large string with repeated patterns (good compression)'
    },
    {
        name: 'Empty String',
        original: '',
        description: 'Empty string edge case'
    },
    {
        name: 'Whitespace String',
        original: '   \n\t   ',
        description: 'String with various whitespace characters'
    },
    {
        name: 'String with Null Bytes',
        original: 'Hello\x00World\x00Test',
        description: 'String containing null bytes'
    }

];

// Generate test data
const results = {
    timestamp: new Date().toISOString(),
    testCases: []
};

console.log('Generating test data for Python verification...');

testCases.forEach((testCase, index) => {
    try {
        const compressed = compressString(testCase.original);
        const base64Encoded = encodeBase64(testCase.original);
        
        results.testCases.push({
            name: testCase.name,
            description: testCase.description,
            original: testCase.original,
            compressed: compressed,
            base64Encoded: base64Encoded,
            originalLength: Buffer.from(testCase.original, 'utf8').length,
            compressedLength: Buffer.from(compressed, 'base64').length
        });
        
        console.log(`✓ ${testCase.name}: ${Buffer.from(testCase.original, 'utf8').length} → ${Buffer.from(compressed, 'base64').length} bytes`);
    } catch (error) {
        console.error(`✗ ${testCase.name}: ${error.message}`);
        results.testCases.push({
            name: testCase.name,
            description: testCase.description,
            original: testCase.original,
            error: error.message
        });
    }
});

// Save results to JSON file
fs.writeFileSync('compression_test_data.json', JSON.stringify(results, null, 2));
console.log('\nTest data saved to compression_test_data.json');
console.log(`Generated ${results.testCases.length} test cases`);
