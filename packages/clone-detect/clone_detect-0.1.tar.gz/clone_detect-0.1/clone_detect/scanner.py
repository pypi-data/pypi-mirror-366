# scanner.py
import os
import hashlib

def hash_file(path, algo='sha256'):
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(folder, algo='sha256'):
    hashes = {}
    duplicates = {}
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            try:
                file_hash = hash_file(path, algo)
                if file_hash in hashes:
                    duplicates.setdefault(file_hash, [hashes[file_hash]]).append(path)
                else:
                    hashes[file_hash] = path
            except Exception as e:
                print(f"Error processing {path}: {e}")
    return duplicates
