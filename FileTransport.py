import base64
import os

def file_to_base64_simple(input_file_path, output_txt_path):
    with open(input_file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    filename = os.path.basename(input_file_path)  # 只取檔名
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(filename + '\n')
        f.write(encoded)

def base64_to_file_simple(input_txt_path, output_dir='.'):
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    filename = lines[0].strip()
    encoded = ''.join(lines[1:]).strip()  # 合併剩餘行，避免被自動分段

    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(encoded))

    print(f"還原完成: {output_path}")

file_to_base64_simple(r'C:\WorkSpace\.publish\ver0731\file.7z', 'transv0731.t64')
# base64_to_file_simple('transv0731.t64')
