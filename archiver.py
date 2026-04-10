import argparse
from io import BufferedWriter
import os
import struct

CHUNK_SIZE = 65536 # Сканируем по 64КБ для избежания заполнения памяти

def pack_file(f_out:BufferedWriter, file_path:str):
    """Вспомогательная функция для записи одного файла в архив"""
    dir_path = os.path.basename(file_path)
    name_bytes = dir_path.encode('utf-8')
    name_len = len(name_bytes)
    file_size = os.path.getsize(file_path)

    # <H - 2 байта  <Q - 8 байта
    f_out.write(struct.pack('<H', name_len))
    f_out.write(name_bytes)
    f_out.write(struct.pack('<Q', file_size))

    with open(file_path, 'rb') as f_in:
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            f_out.write(chunk)

def create_archive(f_output:str,dir_path:str):
    if not os.path.isdir(f_output):
        print(f"Ошибка: {f_output} не является папкой.")
        return 1

    with open(dir_path, 'wb') as f_out:
        for filename in os.listdir(f_output):
            file_path = os.path.join(f_output, filename)
            if os.path.isfile(file_path):
                pack_file(f_out, file_path)
    print(f"Архив '{dir_path}' успешно создан из папки '{f_output}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "action",
        type=str,
        metavar="action",
        help="Действия с архивом: {create, add, rm, unpack}",
        choices=["create", "add", "rm", "unpack"],
    )
    parser.add_argument("filename", type=str, help="Относительный/абсолютный путь архива")
    parser.add_argument("path", type=str, help="Абсолютный путь")

    args = parser.parse_args()
    #print(args)
    if args.action == "create":
        create_archive(args.filename,args.path)
    elif args.action == "add":
        pass
    elif args.action == "rm":
        pass
    else:
        pass
