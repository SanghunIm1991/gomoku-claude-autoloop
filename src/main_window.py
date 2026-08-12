"""メインウィンドウ・GUIコントローラ層（COMP-03）。

COMP-02（GameLogic）への着手・リスタート依頼と、COMP-04（BoardView）・
COMP-05（StatusPanel）への表示更新指示を仲介する。自身はtkinterウィジェット
を直接生成・配置するが、対局のルール上の状態（盤面・手番・勝敗）は保持せず、
すべてCOMP-02に問い合わせる。
"""

import tkinter as tk

from board_view import BoardView
from game_logic import GameLogic
from status_panel import StatusPanel


class MainWindow:
    """メインウィンドウ全体の構築と、GUI操作とゲームロジックの仲介を行うコントローラ。"""

    def __init__(self, root: tk.Tk, game_logic: GameLogic) -> None:
        self.game_logic = game_logic
        self.board_view = BoardView(root, self.on_board_click)
        self.status_panel = StatusPanel(root, self.on_restart_click)
        self._show_initial_state()

    def _show_initial_state(self) -> None:
        self.board_view.draw_empty_board()
        self.status_panel.show_turn('black')

    def on_board_click(self, row: int, col: int) -> None:
        result = self.game_logic.make_move(row, col)
        if not result.valid:
            return

        self.board_view.draw_stone(row, col, result.color)
        if result.game_over and result.winner is not None:
            self.status_panel.show_winner(result.winner)
        elif result.game_over and result.is_draw:
            self.status_panel.show_draw()
        elif not result.game_over:
            self.status_panel.show_turn(result.next_turn)

    def on_restart_click(self) -> None:
        result = self.game_logic.restart()
        self.board_view.draw_empty_board()
        self.status_panel.show_turn(result.next_turn)
