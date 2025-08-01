# remover.py
import os

def delete_duplicates(dupes, dry_run=True):
    for filehash, paths in dupes.items():
        for path in paths[1:]:  # Keep the first one
            print(f"{'[DRY RUN]' if dry_run else '[DELETING]'} {path}")
            if not dry_run:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")
