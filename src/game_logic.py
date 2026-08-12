"""ゲームロジック層（COMP-02）。

盤面状態・手番管理・勝敗判定を担う。tkinter等の外部ライブラリには依存しない。
"""

from dataclasses import dataclass
from typing import List, Optional

BOARD_SIZE = 15

# 4方向（横・縦・斜め右下がり・斜め右上がり）
_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


@dataclass
class MoveResult:
    """着手処理（make_move）の戻り値。"""

    valid: bool
    color: Optional[str]
    winner: Optional[str]
    is_draw: bool
    next_turn: Optional[str]
    game_over: bool


@dataclass
class RestartResult:
    """リスタート処理（restart）の戻り値。"""

    success: bool
    next_turn: str


class GameLogic:
    """五目並べのゲームロジック（盤面状態・手番管理・勝敗判定）。"""

    def __init__(self) -> None:
        self._reset_state()

    def restart(self) -> RestartResult:
        self._reset_state()
        return RestartResult(success=True, next_turn='black')

    def _reset_state(self) -> None:
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        self.current_turn: str = 'black'
        self.game_state: str = 'in_progress'

    def make_move(self, row: int, col: int) -> MoveResult:
        invalid_result = MoveResult(
            valid=False, color=None, winner=None, is_draw=False,
            next_turn=None, game_over=False,
        )

        if self.game_state != 'in_progress':
            return invalid_result
        if not self._is_within_board(row, col):
            return invalid_result
        if self.board[row][col] is not None:
            return invalid_result

        color = self.current_turn
        self.board[row][col] = color

        if self._check_win(row, col, color):
            self.game_state = 'black_win' if color == 'black' else 'white_win'
            return MoveResult(
                valid=True, color=color, winner=color, is_draw=False,
                next_turn=None, game_over=True,
            )

        if self._is_board_full():
            self.game_state = 'draw'
            return MoveResult(
                valid=True, color=color, winner=None, is_draw=True,
                next_turn=None, game_over=True,
            )

        next_turn = 'white' if color == 'black' else 'black'
        self.current_turn = next_turn
        return MoveResult(
            valid=True, color=color, winner=None, is_draw=False,
            next_turn=next_turn, game_over=False,
        )

    def _is_within_board(self, row: int, col: int) -> bool:
        return 0 <= row <= BOARD_SIZE - 1 and 0 <= col <= BOARD_SIZE - 1

    def _check_win(self, row: int, col: int, color: str) -> bool:
        for d_row, d_col in _DIRECTIONS:
            count = (
                1
                + self._count_consecutive(row, col, color, d_row, d_col)
                + self._count_consecutive(row, col, color, -d_row, -d_col)
            )
            if count >= 5:
                return True
        return False

    def _count_consecutive(
        self, row: int, col: int, color: str, d_row: int, d_col: int
    ) -> int:
        count = 0
        r, c = row + d_row, col + d_col
        while self._is_within_board(r, c) and self.board[r][c] == color:
            count += 1
            r += d_row
            c += d_col
        return count

    def _is_board_full(self) -> bool:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] is None:
                    return False
        return True
