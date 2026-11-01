"""Library：把一堆书变成一个能检索、能借出的书架。

对外只有四个动作：
    list / get / search / borrow / give_back

其中 search 是本周最重要的一课：
    我们不关心它内部怎么算，只关心它承诺的输入输出。
"""

from __future__ import annotations

import math
import re

from models import Book, BookError


class Hit:
    """一条检索结果：哪本书的第几页，相关度多少。"""

    def __init__(self, book: Book, page, score: float) -> None:
        self.book = book
        self.page = page
        self.score = score

    def where(self) -> str:
        return (
            f"[{self.book.tag}] 《{self.book.title}》"
            f"第 {self.page.number} 页 · {self.page.title}"
        )

    def __repr__(self) -> str:
        return f"<Hit {self.book.title} p{self.page.number} {self.score:.2f}>"


class Library:
    """一个书架。它"拥有"书，但不是书（组合，不是继承）。"""

    def __init__(self, name: str, books: list[Book]) -> None:
        if not books:
            raise BookError("书架不能是空的")
        self.name = name
        self._books = list(books)
        self._loans: dict[str, str] = {}
        self._index = self._build_index()

    # ---------- 对外的简单接口 ----------

    @property
    def books(self) -> tuple[Book, ...]:
        return tuple(self._books)

    @property
    def loans(self) -> dict[str, str]:
        """返回副本：外部拿到的字典改了也不影响真实借阅记录。"""
        return dict(self._loans)

    def add(self, book: Book) -> None:
        self._books.append(book)
        self._index = self._build_index()

    def get(self, isbn: str) -> Book:
        for book in self._books:
            if book.isbn == isbn:
                return book
        raise BookError(f"书架上没有 ISBN 为 {isbn} 的书")

    def search(self, query: str, limit: int = 5) -> list[Hit]:
        """输入一句话，返回最相关的若干页，越相关的排越前。

        这是本周唯一需要你记住的契约：
            search("怎么切片") -> [Hit, Hit, ...]
        """
        terms = self._tokenize(query)
        if not terms:
            return []

        hits: list[Hit] = []
        for book in self._books:
            for page in book:
                score = self._score(terms, book, page)
                if score > 0:
                    hits.append(Hit(book, page, score))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:limit]

    def borrow(self, isbn: str, who: str) -> None:
        book = self.get(isbn)
        who = who.strip()
        if not who:
            raise BookError("借书人不能为空")
        if isbn in self._loans:
            raise BookError(f"《{book.title}》已经被 {self._loans[isbn]} 借走了")
        self._loans[isbn] = who

    def give_back(self, isbn: str) -> str:
        if isbn not in self._loans:
            raise BookError("这本书没有借出记录")
        return self._loans.pop(isbn)

    def stats(self) -> dict[str, int]:
        books = self._books
        return {
            "书": len(books),
            "页": sum(len(book) for book in books),
            "字": sum(page.words for book in books for page in book),
            "在借": len(self._loans),
        }

    # ======================================================================
    # 下面是"故意写复杂"的实现细节。
    #
    # 你不需要看懂 _tokenize / _build_index / _score 里的循环和公式，
    # 也不需要知道 TF-IDF 是什么东西。
    #
    # 你只需要知道这条契约：
    #     给它一句话 -> 它给出若干 Hit，越相关的排越前
    #
    # 这就是封装：把复杂度关进黑盒，外面看不到乱糟糟的中间状态。
    # 这也是抽象：外面只认识 search 这一个名字，换个算法也不用改调用方。
    # ======================================================================

    def _tokenize(self, text: str) -> set[str]:
        """把一句话切成检索用的词：英文按标识符，中文按相邻两字切。"""
        lowered = text.lower()
        words = set(re.findall(r"[a-z_][a-z0-9_]*", lowered))
        for run in re.findall(r"[\u4e00-\u9fa5]+", lowered):
            if len(run) == 1:
                words.add(run)
            else:
                words.update(run[i : i + 2] for i in range(len(run) - 1))
        return {word for word in words if word.strip()}

    def _build_index(self) -> dict[str, int]:
        """倒排索引的简化版：记录每个词出现在多少个页面里。"""
        frequency: dict[str, int] = {}
        for book in self._books:
            for page in book:
                for term in self._tokenize(page.text):
                    frequency[term] = frequency.get(term, 0) + 1
        return frequency

    def _score(self, terms: set[str], book: Book, page) -> float:
        """TF-IDF 的小变种：词频越高越相关，越罕见的词权重越大。"""
        documents = sum(len(item) for item in self._books)
        text = page.text.lower()
        title = page.title.lower()
        domain = book.keywords()

        score = 0.0
        for term in terms:
            count = text.count(term)
            if not count:
                continue
            occurrence = self._index.get(term, 0) or 1
            inverse = math.log((documents + 1) / (occurrence + 1)) + 1.0
            weight = (1 + math.log(count)) * inverse
            if term in title:
                weight *= 1.8
            if term in domain:
                weight *= 1.2
            score += weight

        if not score:
            return 0.0
        length_penalty = math.sqrt(max(page.words, 1) / 80)
        return score / length_penalty
