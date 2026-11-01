"""程序入口：造书架，进命令行。

运行方式（在本目录下）：
    python3 main.py
"""

from cli import run
from data import build_books
from library import Library


def main() -> None:
    library = Library("第三周示范书架", build_books())
    run(library)


if __name__ == "__main__":
    main()
