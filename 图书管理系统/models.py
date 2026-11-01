"""图书管理系统的数据模型。

书 = 元信息 + 若干页；一页 = 页码 + 小标题 + 正文若干行。

这个模块只做三件事：
1. Page                         描述"一页"
2. Book                         抽象类，规定"一本书必须会做什么"
3. PythonBook / ROS2Book / UbuntuBook
                                三本具体书，只改写"怎么排版、怎么抽关键词"
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod


class BookError(Exception):
    """图书系统自己的异常类型。

    不直接抛 ValueError 的好处：调用方一眼能看出问题出在图书数据上，
    而不是某个随便写错的下标。
    """


class Page:
    """一页书。

    页码从 1 开始；正文用元组保存，因此外部拿到的只是内容，改不动它。
    """

    __slots__ = ("number", "title", "_lines")

    def __init__(self, number: int, title: str, lines: list[str]) -> None:
        if number < 1:
            raise BookError(f"页码必须从 1 开始，收到 {number}")
        self.number = number
        self.title = title
        self._lines = tuple(lines)

    @property
    def lines(self) -> tuple[str, ...]:
        return self._lines

    @property
    def text(self) -> str:
        return "\n".join(self._lines)

    @property
    def words(self) -> int:
        """粗略词数：去掉空格按字符数算，用来给检索结果做长度归一化。"""
        return sum(len(line.replace(" ", "")) for line in self._lines)

    def __repr__(self) -> str:
        return f"<Page {self.number} {self.title!r}>"


class Book(ABC):
    """一本书的抽象基类。

    所有书都一样的东西放这里：元信息、页列表、按页号取页、长度、遍历。
    各书不一样的只有两件事，声明成抽象方法，强制子类自己实现：

        render_page(page)  按本书的风格把一页排成文本
        keywords()         本书的领域词，用于检索加权

    没有实现这两个方法，Book 的子类连实例化都做不到。
    """

    tag = "通用"

    def __init__(
        self,
        isbn: str,
        title: str,
        author: str,
        year: int,
        pages: list[Page],
    ) -> None:
        if not pages:
            raise BookError(f"《{title}》至少要有一页")
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self._pages = list(pages)

    # ---------- 元信息与只读访问 ----------

    @property
    def pages(self) -> tuple[Page, ...]:
        """返回元组而不是内部列表，外面拿不到改内部状态的把手。"""
        return tuple(self._pages)

    def page(self, number: int) -> Page:
        if not 1 <= number <= len(self._pages):
            raise BookError(
                f"《{self.title}》只有 {len(self._pages)} 页，没有第 {number} 页"
            )
        return self._pages[number - 1]

    def brief(self) -> str:
        return (
            f"[{self.tag}] 《{self.title}》 {self.author} / {self.year} / "
            f"{len(self._pages)} 页 / ISBN {self.isbn}"
        )

    def __len__(self) -> int:
        return len(self._pages)

    def __iter__(self):
        return iter(self._pages)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.title!r}>"

    # ---------- 交给子类实现的部分 ----------

    @abstractmethod
    def render_page(self, page: Page) -> str:
        """按本书风格渲染一页：代码书编号、命令书加提示符、终端书进终端。"""

    @abstractmethod
    def keywords(self) -> set[str]:
        """本书的领域关键词。检索时命中这些词会加权。"""


def _identifiers(text: str) -> set[str]:
    """从文本里抽出英文标识符，供子类复用。"""
    return {word.lower() for word in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text)}


class PythonBook(Book):
    """Python 教程：正文按源码风格渲染，带行号。"""

    tag = "Python"

    def render_page(self, page: Page) -> str:
        rows = [f"── 《{self.title}》第 {page.number} 页 · {page.title} ──"]
        for number, line in enumerate(page.lines, start=1):
            rows.append(f"{number:>3} │ {line}")
        return "\n".join(rows)

    def keywords(self) -> set[str]:
        words = {"python", "切片", "列表", "异常", "self"}
        for page in self:
            words |= _identifiers(page.text)
        return words


class ROS2Book(Book):
    """ROS2 实战：命令行在终端里执行，所以要加 $ 提示符。"""

    tag = "ROS2"

    def render_page(self, page: Page) -> str:
        rows = [f"=== 《{self.title}》 P{page.number} · {page.title} ==="]
        for line in page.lines:
            if line.startswith(("ros2", "colcon", "source", "sudo")):
                rows.append(f"$ {line}")
            else:
                rows.append(f"    {line}")
        return "\n".join(rows)

    def keywords(self) -> set[str]:
        words = {"ros2", "node", "topic", "service", "launch", "colcon"}
        for page in self:
            words |= _identifiers(page.text)
        return words


class UbuntuBook(Book):
    """Ubuntu 运维：模拟一台机器上的终端输出。"""

    tag = "Ubuntu"

    def render_page(self, page: Page) -> str:
        rows = [f"user@ubuntu:~$ cat 《{self.title}》/第{page.number}页"]
        for line in page.lines:
            if line.startswith(("sudo", "apt", "systemctl", "ssh", "ls", "chmod", "df", "mount")):
                rows.append(f"user@ubuntu:~$ {line}")
            else:
                rows.append(f"  {line}")
        return "\n".join(rows)

    def keywords(self) -> set[str]:
        words = {"ubuntu", "apt", "systemd", "ssh", "chmod", "mount", "systemctl"}
        for page in self:
            words |= _identifiers(page.text)
        return words
