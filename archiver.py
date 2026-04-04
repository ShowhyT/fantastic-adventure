import argparse


def check_arcive():
    pass


def create_file():
    pass


parser = argparse.ArgumentParser(color=False)

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


if __name__ == "__main__":
    print(args)
