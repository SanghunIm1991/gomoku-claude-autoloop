"""盤面表示層（COMP-04）。

tkinterのCanvasによる15x15マスの盤面描画・クリック検出を担う。対局のルール上の
状態（どのマスに何色の石があるか等）は保持せず、呼び出し元（COMP-03）からの指示
に基づいて描画するのみとする。

石は格子線の「交点」（15×15の交点、盤面外周からマス目の1辺のピクセルサイズの
半分の余白を空けた位置を起点にマス目の1辺のピクセルサイズ間隔で並ぶ座標）に
配置する（NFR-06関連の見直し、function_design.md FUNC-15/16/17参照）。
"""

import tkinter as tk
from typing import Callable, Optional, Tuple

BOARD_CELLS = 15
CELL_SIZE = 40
BOARD_PIXEL_SIZE = BOARD_CELLS * CELL_SIZE

_STONE_MARGIN = 4  # 石の円を交点から内側に離すための余白（ピクセル）
_GRID_MARGIN = CELL_SIZE // 2  # 格子線の起点（盤面外周から最初の交点までの余白、ピクセル）


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
        """Canvas上の描画内容をすべて消去し、15本×15本（計30本）の格子線を交点座標に再描画する。

        各線は、盤面外周からマス目の1辺のピクセルサイズの半分の余白を空けた位置を
        起点に、マス目の1辺のピクセルサイズの間隔で並ぶ交点と交点の間のみを結ぶ
        （盤面の外周ぎりぎりまでは伸ばさない）。これにより、石の中心座標（交点座標、
        draw_stoneが用いる座標と数値的に一致）と格子線の交点が一致する。
        """
        self._canvas.delete("all")
        cell = self._cell_size
        margin = _GRID_MARGIN
        first = margin
        last = margin + (BOARD_CELLS - 1) * cell
        for i in range(BOARD_CELLS):
            offset = margin + i * cell
            self._canvas.create_line(first, offset, last, offset)
            self._canvas.create_line(offset, first, offset, last)

    def draw_stone(self, row: int, col: int, color: str) -> None:
        """指定された行・列インデックスに対応する交点に、指定色で塗りつぶした円（石）を描画する。

        視認性確保（NFR-06）のため、塗りつぶし色（fill）に関わらず、円の輪郭線
        （outline）は黒色で固定して描画する。これにより白石が盤面の背景色（白）と
        同化せず判別可能になる。
        """
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
            outline="black",
        )

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Canvas上のピクセル座標を、最も近い交点の (row, col) に変換する。盤面外なら None。"""
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
