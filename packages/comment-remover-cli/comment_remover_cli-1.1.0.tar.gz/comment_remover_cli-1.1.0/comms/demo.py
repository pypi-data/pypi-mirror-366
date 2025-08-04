#!/usr/bin/env python3
"""
comms.demo - Create demo files for testing the comment removal tool

Provides functionality to create sample files with comments for testing.
"""

from pathlib import Path
from typing import Dict


def create_demo_files() -> None:
    """Create demo files with various comment types for testing."""
    demo_dir = Path("demo_files")
    demo_dir.mkdir(exist_ok=True)
    
    # Sample files with comments
    demo_files = {
        'test.py': '''#!/usr/bin/env python3
# This is a single-line comment that should be removed
"""
This is a docstring that should be preserved
"""
import requests  # This comment should be removed

def process_data():
    # Another comment to remove
    url = "https://api.example.com"  # URL should be preserved
    color = "#FF5733"  # Color code should be preserved
    
    # Multi-line comment
    # that spans several lines
    # should all be removed
    
    data = {
        "comment": "This # is not a comment",  # But this is
        "color": "#123ABC",  # Color preserved
        "url": "http://test.com#anchor"  # URL with # preserved
    }
    
    return data

# Final comment to remove
''',
        
        'test.js': '''// Single-line comment to remove
/* Multi-line comment
   that should be removed */
   
function processData() {
    // Another comment to remove
    const url = "https://example.com";  // URL preserved
    const color = "#FF5733";  // Color preserved
    
    /* This is a 
       multi-line comment
       to remove */
    
    const data = {
        comment: "This // is not a comment",  // But this is
        color: "#ABC123",  // Color preserved
        url: "https://test.com"  // URL preserved
    };
    
    return data;
}

// Final comment
''',
        
        'test.css': '''/* Header styles */
.header {
    background-color: #FF5733; /* Primary color */
    color: #FFFFFF; /* White text */
    /* padding: 10px; This is commented out */
}

/* Navigation styles */
.nav {
    background: url("https://example.com/bg.jpg"); /* Background image */
    /* margin: 0; */
}

/* Media queries */
@media (max-width: 768px) {
    /* Mobile styles */
    .header {
        font-size: 14px; /* Smaller font */
    }
}
''',
        
        'test.c': '''#include <stdio.h>  // Standard I/O
#define MAX_SIZE 100  // Define constant
// This is a comment to remove

/* Multi-line comment
   to be removed */
   
int main() {
    // Single line comment
    char* url = "https://example.com";  // URL preserved
    char* color = "#FF5733";  // Color preserved
    
    /* Another multi-line
       comment to remove */
    
    printf("URL: %s\\n", url);  // Print URL
    return 0;  // Return success
}

// End of file comment
''',
        
        'test.sh': '''#!/bin/bash
# This is a shell comment to remove

# Function definition
process_data() {
    # Local comment to remove
    URL="https://example.com"  # URL preserved
    COLOR="#FF5733"  # Color preserved
    
    echo "Processing data..."  # This comment goes
    # Multiple line comment
    # that should be removed
    
    echo "URL: $URL"
    echo "Color: $COLOR"
}

# Main execution
process_data

# End comment
''',
        
        'test.html': '''<!DOCTYPE html>
<!-- This HTML comment should be removed -->
<html>
<head>
    <!-- Page title comment -->
    <title>Test Page</title>
    <style>
        /* CSS comment in HTML */
        body { background: #FF5733; /* Color preserved */ }
    </style>
</head>
<body>
    <!-- Main content comment -->
    <h1>Hello World</h1>
    <a href="https://example.com">Link</a> <!-- Link comment -->
    
    <!-- Footer comment -->
</body>
</html>
''',
        
        'test.sql': '''-- This is a SQL comment to remove
/* Multi-line SQL comment
   to be removed */

SELECT * FROM users
WHERE email = 'test@example.com'  -- Email filter comment
  AND status = 'active';  -- Status comment

-- Another query
/* Query for statistics */
SELECT 
    COUNT(*) as total,  -- Count comment
    AVG(age) as avg_age  -- Average comment
FROM users
WHERE created_at > '2023-01-01';  -- Date filter

-- End of file
'''
    }
    
    # Write demo files
    created_count = 0
    for filename, content in demo_files.items():
        file_path = demo_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_count += 1
        except IOError as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    print(f"✅ Created {created_count} demo files in {demo_dir}/")
    print("\\nDemo files with comments:")
    for filename in demo_files.keys():
        print(f"  • {filename}")
    
    print(f"\\n🎯 To test the comment removal tool:")
    print(f"1. cd {demo_dir}")
    print(f"2. comms")
    print(f"3. Check the results")
    print(f"4. comms --undo (to restore)")
    
    print(f"\\n📁 Or run from current directory:")
    print(f"   comms {demo_dir}")


if __name__ == "__main__":
    create_demo_files()
