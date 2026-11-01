"""命令行界面。

这一层只做三件事：读指令、调 Library、打印结果。
它不认识 Page 的内部结构，也不知道检索是怎么算的——
这正是封装换来的好处：界面层可以随便换，检索算法也可以随便换。
"""

from library import Library
from models import BookError

HELP = """可用命令
  list                 列出书架上的书
  info <isbn>          看一本书的目录
  read <isbn> <页码>    读某一页（按这本书自己的风格排版）
  search <关键词>       检索内容，返回最相关的几页
  borrow <isbn> <名字>  借书
  giveback <isbn>      还书
  loans                查看借阅情况
  stats                看书架统计
  help / quit"""


def _need(args: list[str], count: int, usage: str) -> None:
    if len(args) < count:
        raise BookError(f"参数不够，用法：{usage}")


def _show_books(library: Library, args: list[str]) -> None:
    for book in library.books:
        mark = "（已借出）" if book.isbn in library.loans else ""
        print(book.brief() + mark)


def _show_info(library: Library, args: list[str]) -> None:
    _need(args, 1, "info <isbn>")
    book = library.get(args[0])
    print(book.brief())
    for page in book:
        print(f"  第 {page.number} 页  {page.title}（约 {page.words} 字）")


def _show_page(library: Library, args: list[str]) -> None:
    _need(args, 2, "read <isbn> <页码>")
    book = library.get(args[0])
    number = int(args[1])
    # 关键一行：同一个 render_page，不同的书给出不同排版
    print(book.render_page(book.page(number)))


def _show_search(library: Library, args: list[str]) -> None:
    _need(args, 1, "search <关键词>")
    query = " ".join(args)
    hits = library.search(query)
    if not hits:
        print(f"没有找到和「{query}」相关的内容")
        return
    for index, hit in enumerate(hits, start=1):
        print(f"{index}. {hit.where()}   相关度 {hit.score:.2f}")
    print("用 read <isbn> <页码> 查看具体内容")


def _borrow(library: Library, args: list[str]) -> None:
    _need(args, 2, "borrow <isbn> <名字>")
    library.borrow(args[0], " ".join(args[1:]))
    print(f"借出成功：《{library.get(args[0]).title}》")


def _give_back(library: Library, args: list[str]) -> None:
    _need(args, 1, "giveback <isbn>")
    who = library.give_back(args[0])
    print(f"归还成功，之前是 {who} 借的")


def _show_loans(library: Library, args: list[str]) -> None:
    loans = library.loans
    if not loans:
        print("现在没有书借出")
        return
    for isbn, who in loans.items():
        print(f"《{library.get(isbn).title}》  ->  {who}")


def _show_stats(library: Library, args: list[str]) -> None:
    for key, value in library.stats().items():
        print(f"{key}: {value}")


COMMANDS = {
    "list": _show_books,
    "info": _show_info,
    "read": _show_page,
    "search": _show_search,
    "borrow": _borrow,
    "giveback": _give_back,
    "loans": _show_loans,
    "stats": _show_stats,
}


def run(library: Library) -> None:
    print(f"欢迎来到「{library.name}」，输入 help 查看命令，quit 退出。")
    while True:
        try:
            raw = input("book> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            return
        if not raw:
            continue

        command, _, rest = raw.partition(" ")
        args = rest.split()

        if command in ("quit", "exit"):
            print("再见。")
            return
        if command == "help":
            print(HELP)
            continue

        handler = COMMANDS.get(command)
        if handler is None:
            print(f"没有「{command}」这个命令，输入 help 看看。")
            continue

        try:
            handler(library, args)
        except BookError as error:
            print(f"出错了：{error}")
        except ValueError as error:
            print(f"参数格式不对：{error}")
