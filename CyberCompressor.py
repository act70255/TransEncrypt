import os
import zlib
import hashlib
import argparse
from pathlib import Path
from typing import Optional
import py7zr
import py7zr.exceptions

PW_SALT = ''

def generate_password_from_crc(crc_value: int) -> str:
    crc_string = f"{crc_value & 0xFFFFFFFF:08x}"
    hasher = hashlib.sha256()
    hasher.update(crc_string.encode('utf-8'))
    hashed_string = hasher.hexdigest()
    password = hashed_string[-16:]
    print(f"[*] CRC32 值: {crc_string}")
    print(f"[*] SHA-256 Hash: ...{hashed_string[-24:]}")
    print(f"[*] 生成的最終密碼 (後16碼): {password}")
    return f'{password}{PW_SALT}'

def find_key_file_crc(target_path: Path) -> Optional[int]:
    if not target_path.is_dir():
        print(f"[!] 錯誤: 資料夾 '{target_path}' 不存在。")
        return None
    all_files = [f for f in target_path.glob('**/*') if f.is_file()]
    if not all_files:
        print(f"[!] 警告: 資料夾 '{target_path}' 中沒有任何檔案。")
        return None
    source_file_path = min(all_files, key=lambda f: f.name)
    print(f"[*] 找到用於密碼生成的檔案: {source_file_path.relative_to(target_path)}")
    try:
        with open(source_file_path, 'rb') as f:
            content = f.read()
            return zlib.crc32(content)
    except IOError as e:
        print(f"[!] 錯誤: 無法讀取檔案 '{source_file_path.name}': {e}")
        return None

def compress_folder(source_folder: str):
    """【v4】自動決定輸出路徑並壓縮。"""
    source_path = Path(source_folder).resolve()
    output_archive_path = source_path.parent / f"{source_path.name}.7z"
    
    crc_value = find_key_file_crc(source_path)
    if crc_value is None:
        print("[!] 無法生成密碼，壓縮中止。")
        return

    password = generate_password_from_crc(crc_value)
    
    print(f"[*] 自動設定輸出檔案為: {output_archive_path}")
    print(f"[*] 使用 py7zr 進行壓縮...")
    try:
        with py7zr.SevenZipFile(output_archive_path, 'w', password=password) as archive:
            print(f"[*] 正在將 '{source_path.name}' 添加到壓縮檔...")
            archive.writeall(source_path, arcname=source_path.name)
        print(f"[+] 成功! 資料夾 '{source_folder}' 已壓縮至 '{output_archive_path}'")
    except Exception as e:
        print(f"[!] 使用 py7zr 壓縮時發生錯誤: {e}")

def decompress_archive(source_archive: str):
    """【v4】自動決定輸出路徑並解壓縮。"""
    archive_file = Path(source_archive).resolve()
    if not archive_file.is_file():
        print(f"[!] 錯誤: 壓縮檔 '{source_archive}' 不存在。")
        return

    output_path = archive_file.parent #/ archive_file.stem
    output_path = os.path.join(output_path, 'Decompressed')
    
    try:
        print("[*] 正在讀取壓縮檔元數據以生成密碼...")
        with py7zr.SevenZipFile(archive_file, 'r') as archive:
            all_files = archive.list()
            if not all_files: return
            file_infos = [f for f in all_files if not f.is_directory]
            if not file_infos: return
            target_file_info = min(file_infos, key=lambda f: Path(f.filename).name)
            crc_value = target_file_info.crc32
            print(f"[*] 從元數據中找到用於密碼生成的檔案: {target_file_info.filename}")

        password = generate_password_from_crc(crc_value)
        
        print(f"[*] 自動設定輸出資料夾為: {output_path}")
        print(f"[*] 使用 py7zr 執行解壓縮...")
        with py7zr.SevenZipFile(archive_file, 'r', password=password) as archive:
            archive.extractall(path=output_path)
        print(f"[+] 成功! 檔案已解壓縮至 '{output_path}'")
    except py7zr.exceptions.PasswordRequired:
         print("[!] 錯誤: 壓縮檔的檔案列表已被加密。")
    except py7zr.exceptions.Bad7zFile as e:
        print(f"[!] 錯誤: 檔案格式錯誤或密碼不正確。 {e}")
    except Exception as e:
        print(f"[!] 處理時發生未知錯誤: {e}")

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(
    #     description="【v4】自動化 7-Zip 加解壓縮，自動決定輸出路徑。",
    #     formatter_class=argparse.RawTextHelpFormatter
    # )
    # parser.add_argument('mode', choices=['compress', 'decompress'], help="選擇操作模式")
    # parser.add_argument('source', help="來源路徑 (資料夾或 .7z 檔案)")
    # args = parser.parse_args()

    # if args.mode == 'compress':
    #     compress_folder(args.source)
    # elif args.mode == 'decompress':
    #     decompress_archive(args.source)
    
    # compress_folder(r'C:\WorkSpace\.publish\ver0731\file')
    decompress_archive(r'C:\WorkSpace\.publish\ver0731\file.7z')