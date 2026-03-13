import os
import sys
import argparse
import shutil
from mutagen.easyid3 import EasyID3

def decode_(s):
    try:
        return s.encode("latin-1").decode('cp1251').encode('utf8').decode('utf8')
    except Exception as e:
        print(f"Decoding error: {e}")
        return s

def main():
    parser = argparse.ArgumentParser(description='Process MP3 files in a specified folder.')
    parser.add_argument('folder', type=str, help='Path to the folder containing mp3 files.')
    parser.add_argument('--recursive', action='store_true', help='Recursively process subdirectories.')
    parser.add_argument('--backup', type=str, choices=['yes', 'no'], default='yes', help='Create backup files (yes) or edit current files (no).')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t modify anything, just show the changes.')

    args = parser.parse_args()

    folder = args.folder
    recursive = args.recursive
    dry_run = args.dry_run
    backup = args.backup == 'yes'

    # Process files based on arguments
    if recursive:
        for dirpath, dirnames, filenames in os.walk(folder):
            process_mp3_files(dirpath, backup, dry_run)
    else:
        process_mp3_files(folder, backup, dry_run)

def process_mp3_files(directory, backup, dry_run):
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith('.mp3'):
            full_path = os.path.join(directory, filename)
            print('-' * 20, full_path, '-' * 20)

            try:
                audio = EasyID3(full_path)
                print('Was:', audio)

                for key, vals in audio.items():
                    audio[key] = [decode_(elem) for elem in vals]

                print('Now:', audio)

                if backup:
                    copy_path = f"{os.path.splitext(full_path)[0]}-fix.mp3"
                    if not dry_run:
                        shutil.copy(full_path, copy_path) 
                    
                    if not dry_run:
                        audio.save(copy_path)
                    print(f"Backup file '{copy_path}' created from '{full_path}'.")
                else:
                    if not dry_run:
                        audio.save(full_path)
                    print(f"File '{full_path}' successfully updated.")

            except Exception as e:
                print(f"Error processing file '{full_path}': {e}")

            print('-' * 50)

if __name__ == "__main__":
    main()
