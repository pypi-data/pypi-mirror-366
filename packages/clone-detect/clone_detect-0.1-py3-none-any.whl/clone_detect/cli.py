# cli.py
import argparse
from clone_detect.scanner import find_duplicates
from clone_detect.remover import delete_duplicates

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files recursively.")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("--algo", default="sha256", help="Hash algorithm (default: sha256)")
    parser.add_argument("--delete", action="store_true", help="Delete duplicates (keep first)")
    parser.add_argument("--dry-run", action="store_true", help="Just show what would be deleted")
    args = parser.parse_args()

    print(f"Scanning {args.folder}...")
    dupes = find_duplicates(args.folder, args.algo)
    if not dupes:
        print("No duplicates found.")
        return

    for filehash, paths in dupes.items():
        print(f"\nDuplicate group (hash={filehash}):")
        for i, path in enumerate(paths):
            mark = " (keep)" if i == 0 else ""
            print(f"  [{i+1}] {path}{mark}")
    
    if args.delete:
        delete_duplicates(dupes, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
