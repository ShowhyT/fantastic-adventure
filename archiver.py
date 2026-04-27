import argparse
import os
import struct
from io import BufferedReader, BufferedWriter

CHUNK_SIZE = 65536  # Сканируем по 64КБ для избежания заполнения памяти


def _pack_file(f_out: BufferedWriter, file_path: str) -> None:
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


def _write_file_data(
    f_in: BufferedReader,
    f_out: BufferedWriter,
    file_size: int,
):
    bytes_left = file_size
    while bytes_left > 0:
        chunk = f_in.read(min(bytes_left, CHUNK_SIZE))
        f_out.write(chunk)
        bytes_left -= len(chunk)


def create_archive(archive_name: str, dir_path: str) -> int:
    if not os.path.isdir(dir_path):
        return 1

    with open(archive_name, "wb") as f_out:
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                _pack_file(f_out, file_path)
    return 0


def add_file_to_archive(archive_name: str, file_path: str) -> int:
    if not os.path.exists(archive_name) or not os.path.exists(file_path):
        return 1
    with open(archive_name, "ab") as f_out:  # ab - режим дозаписи в архив
        _pack_file(f_out, file_path)
    return 0


def rm_file_from_archive(archive_name: str, file_path: str) -> int:
    if not os.path.exists(archive_name):
        return 2

    temp_archive = archive_name + ".tmp"
    file_deleted = False

    # Открываем старый архив на чтение, а новый временный - на запись.
    with open(archive_name, "rb") as f_in, open(temp_archive, "wb") as f_out:
        while True:
            name_len_bytes = f_in.read(2)
            if not name_len_bytes:
                break  # Дошли до конца файла

            name_len = struct.unpack("<H", name_len_bytes)[0]
            name_bytes = f_in.read(name_len)
            file_name = name_bytes.decode("utf-8")

            size_bytes = f_in.read(8)
            file_size = struct.unpack("<Q", size_bytes)[0]

            if file_name == os.path.basename(file_path):
                # Пропускаем файл перепрыгиванием на определенный офсет
                f_in.seek(file_size, os.SEEK_CUR)
                file_deleted = True
                continue
            else:
                f_out.write(name_len_bytes)
                f_out.write(name_bytes)
                f_out.write(size_bytes)
                _write_file_data(f_in, f_out, file_size)

    # Проверка на то, что файл удалился, если нет, то выводим ошибку
    if file_deleted:
        os.replace(temp_archive, archive_name)
        return 0
    else:
        return 1


def unpack_archive(archive_name: str, folder_path: str) -> int:
    if not os.path.exists(archive_name):
        return 1

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
            size_bytes = f_in.read(8)
            file_size = struct.unpack("<Q", size_bytes)[0]  # Читаем размер файла 8б

            # Создаем файл и записываем в него данные
            out_path = os.path.join(folder_path, file_name)
            with open(out_path, "wb") as f_out:
                _write_file_data(f_in, f_out, file_size)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "action",
        type=str,
        metavar="action",
        help="Действия с архивом: {create, add, rm, unpack}",
        choices=["create", "add", "rm", "unpack"],
    )
    parser.add_argument("filename", type=str, help="Путь до архива")
    parser.add_argument("path", type=str, help="Абсолютный путь до папки, файла")

    args = parser.parse_args()

    if args.action == "create":
        err = create_archive(args.filename, args.path)
        if err:
            print(f"Ошибка: {args.filename} не является папкой.")
        else:
            print(f"Архив {args.filename} успешно создан из папки {args.path}.")

    elif args.action == "add":
        err = add_file_to_archive(args.filename, args.path)
        if err:
            print("Ошибка, не существует файла, который вы хотите добавить, или архива")
        else:
            print(
                f"Файл {os.path.basename(args.path)} успешно добавлен в {args.filename}."
            )

    elif args.action == "rm":
        err = rm_file_from_archive(args.filename, args.path)
        if err == 1:
            print("Ошибка, не получилось удалить файл")
        elif err == 2:
            print("Ошибка: архив не существует")
        else:
            print(f"{os.path.basename(args.path)} успешно удален из {args.filename}.")

    else:
        err = unpack_archive(args.filename, args.path)
        if err:
            print(f"Ошибка, архив {args.filename} не найден/не существует")
        else:
            print(f"Архив {args.filename} успешно распакован в {args.path}.")
