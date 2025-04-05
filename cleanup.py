#!/usr/bin/env python3
"""
Script to clean up unnecessary files from the repository.
This script will remove empty files that are no longer needed.
"""

import os
import sys

# Files to be removed (if they exist and are empty)
files_to_remove = [
    'check_api_keys.py',
    'check_creds.py',
    'check_gemini_key.py',
    'research_crew.py'
]

def cleanup():
    """Clean up empty files that are no longer needed."""
    print("Starting cleanup process...")
    
    # Track counts for summary
    removed = 0
    skipped = 0
    
    for filename in files_to_remove:
        if os.path.exists(filename):
            # Check if file is empty
            if os.path.getsize(filename) == 0:
                try:
                    os.remove(filename)
                    print(f"✓ Removed empty file: {filename}")
                    removed += 1
                except Exception as e:
                    print(f"✗ Failed to remove {filename}: {e}")
            else:
                print(f"! Skipped non-empty file: {filename}")
                skipped += 1
        else:
            print(f"- File not found: {filename}")
    
    # Print summary
    print("\nCleanup complete!")
    print(f"Files removed: {removed}")
    print(f"Files skipped: {skipped}")

if __name__ == "__main__":
    cleanup()