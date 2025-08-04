#!/usr/bin/env python3
"""
comms.config - Configuration loading and management

Handles loading configuration from JSON files in various locations.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any


def load_config() -> Optional[Dict[str, Any]]:
    """Load configuration from available sources."""
    config_locations = [
        Path.cwd() / "comms.json",          # Current directory
        Path.home() / ".comms.json",        # Home directory
        Path.cwd() / ".comms.json",         # Hidden file in current directory
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"📄 Loaded configuration from: {config_path}")
                return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading config from {config_path}: {e}")
                continue
    
    return None


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration."""
    return {
        "preserve_patterns": [
            r"#[0-9a-fA-F]{3,8}\\b",  # Color codes: #FF5733, #123
            r"https?://[^\\s]+",       # URLs
            r"#!/[^\\n]+",             # Shebang lines
            r"#pragma\\s+",            # C pragmas
            r"#include\\s+",           # C includes
            r"#define\\s+",            # C defines
            r"#if\\w*\\s+",            # C conditionals
            r"#endif\\b",              # C endif
            r"#undef\\s+",             # C undef
            r"#error\\s+",             # C error
            r"#warning\\s+",           # C warning
        ],
        "file_extensions": {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".css": "css",
            ".html": "html",
            ".c": "c_style",
            ".cpp": "c_style",
            ".java": "c_style",
            ".sh": "shell",
            ".sql": "sql",
        },
        "backup_directory": ".backup",
        "require_confirmation": True,
        "verbose_output": True,
    }


def create_sample_config(path: Path = None) -> None:
    """Create a sample configuration file."""
    if path is None:
        path = Path.cwd() / "comms.json"
    
    config = {
        "_description": "Configuration file for comms comment removal tool",
        "preserve_patterns": [
            "#[0-9a-fA-F]{3,8}\\\\b",
            "https?://[^\\\\s]+",
            "#!/[^\\\\n]+",
            "#pragma\\\\s+",
            "#include\\\\s+",
            "#define\\\\s+"
        ],
        "file_extensions": {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".css": "css",
            ".html": "html",
            ".c": "c_style",
            ".cpp": "c_style",
            ".java": "c_style",
            ".sh": "shell",
            ".sql": "sql",
            ".txt": "shell",
            ".config": "shell"
        },
        "backup_directory": ".backup",
        "require_confirmation": True,
        "verbose_output": True
    }
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created sample config file: {path}")
    except IOError as e:
        print(f"❌ Failed to create config file: {e}")


if __name__ == "__main__":
    # Create sample config when run directly
    create_sample_config()
