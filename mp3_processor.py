import os
import shutil
import argparse
from mutagen.easyid3 import EasyID3

def decode_(s):
    try:
        return s.encode("latin-1").decode('cp1251').encode('utf8').decode('utf8')
    except Exception as e:
        print(f"Decoding error: {e}")
        return s

def parse_and_fix_tags(full_path, decode_fn=decode_, create_backup=True, dry_run=False):
    """
    Парсит ID3 теги MP3, декодирует значения с помощью decode_fn и сохраняет изменения.
    Возвращает словарь с информацией для тестов:
      {
        "path": full_path,
        "was": <dict or None>,
        "now": <dict or None>,
        "backup_path": <str or None>,
        "updated_path": <str or None>,
        "error": <str or None>
      }
    """
    result = {
        "path": full_path,
        "was": None,
        "now": None,
        "backup_path": None,
        "updated_path": None,
        "error": None
    }

    try:
        audio = EasyID3(full_path)
        # Сохраним исходные теги (копия)
        result["was"] = {k: list(v) for k, v in audio.items()}

        # Декодируем каждое значение
        for key, vals in audio.items():
            audio[key] = [decode_fn(elem) for elem in vals]

        result["now"] = {k: list(v) for k, v in audio.items()}

        if create_backup:
            copy_path = f"{os.path.splitext(full_path)[0]}-fix.mp3"
            result["backup_path"] = copy_path
            if not dry_run:
                shutil.copy(full_path, copy_path)
                audio.save(copy_path)
            result["updated_path"] = copy_path
        else:
            result["backup_path"] = None
            if not dry_run:
                audio.save(full_path)
            result["updated_path"] = full_path

    except Exception as e:
        result["error"] = str(e)

    return result

def process_mp3_files(directory, backup, dry_run):
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith('.mp3'):
            full_path = os.path.join(directory, filename)
            print('-' * 20, full_path, '-' * 20)
            res = parse_and_fix_tags(full_path, decode_, create_backup=backup, dry_run=dry_run)
            if res["error"]:
                print(f"Error processing file '{full_path}': {res['error']}")
            else:
                print('Was:', res["was"])
                print('Now:', res["now"])
                if res["backup_path"]:
                    print(f"Backup file '{res['backup_path']}' created from '{full_path}'.")
                else:
                    print(f"File '{full_path}' successfully updated.")
            print('-' * 50)

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

    if recursive:
        for dirpath, dirnames, filenames in os.walk(folder):
            process_mp3_files(dirpath, backup, dry_run)
    else:
        process_mp3_files(folder, backup, dry_run)

if __name__ == "__main__":
    main()
