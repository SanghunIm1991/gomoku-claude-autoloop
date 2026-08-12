"""盤面表示層（COMP-04）。

tkinterのCanvasによる15x15マスの盤面描画・クリック検出を担う。対局のルール上の
状態（どのマスに何色の石があるか等）は保持せず、呼び出し元（COMP-03）からの指示
に基づいて描画するのみとする。
"""

import tkinter as tk
from typing import Callable, Optional, Tuple

BOARD_CELLS = 15
CELL_SIZE = 40
BOARD_PIXEL_SIZE = BOARD_CELLS * CELL_SIZE

_STONE_MARGIN = 4  # 石の円をマス目の枠線から内側に離すための余白（ピクセル）


class BoardView:
    """15×15マスの盤面をCanvas上に描画し、クリックを行・列インデックスに変換して通知する。"""

    def __init__(self, parent: tk.Widget, on_cell_click: Callable[[int, int], None]) -> None:
        self._on_cell_click = on_cell_click
        self._cell_size = CELL_SIZE
        self._board_pixel_size = BOARD_PIXEL_SIZE

        self._canvas = tk.Canvas(
            parent,
            width=self._board_pixel_size,
            height=self._board_pixel_size,
            bg="white",
            highlightthickness=0,
        )
        self._canvas.pack()
        self._canvas.bind("<Button-1>", self._on_canvas_click)

        self.draw_empty_board()

    def draw_empty_board(self) -> None:
        """Canvas上の描画内容をすべて消去し、15×15マス分の格子線のみを再描画する。"""
        self._canvas.delete("all")
        size = self._board_pixel_size
        cell = self._cell_size
        for i in range(BOARD_CELLS + 1):
            offset = i * cell
            self._canvas.create_line(0, offset, size, offset)
            self._canvas.create_line(offset, 0, offset, size)

    def draw_stone(self, row: int, col: int, color: str) -> None:
        """指定マスの中心に、指定色で塗りつぶした円（石）を描画する。"""
        cell = self._cell_size
        center_x = col * cell + cell // 2
        center_y = row * cell + cell // 2
        radius = cell // 2 - _STONE_MARGIN
        self._canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=color,
            outline=color,
        )

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Canvas上のピクセル座標を、対応する (row, col) に変換する。盤面外なら None。"""
        row = y // self._cell_size
        col = x // self._cell_size
        if 0 <= row <= BOARD_CELLS - 1 and 0 <= col <= BOARD_CELLS - 1:
            return (row, col)
        return None

    def _on_canvas_click(self, event: tk.Event) -> None:
        cell = self._pixel_to_cell(event.x, event.y)
        if cell is None:
            return
        row, col = cell
        self._on_cell_click(row, col)
