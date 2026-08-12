"""ステータス表示・操作パネル層（COMP-05）。

対局中の手番・勝敗・引き分けをテキストで表示するLabelと、リスタート用のButton
を扱う。対局のルール上の状態そのものは保持せず、呼び出し元（COMP-03）からの指示
に基づいて表示テキストを更新するのみとする。
"""

import tkinter as tk
from typing import Callable

_COLOR_LABEL = {"black": "黒", "white": "白"}


class StatusPanel:
    """手番／勝敗／引き分けのテキスト表示とリスタートボタンをまとめて扱う。"""

    def __init__(self, parent: tk.Widget, on_restart_click: Callable[[], None]) -> None:
        self._on_restart_click = on_restart_click

        self._status_label = tk.Label(parent, text="")
        self._status_label.pack()

        self._restart_button = tk.Button(
            parent, text="リスタート", command=self._on_restart_button_click
        )
        self._restart_button.pack()

    def show_turn(self, color: str) -> None:
        """現在の手番が color であることをテキストで表示する。"""
        self._status_label.config(text=f"{_COLOR_LABEL[color]}の番です")

    def show_winner(self, color: str) -> None:
        """color が勝利したことをテキストで表示する。"""
        self._status_label.config(text=f"{_COLOR_LABEL[color]}の勝ちです")

    def show_draw(self) -> None:
        """引き分けであることをテキストで表示する。"""
        self._status_label.config(text="引き分けです")

    def _on_restart_button_click(self) -> None:
        self._on_restart_click()
