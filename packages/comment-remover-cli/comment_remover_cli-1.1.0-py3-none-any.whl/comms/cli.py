#!/usr/bin/env python3
"""
comms.cli - Command line interface for the comment removal tool

Provides the main CLI functionality including comment removal, undo, and demo.
"""

import sys
import time
import shutil
from pathlib import Path
from typing import List, Tuple

from .core import CommentRemover
from .undo import restore_from_backup
from .demo import create_demo_files
from .config import load_config


def show_help():
    """Show help information."""
    print("""
🔧 Comment Removal Tool

USAGE:
  comms [directory]          # Remove comments from directory
  comms --undo              # Restore files from backup
  comms --demo              # Create demo files for testing
  comms --config            # Show configuration options
  comms --help              # Show this help

EXAMPLES:
  comms                     # Current directory (recursive)
  comms /path/to/project    # Specific directory (recursive)
  comms --undo              # Restore from .backup/
  comms --demo              # Create test files in demo_files/

FEATURES:
  • Supports 20+ programming languages
  • Creates automatic backups in .backup/
  • Preserves color codes, URLs, shebangs, preprocessor directives
  • Recursive directory scanning
  • Safe operation with confirmation prompts

PRESERVED PATTERNS:
  • Color codes: #FF5733, #123ABC
  • URLs: https://example.com, http://site.com
  • Shebangs: #!/usr/bin/env python
  • C preprocessor: #include, #define, #if, #endif
  • Content inside strings

SUPPORTED FILE TYPES:
  Python, JavaScript, TypeScript, C/C++, Java, C#, Go, Rust,
  HTML, CSS, SQL, PHP, Ruby, Shell, PowerShell, YAML, and more

For more information: https://github.com/yourusername/comms
""")


def run_comment_removal(directory: str = ".") -> None:
    """Main comment removal function."""
    start_time = time.time()
    directory_path = Path(directory).resolve()
    
    # Load configuration
    config = load_config()
    remover = CommentRemover()
    
    # Apply config if available
    if config:
        if 'preserve_patterns' in config:
            remover.preserve_patterns.extend(config['preserve_patterns'])
        if 'file_extensions' in config:
            remover.supported_extensions.update(config['file_extensions'])
    
    print("🔍 Comment Removal Tool")
    print("=" * 50)
    print(f"Scanning directory: {directory_path}")
    
    # Scan for files
    files = remover.scan_directory(directory_path)
    
    if not files:
        print("No supported files found.")
        return
    
    print(f"Found {len(files)} supported files")
    print("\\nSupported file types:")
    extensions = set(f.suffix for f in files)
    for ext in sorted(extensions):
        print(f"  {ext} ({remover.supported_extensions.get(ext, 'unknown')})")
    
    # Warning and confirmation
    print("\\n⚠️  WARNING ⚠️")
    print("This tool will remove ALL comments from the detected files.")
    print("Backups will be created in .backup/ directory.")
    print("Previous backups will be OVERWRITTEN.")
    print("\\nWhat will be preserved:")
    print("  • Color codes (#FF5733)")
    print("  • URLs (https://example.com)")
    print("  • Shebang lines (#!/usr/bin/env)")
    print("  • C preprocessor directives (#include, #define, etc.)")
    print("  • Content inside strings")
    
    response = input("\\nContinue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    # Clear old backups
    if remover.backup_dir.exists():
        shutil.rmtree(remover.backup_dir)
    
    # Process files
    processed_count = 0
    
    print(f"\\nProcessing {len(files)} files...")
    for i, file_path in enumerate(files, 1):
        # Show relative path from the scanning directory
        try:
            rel_path = file_path.relative_to(directory_path)
            display_path = str(rel_path)
        except ValueError:
            display_path = file_path.name
        
        print(f"[{i:3d}/{len(files)}] {display_path}", end=" ... ")
        
        if remover.process_file(file_path):
            print("✓ Comments removed")
            processed_count += 1
        else:
            print("○ No changes")
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\\n{'='*50}")
    print(f"✅ Processing complete!")
    print(f"Files processed: {processed_count}/{len(files)}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Backups stored in: {remover.backup_dir}")
    print(f"\\nTo undo changes, run: comms --undo")


def show_config():
    """Show configuration information."""
    print("🔧 Configuration Options")
    print("=" * 30)
    print()
    print("The tool looks for configuration in these locations:")
    print("  1. ./comms.json (current directory)")
    print("  2. ~/.comms.json (home directory)")
    print("  3. Built-in defaults")
    print()
    print("Example configuration file (comms.json):")
    print('''
{
  "preserve_patterns": [
    "#[0-9a-fA-F]{3,8}\\\\b",
    "https?://[^\\\\s]+",
    "#!/[^\\\\n]+"
  ],
  "file_extensions": {
    ".txt": "shell",
    ".config": "shell"
  },
  "backup_directory": ".backup"
}
''')
    
    # Show current config
    config = load_config()
    if config:
        print("\\n📄 Current configuration loaded from file:")
        import json
        print(json.dumps(config, indent=2))
    else:
        print("\\n📄 Using built-in default configuration")


def main():
    """Main entry point for CLI."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ['--help', '-h']:
            show_help()
        elif arg in ['--undo', '-u']:
            restore_from_backup()
        elif arg in ['--demo', '-d']:
            create_demo_files()
        elif arg in ['--config', '-c']:
            show_config()
        elif arg.startswith('-'):
            print(f"Unknown option: {arg}")
            print("Use 'comms --help' for usage information.")
        else:
            # Directory argument
            run_comment_removal(arg)
    else:
        # Default: current directory
        run_comment_removal(".")


if __name__ == "__main__":
    main()
