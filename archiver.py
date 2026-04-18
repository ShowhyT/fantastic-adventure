import argparse
import os
import struct
from io import BufferedWriter

CHUNK_SIZE = 65536  # Сканируем по 64КБ для избежания заполнения памяти


def _pack_file(f_out: BufferedWriter, file_path: str):
    """Вспомогательная функция для записи одного файла в архив"""
    dir_path = os.path.basename(file_path)
    name_bytes = dir_path.encode("utf-8")
    name_len = len(name_bytes)
    file_size = os.path.getsize(file_path)

    # <H - 2 байта  <Q - 8 байта
    f_out.write(struct.pack("<H", name_len))
    f_out.write(name_bytes)
    f_out.write(struct.pack("<Q", file_size))

    # Считываем данные с файла в chunk и записываем
    with open(file_path, "rb") as f_in:
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            f_out.write(chunk)


def create_archive(f_output: str, dir_path: str):
    if not os.path.isdir(f_output):
        print(f"Ошибка: {f_output} не является папкой.")
        return 1

    with open(dir_path, "wb") as f_out:
        for filename in os.listdir(f_output):
            file_path = os.path.join(f_output, filename)
            if os.path.isfile(file_path):
                _pack_file(f_out, file_path)
    print(f"Архив {dir_path} успешно создан из папки {f_output}.")


def add_file_to_archive(archive_name: str, file_path: str):
    if not os.path.lexists(archive_name) or not os.path.lexists(file_path):
        print("Ошибка, не существует файла, который вы хотите добавить, или архива")
        return 1

    with open(archive_name, "ab") as f_out:  # ab - режим дозаписи в архив
        _pack_file(f_out, file_path)
    print(f"Файл {file_path} успешно добавлен в {archive_name}.")


def unpack_archive(archive_name: str, folder_path: str):
    """Извлекает все файлы из архива в указанную папку"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(archive_name, "rb") as f_in:
        while True:
            name_len_bytes = f_in.read(2)  # Читаем длину имени (2 байта)
            if not name_len_bytes:
                break  # Конец архива

            name_len = struct.unpack("<H", name_len_bytes)[0]  # Читаем длину имени

            name_bytes = f_in.read(name_len)  # Считываем имя файла по длине
            file_name = name_bytes.decode("utf-8")

            file_size = struct.unpack("<Q", f_in.read(8))[0]  # Читаем размер файла 8б

            # Создаем файл и записываем в него данные
            out_path = os.path.join(folder_path, file_name)
            with open(out_path, "wb") as f_out:
                bytes_left = file_size
                while bytes_left > 0:
                    chunk = f_in.read(min(bytes_left, CHUNK_SIZE))
                    f_out.write(chunk)
                    bytes_left -= len(chunk)

    print(f"Архив {archive_name} успешно распакован в {folder_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "action",
        type=str,
        metavar="action",
        help="Действия с архивом: {create, add, rm, unpack}",
        choices=["create", "add", "rm", "unpack"],
    )
    parser.add_argument(
        "filename", type=str, help="Относительный/абсолютный путь архива"
    )
    parser.add_argument("path", type=str, help="Абсолютный путь")

    args = parser.parse_args()

    if args.action == "create":
        create_archive(args.filename, args.path)
    elif args.action == "add":
        add_file_to_archive(args.filename, args.path)
    elif args.action == "rm":
        pass
    else:
        unpack_archive(args.filename, args.path)
