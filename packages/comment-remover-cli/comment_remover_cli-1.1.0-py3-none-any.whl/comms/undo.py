#!/usr/bin/env python3
"""
comms.undo - Restore files from backup

Provides functionality to restore files from .backup directory.
"""

import shutil
import time
from pathlib import Path
from typing import List, Tuple


def get_backup_files() -> List[Tuple[Path, Path]]:
    """Get list of backup files and their restore destinations."""
    backup_dir = Path(".backup")
    
    if not backup_dir.exists():
        return []
    
    backup_files = []
    for backup_file in backup_dir.rglob('*'):
        if backup_file.is_file():
            # Calculate original path
            rel_path = backup_file.relative_to(backup_dir)
            original_path = Path.cwd() / rel_path
            backup_files.append((backup_file, original_path))
    
    return backup_files


def restore_file(backup_path: Path, original_path: Path) -> bool:
    """Restore a single file from backup."""
    try:
        # Create directory if it doesn't exist
        original_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy backup to original location
        shutil.copy2(backup_path, original_path)
        return True
    
    except Exception as e:
        print(f"Error restoring {original_path}: {e}")
        return False


def restore_from_backup() -> None:
    """Main backup restoration function."""
    start_time = time.time()
    backup_dir = Path(".backup")
    
    print("🔄 Backup Restoration Tool")
    print("=" * 50)
    
    if not backup_dir.exists():
        print("❌ No backup directory found.")
        print("Make sure you have run 'comms' first to create backups.")
        return
    
    # Get backup files
    backup_files = get_backup_files()
    
    if not backup_files:
        print("❌ No backup files found.")
        return
    
    print(f"Found {len(backup_files)} backup files")
    
    # Show what will be restored
    print("\\nFiles to be restored:")
    for backup_path, original_path in backup_files:
        print(f"  {original_path}")
    
    # Warning and confirmation
    print("\\n⚠️  WARNING ⚠️")
    print("This will OVERWRITE all modified files with their backup versions.")
    print("Any changes made after running 'comms' will be LOST.")
    
    response = input("\\nContinue with restoration? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Restoration cancelled.")
        return
    
    # Restore files
    restored_count = 0
    
    print(f"\\nRestoring {len(backup_files)} files...")
    for i, (backup_path, original_path) in enumerate(backup_files, 1):
        print(f"[{i:3d}/{len(backup_files)}] {original_path.name}", end=" ... ")
        
        if restore_file(backup_path, original_path):
            print("✓ Restored")
            restored_count += 1
        else:
            print("✗ Failed")
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\\n{'='*50}")
    print(f"✅ Restoration complete!")
    print(f"Files restored: {restored_count}/{len(backup_files)}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    
    # Ask about cleanup
    print(f"\\nBackup files are still in {backup_dir}")
    cleanup = input("Remove backup files? (yes/no): ").strip().lower()
    if cleanup in ['yes', 'y']:
        try:
            shutil.rmtree(backup_dir)
            print("✓ Backup files cleaned up")
        except Exception as e:
            print(f"✗ Could not remove backup directory: {e}")


if __name__ == "__main__":
    restore_from_backup()
