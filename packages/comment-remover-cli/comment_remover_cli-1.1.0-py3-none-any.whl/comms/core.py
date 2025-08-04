#!/usr/bin/env python3
"""
comms.core - Core comment removal functionality

Contains the main CommentRemover class with all the parsing logic.
"""

import os
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set


class CommentRemover:
    """High-accuracy comment removal for multiple programming languages."""
    
    def __init__(self):
        self.backup_dir = Path(".backup")
        self.supported_extensions = {
            # Python
            '.py': 'python',
            '.pyi': 'python',
            '.pyw': 'python',
            
            # JavaScript/TypeScript
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            
            # C-family
            '.c': 'c_style',
            '.cpp': 'c_style',
            '.cxx': 'c_style',
            '.cc': 'c_style',
            '.h': 'c_style',
            '.hpp': 'c_style',
            '.hxx': 'c_style',
            '.cs': 'c_style',
            '.java': 'c_style',
            
            # Web
            '.html': 'html',
            '.htm': 'html',
            '.xml': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.less': 'css',
            
            # Scripts
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
            
            # SQL
            '.sql': 'sql',
            
            # Other languages
            '.go': 'c_style',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.pl': 'perl',
            '.r': 'r',
            '.m': 'matlab',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.lua': 'lua',
            '.ps1': 'powershell',
            '.psm1': 'powershell',
            '.dockerfile': 'shell',
            '.yml': 'yaml',
            '.yaml': 'yaml',
        }
        
        # Patterns that should NOT be removed
        self.preserve_patterns = [
            r'#[0-9a-fA-F]{3,8}\b',  # Color codes: #FF5733, #123
            r'https?://[^\s]+',       # URLs
            r'#!/[^\n]+',             # Shebang lines
            r'#pragma\s+',            # C pragmas
            r'#include\s+',           # C includes
            r'#define\s+',            # C defines
            r'#if\w*\s+',             # C conditionals
            r'#endif\b',              # C endif
            r'#undef\s+',             # C undef
            r'#error\s+',             # C error
            r'#warning\s+',           # C warning
        ]
    
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of file before modification."""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create relative path structure in backup
            rel_path = file_path.relative_to(Path.cwd())
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Warning: Could not backup {file_path}: {e}")
            return False
    
    def is_preserve_pattern(self, content: str, comment_start: int) -> bool:
        """Check if the comment-like pattern should be preserved."""
        # Extract the potential comment part starting from comment_start
        remaining_content = content[comment_start:]
        
        # Check each preserve pattern
        for pattern in self.preserve_patterns:
            # Check if the pattern matches at the beginning of the remaining content
            match = re.match(pattern, remaining_content)
            if match:
                return True
        return False
    
    def remove_python_comments(self, content: str) -> str:
        """Remove Python comments while preserving strings."""
        lines = content.split('\n')
        result = []
        
        for line in lines:
            if not line.strip():
                result.append(line)
                continue
                
            # Handle strings and comments
            new_line = ""
            i = 0
            in_single_quote = False
            in_double_quote = False
            in_triple_single = False
            in_triple_double = False
            escape_next = False
            
            while i < len(line):
                char = line[i]
                
                if escape_next:
                    new_line += char
                    escape_next = False
                elif char == '\\' and (in_single_quote or in_double_quote):
                    new_line += char
                    escape_next = True
                elif not any([in_single_quote, in_double_quote, in_triple_single, in_triple_double]):
                    # Not in any string
                    if i + 2 < len(line) and line[i:i+3] == '"""':
                        in_triple_double = True
                        new_line += line[i:i+3]
                        i += 2
                    elif i + 2 < len(line) and line[i:i+3] == "'''":
                        in_triple_single = True
                        new_line += line[i:i+3]
                        i += 2
                    elif char == '"':
                        in_double_quote = True
                        new_line += char
                    elif char == "'":
                        in_single_quote = True
                        new_line += char
                    elif char == '#':
                        # Check if this should be preserved
                        if not self.is_preserve_pattern(line, i):
                            break  # Rest of line is comment
                        else:
                            new_line += char
                    else:
                        new_line += char
                else:
                    # Inside string
                    if in_triple_double and i + 2 < len(line) and line[i:i+3] == '"""':
                        in_triple_double = False
                        new_line += line[i:i+3]
                        i += 2
                    elif in_triple_single and i + 2 < len(line) and line[i:i+3] == "'''":
                        in_triple_single = False
                        new_line += line[i:i+3]
                        i += 2
                    elif in_double_quote and char == '"':
                        in_double_quote = False
                        new_line += char
                    elif in_single_quote and char == "'":
                        in_single_quote = False
                        new_line += char
                    else:
                        new_line += char
                
                i += 1
            
            result.append(new_line.rstrip())
        
        return '\n'.join(result)
    
    def remove_c_style_comments(self, content: str) -> str:
        """Remove C-style comments (// and /* */) while preserving strings."""
        result = ""
        i = 0
        in_single_quote = False
        in_double_quote = False
        escape_next = False
        
        while i < len(content):
            char = content[i]
            
            if escape_next:
                result += char
                escape_next = False
            elif char == '\\' and (in_single_quote or in_double_quote):
                result += char
                escape_next = True
            elif not in_single_quote and not in_double_quote:
                # Not in string
                if char == '"':
                    in_double_quote = True
                    result += char
                elif char == "'":
                    in_single_quote = True
                    result += char
                elif i + 1 < len(content) and content[i:i+2] == '//':
                    # Single-line comment
                    if not self.is_preserve_pattern(content, i):
                        # Skip to end of line
                        while i < len(content) and content[i] != '\n':
                            i += 1
                        continue
                    else:
                        result += char
                elif i + 1 < len(content) and content[i:i+2] == '/*':
                    # Multi-line comment
                    if not self.is_preserve_pattern(content, i):
                        i += 2
                        # Skip until */
                        while i + 1 < len(content) and content[i:i+2] != '*/':
                            i += 1
                        if i + 1 < len(content):
                            i += 2  # Skip both * and /
                        continue
                    else:
                        result += char
                else:
                    result += char
            else:
                # Inside string
                if in_double_quote and char == '"':
                    in_double_quote = False
                elif in_single_quote and char == "'":
                    in_single_quote = False
                result += char
            
            i += 1
        
        return result
    
    def remove_html_comments(self, content: str) -> str:
        """Remove HTML/XML comments while preserving content."""
        # Remove <!-- ... --> comments
        pattern = r'<!--.*?-->'
        return re.sub(pattern, '', content, flags=re.DOTALL)
    
    def remove_css_comments(self, content: str) -> str:
        """Remove CSS comments while preserving color codes and URLs."""
        result = ""
        i = 0
        in_string = False
        string_char = None
        
        while i < len(content):
            char = content[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    result += char
                elif i + 1 < len(content) and content[i:i+2] == '/*':
                    # CSS comment
                    if not self.is_preserve_pattern(content, i):
                        i += 2
                        while i + 1 < len(content) and content[i:i+2] != '*/':
                            i += 1
                        if i + 1 < len(content):
                            i += 2  # Skip both * and /
                        continue
                    else:
                        result += char
                else:
                    result += char
            else:
                if char == string_char:
                    in_string = False
                    string_char = None
                result += char
            
            i += 1
        
        return result
    
    def remove_shell_comments(self, content: str) -> str:
        """Remove shell comments while preserving shebangs."""
        lines = content.split('\n')
        result = []
        
        for line in lines:
            if not line.strip():
                result.append(line)
                continue
            
            # Preserve shebang
            if line.startswith('#!'):
                result.append(line)
                continue
            
            new_line = ""
            i = 0
            in_single_quote = False
            in_double_quote = False
            escape_next = False
            
            while i < len(line):
                char = line[i]
                
                if escape_next:
                    new_line += char
                    escape_next = False
                elif char == '\\':
                    new_line += char
                    escape_next = True
                elif not in_single_quote and not in_double_quote:
                    if char == '"':
                        in_double_quote = True
                        new_line += char
                    elif char == "'":
                        in_single_quote = True
                        new_line += char
                    elif char == '#':
                        if not self.is_preserve_pattern(line, i):
                            break
                        else:
                            new_line += char
                    else:
                        new_line += char
                else:
                    if in_double_quote and char == '"':
                        in_double_quote = False
                    elif in_single_quote and char == "'":
                        in_single_quote = False
                    new_line += char
                
                i += 1
            
            result.append(new_line.rstrip())
        
        return '\n'.join(result)
    
    def remove_sql_comments(self, content: str) -> str:
        """Remove SQL comments (-- and /* */)."""
        lines = content.split('\n')
        result = []
        
        for line in lines:
            if not line.strip():
                result.append(line)
                continue
            
            new_line = ""
            i = 0
            in_string = False
            string_char = None
            
            while i < len(line):
                char = line[i]
                
                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        string_char = char
                        new_line += char
                    elif i + 1 < len(line) and line[i:i+2] == '--':
                        if not self.is_preserve_pattern(line, i):
                            break
                        else:
                            new_line += char
                    else:
                        new_line += char
                else:
                    if char == string_char:
                        in_string = False
                        string_char = None
                    new_line += char
                
                i += 1
            
            result.append(new_line.rstrip())
        
        # Handle /* */ comments
        content = '\n'.join(result)
        return self.remove_c_style_comments(content)
    
    def remove_comments_by_type(self, content: str, file_type: str) -> str:
        """Remove comments based on file type."""
        if file_type == 'python':
            return self.remove_python_comments(content)
        elif file_type in ['javascript', 'typescript', 'c_style', 'rust', 'swift', 'kotlin', 'scala']:
            return self.remove_c_style_comments(content)
        elif file_type == 'html':
            return self.remove_html_comments(content)
        elif file_type == 'css':
            return self.remove_css_comments(content)
        elif file_type in ['shell', 'powershell', 'ruby', 'perl', 'r', 'yaml']:
            return self.remove_shell_comments(content)
        elif file_type == 'sql':
            return self.remove_sql_comments(content)
        elif file_type == 'php':
            # PHP supports both // and # comments
            content = self.remove_c_style_comments(content)
            return self.remove_shell_comments(content)
        elif file_type in ['matlab', 'lua']:
            return self.remove_shell_comments(content)  # % and -- respectively, but similar handling
        else:
            print(f"Unsupported file type: {file_type}")
            return content
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file to remove comments."""
        try:
            suffix = file_path.suffix.lower()
            if suffix not in self.supported_extensions:
                return False
            
            file_type = self.supported_extensions[suffix]
            
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove comments
            processed_content = self.remove_comments_by_type(content, file_type)
            
            # Only write if content changed
            if processed_content != content:
                # Create backup
                if not self.create_backup(file_path):
                    return False
                
                # Write processed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                return True
            
            return False
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for supported files."""
        files = []
        try:
            for item in directory.rglob('*'):
                if item.is_file() and item.suffix.lower() in self.supported_extensions:
                    # Skip backup directory
                    if '.backup' not in item.parts:
                        files.append(item)
        except PermissionError:
            print(f"Permission denied: {directory}")
        
        return files
