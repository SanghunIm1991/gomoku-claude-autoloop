"""COMP-02（ゲームロジック層 `GameLogic`）の単体テスト。

対応テストモジュールID: TESTMOD-01
テスト仕様書: docs/04_test/test_specification.md（COMP-02節）を参照。

本モジュールはtkinter等のGUIライブラリに一切依存せず、`src/game_logic.py` の
`GameLogic` / `MoveResult` / `RestartResult` を直接importして検証する（NFR-05）。

各テスト関数のdocstring冒頭に対応するテストケースID（TEST-xx）を明記する。
"""

import time

import pytest

from game_logic import BOARD_SIZE, GameLogic, MoveResult, RestartResult


# ---------------------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------------------

def _pattern_color(row: int, col: int) -> str:
    """縦・横・斜め（右下がり・右上がり）のいずれの方向にも5連続同色を
    生じさせない安全な市松状パターンで、座標に対応する色を返す。

    v = (2*row + col) % 5 とすると、4方向（(0,1), (1,0), (1,1), (1,-1)）の
    いずれについても、移動量とv の変化量の組み合わせが 5 と互いに素になるため、
    どの方向へ連続する5マスを見ても v は 0〜4 の値をちょうど1回ずつ取る。
    そのためこの色分けでは、どの方向にも同色が5個以上連続することがない。
    """
    v = (2 * row + col) % 5
    return "black" if v < 2 else "white"


def _fill_board_no_win(game: GameLogic, exclude=None) -> None:
    """勝利条件を満たさない安全なパターンで盤面を埋める（内部属性を直接操作）。

    `exclude` に (row, col) を指定した場合、そのマスのみ空のまま残す。
    """
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if exclude is not None and (r, c) == exclude:
                continue
            game.board[r][c] = _pattern_color(r, c)


def _place_line(game: GameLogic, cells, color: str) -> None:
    """指定したマス群に直接同色の石を置く（着手処理を経由しない前提条件セットアップ用）。"""
    for r, c in cells:
        game.board[r][c] = color


# ---------------------------------------------------------------------------
# FUNC-02: 初期化（コンストラクタ） / FUNC-04: _reset_state
# ---------------------------------------------------------------------------

def test_01_initial_state_all_empty_black_turn_in_progress():
    """TEST-01: 初期状態は全マス空・手番黒・対局状態in_progressであること。

    REQ-01, REQ-02, REQ-13, CON-01, CON-02, CON-04 / FUNC-02, FUNC-04
    """
    game = GameLogic()

    assert len(game.board) == BOARD_SIZE
    for row in game.board:
        assert len(row) == BOARD_SIZE
        assert all(cell is None for cell in row)

    assert game.current_turn == "black"
    assert game.game_state == "in_progress"


# ---------------------------------------------------------------------------
# FUNC-06: _is_within_board
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("row,col", [(0, 0), (14, 14), (0, 14), (14, 0), (7, 7)])
def test_02_is_within_board_true_on_boundaries(row, col):
    """TEST-02: 盤面境界(0,14)を含む範囲内座標はTrueと判定されること。

    REQ-01, CON-02 / FUNC-06
    """
    game = GameLogic()
    assert game._is_within_board(row, col) is True


@pytest.mark.parametrize("row,col", [(-1, 0), (15, 0), (0, -1), (0, 15), (-1, -1), (15, 15)])
def test_03_is_within_board_false_out_of_range(row, col):
    """TEST-03: 盤面範囲外座標はFalseと判定されること。

    REQ-01, CON-02 / FUNC-06
    """
    game = GameLogic()
    assert game._is_within_board(row, col) is False


# ---------------------------------------------------------------------------
# FUNC-05: make_move（正常系）
# ---------------------------------------------------------------------------

def test_04_black_move_places_stone_and_switches_turn_to_white():
    """TEST-04: 黒番の正常着手で黒石が配置され、手番が白に切り替わること。

    REQ-04, REQ-05, CON-04 / FUNC-05
    """
    game = GameLogic()
    result = game.make_move(7, 7)

    assert result == MoveResult(
        valid=True, color="black", winner=None, is_draw=False,
        next_turn="white", game_over=False,
    )
    assert game.board[7][7] == "black"
    assert game.current_turn == "white"
    assert game.game_state == "in_progress"


def test_05_white_move_places_stone_and_switches_turn_to_black():
    """TEST-05: 白番の正常着手で白石が配置され、手番が黒に切り替わること。

    REQ-04, REQ-05, CON-04 / FUNC-05
    """
    game = GameLogic()
    game.make_move(0, 0)  # 黒
    result = game.make_move(1, 1)  # 白

    assert result == MoveResult(
        valid=True, color="white", winner=None, is_draw=False,
        next_turn="black", game_over=False,
    )
    assert game.board[1][1] == "white"
    assert game.current_turn == "black"


def test_06_move_at_top_left_corner_succeeds():
    """TEST-06: 盤面端(0,0)への配置が正常に成功すること（境界値）。

    REQ-04 / FUNC-05
    """
    game = GameLogic()
    result = game.make_move(0, 0)

    assert result.valid is True
    assert game.board[0][0] == "black"


def test_07_move_at_bottom_right_corner_succeeds():
    """TEST-07: 盤面端(14,14)への配置が正常に成功すること（境界値）。

    REQ-04 / FUNC-05
    """
    game = GameLogic()
    result = game.make_move(14, 14)

    assert result.valid is True
    assert game.board[14][14] == "black"


# ---------------------------------------------------------------------------
# FUNC-05: make_move（異常系）
# ---------------------------------------------------------------------------

def test_08_move_on_occupied_cell_is_invalid_and_state_unchanged():
    """TEST-08: 既に石が置かれているマスへの配置は無効で、盤面・手番が変化しないこと。

    REQ-06 / FUNC-05
    """
    game = GameLogic()
    game.make_move(3, 3)  # 黒配置、手番は白へ

    result = game.make_move(3, 3)

    assert result == MoveResult(
        valid=False, color=None, winner=None, is_draw=False,
        next_turn=None, game_over=False,
    )
    assert game.board[3][3] == "black"  # 上書きされていない
    assert game.current_turn == "white"  # 手番も変化しない


@pytest.mark.parametrize("game_state", ["black_win", "white_win", "draw"])
def test_09_10_11_move_after_game_over_is_invalid(game_state):
    """TEST-09/10/11: 黒勝利後・白勝利後・引き分け後のいずれも、着手は無効となり
    盤面状態が変化しないこと。

    REQ-07 / FUNC-05
    """
    game = GameLogic()
    game.game_state = game_state  # 対局終了状態を直接セット（前提条件）

    result = game.make_move(5, 5)

    assert result == MoveResult(
        valid=False, color=None, winner=None, is_draw=False,
        next_turn=None, game_over=False,
    )
    assert game.board[5][5] is None
    assert game.game_state == game_state


@pytest.mark.parametrize(
    "row,col",
    [(-1, 0), (15, 0), (0, -1), (0, 15), (-1, -1), (15, 15), (100, 100)],
)
def test_12_move_out_of_range_is_invalid_no_exception(row, col):
    """TEST-12: 盤面範囲外の座標への着手は例外を送出せず、無効として扱われること。

    REQ-04, CON-02 / FUNC-05, FUNC-06
    """
    game = GameLogic()

    result = game.make_move(row, col)

    assert result == MoveResult(
        valid=False, color=None, winner=None, is_draw=False,
        next_turn=None, game_over=False,
    )
    assert game.current_turn == "black"
    assert game.game_state == "in_progress"


# ---------------------------------------------------------------------------
# FUNC-05 / FUNC-07 / FUNC-08: 勝敗判定（4方向・境界値）
# ---------------------------------------------------------------------------

def test_13_horizontal_five_in_a_row_wins():
    """TEST-13: 横方向にちょうど5個連続で黒が勝利すること。

    REQ-08 / FUNC-05, FUNC-07, FUNC-08
    """
    game = GameLogic()
    _place_line(game, [(7, 3), (7, 4), (7, 5), (7, 6)], "black")
    game.current_turn = "black"

    result = game.make_move(7, 7)

    assert result.valid is True
    assert result.winner == "black"
    assert result.game_over is True
    assert result.is_draw is False
    assert result.next_turn is None
    assert game.game_state == "black_win"


def test_14_vertical_five_in_a_row_wins():
    """TEST-14: 縦方向にちょうど5個連続で白が勝利すること。

    REQ-08 / FUNC-05, FUNC-07, FUNC-08
    """
    game = GameLogic()
    _place_line(game, [(2, 5), (3, 5), (4, 5), (5, 5)], "white")
    game.current_turn = "white"

    result = game.make_move(6, 5)

    assert result.valid is True
    assert result.winner == "white"
    assert result.game_over is True
    assert game.game_state == "white_win"


def test_15_diagonal_down_right_five_in_a_row_wins():
    """TEST-15: 斜め右下がり方向にちょうど5個連続で黒が勝利すること。

    REQ-08 / FUNC-05, FUNC-07, FUNC-08
    """
    game = GameLogic()
    _place_line(game, [(0, 0), (1, 1), (2, 2), (3, 3)], "black")
    game.current_turn = "black"

    result = game.make_move(4, 4)

    assert result.valid is True
    assert result.winner == "black"
    assert game.game_state == "black_win"


def test_16_diagonal_up_right_five_in_a_row_wins():
    """TEST-16: 斜め右上がり方向にちょうど5個連続で白が勝利すること。

    REQ-08 / FUNC-05, FUNC-07, FUNC-08
    """
    game = GameLogic()
    _place_line(game, [(4, 0), (3, 1), (2, 2), (1, 3)], "white")
    game.current_turn = "white"

    result = game.make_move(0, 4)

    assert result.valid is True
    assert result.winner == "white"
    assert game.game_state == "white_win"


def test_17_six_in_a_row_also_wins():
    """TEST-17: 5個ちょうどではなく6個以上連続する場合も勝利と判定されること。

    REQ-08（境界値） / FUNC-05, FUNC-07
    """
    game = GameLogic()
    _place_line(game, [(9, 3), (9, 4), (9, 5), (9, 6), (9, 7)], "black")
    game.current_turn = "black"

    result = game.make_move(9, 8)  # 追加で6個連続になる

    assert result.valid is True
    assert result.winner == "black"
    assert result.game_over is True
    assert game.game_state == "black_win"


def test_18_four_in_a_row_does_not_win():
    """TEST-18: 4個連続では勝利判定にならないこと（境界値）。

    REQ-08（境界値） / FUNC-05, FUNC-07
    """
    game = GameLogic()
    _place_line(game, [(10, 3), (10, 4), (10, 5)], "black")
    game.current_turn = "black"

    result = game.make_move(10, 6)  # 4個連続になるが5未満

    assert result.valid is True
    assert result.winner is None
    assert result.game_over is False
    assert result.next_turn == "white"
    assert game.game_state == "in_progress"


def test_19_turn_does_not_switch_when_game_is_won():
    """TEST-19: 勝敗が確定した着手では手番が切り替わらないこと（戻り値・内部状態の両面）。

    REQ-05, REQ-08 / FUNC-05
    """
    game = GameLogic()
    _place_line(game, [(1, 1), (1, 2), (1, 3), (1, 4)], "black")
    game.current_turn = "black"

    result = game.make_move(1, 5)

    assert result.next_turn is None
    assert game.current_turn == "black"  # 勝者の色のまま、白へ切り替わっていない

    # 対局終了後の着手が無効であることも合わせて確認する（REQ-07の再確認）。
    follow_up = game.make_move(1, 6)
    assert follow_up.valid is False


# ---------------------------------------------------------------------------
# FUNC-05 / FUNC-09: 引き分け判定（境界値）
# ---------------------------------------------------------------------------

def test_20_board_full_without_winner_is_draw():
    """TEST-20: 225マスすべてが埋まり、かつ勝利条件を満たす色がない場合は
    引き分けが確定すること。

    REQ-09 / FUNC-05, FUNC-09
    """
    game = GameLogic()
    last_cell = (14, 14)
    _fill_board_no_win(game, exclude=last_cell)
    game.current_turn = _pattern_color(*last_cell)

    result = game.make_move(*last_cell)

    assert result.valid is True
    assert result.winner is None
    assert result.is_draw is True
    assert result.game_over is True
    assert game.game_state == "draw"
    assert game._is_board_full() is True


def test_21_board_with_one_empty_cell_is_not_full():
    """TEST-21: 224マス埋まり1マスのみ空の場合、盤面充填チェックはFalseとなること（境界値）。

    REQ-09（境界値） / FUNC-09
    """
    game = GameLogic()
    _fill_board_no_win(game, exclude=(0, 0))

    assert game._is_board_full() is False


def test_22_turn_does_not_switch_when_draw_is_confirmed():
    """TEST-22: 引き分けが確定した着手では手番が切り替わらないこと。

    REQ-05, REQ-09 / FUNC-05
    """
    game = GameLogic()
    last_cell = (14, 14)
    _fill_board_no_win(game, exclude=last_cell)
    mover_color = _pattern_color(*last_cell)
    game.current_turn = mover_color

    result = game.make_move(*last_cell)

    assert result.next_turn is None
    assert game.current_turn == mover_color  # 切り替わっていない


# ---------------------------------------------------------------------------
# FUNC-03: restart / FUNC-04: _reset_state
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "setup_state",
    ["in_progress", "black_win", "white_win", "draw"],
)
def test_23_24_25_26_restart_from_any_state_resets_to_initial(setup_state):
    """TEST-23/24/25/26: 対局中・黒勝利後・白勝利後・引き分け後のいずれの状態から
    リスタートを呼び出しても、常に同一の初期状態（全マス空・黒番・対局中）に戻ること。

    REQ-13 / FUNC-03
    """
    game = GameLogic()
    game.make_move(6, 6)  # 何らかの着手で状態を変化させておく
    game.game_state = setup_state
    if setup_state != "in_progress":
        game.current_turn = "white"  # 終了状態では手番も適当な値にしておく

    result = game.restart()

    assert result == RestartResult(success=True, next_turn="black")
    assert game.current_turn == "black"
    assert game.game_state == "in_progress"
    for row in game.board:
        assert all(cell is None for cell in row)


def test_27_move_is_accepted_after_restart_and_board_is_clear():
    """TEST-27: リスタート後は盤面がクリアされ、通常どおり着手を受け付けること。

    REQ-13 / FUNC-03, FUNC-05
    """
    game = GameLogic()
    game.make_move(6, 6)
    game.restart()

    assert game.board[6][6] is None

    result = game.make_move(6, 6)
    assert result.valid is True
    assert result.color == "black"
    assert game.board[6][6] == "black"


# ---------------------------------------------------------------------------
# FUNC-08: _count_consecutive（境界値）
# ---------------------------------------------------------------------------

def test_28_count_consecutive_returns_zero_when_blocked():
    """TEST-28: 起点の隣接マスが盤面外・空・異色のいずれかの場合、連続数は0を
    返すこと。

    REQ-08 / FUNC-08
    """
    game = GameLogic()

    # 盤面端で、指定方向が盤面外に出るケース。
    assert game._count_consecutive(0, 0, "black", -1, -1) == 0

    # 隣接マスが空のケース。
    game.board[7][7] = "black"
    assert game._count_consecutive(7, 7, "black", 0, 1) == 0

    # 隣接マスが異色のケース。
    game.board[7][8] = "white"
    assert game._count_consecutive(7, 7, "black", 0, 1) == 0


# ---------------------------------------------------------------------------
# FUNC-05: MoveResultの全フィールド確認（異常系）
# ---------------------------------------------------------------------------

def test_29_invalid_move_result_fields_are_all_default():
    """TEST-29: 無効な着手の場合、MoveResultの全フィールドが仕様どおりの
    デフォルト値（valid=False, color=None, winner=None, is_draw=False,
    next_turn=None, game_over=False）であること。

    REQ-06, REQ-07 / FUNC-05
    """
    game = GameLogic()
    game.make_move(0, 0)  # 既着手マスを作る

    result = game.make_move(0, 0)

    assert result.valid is False
    assert result.color is None
    assert result.winner is None
    assert result.is_draw is False
    assert result.next_turn is None
    assert result.game_over is False


# ---------------------------------------------------------------------------
# NFR-04: 応答性能の目安確認
# ---------------------------------------------------------------------------

def test_30_many_moves_complete_without_noticeable_delay():
    """TEST-30: 盤面全マス相当（225回）分のmake_move呼び出しを行っても、
    体感遅延なく完了する（1秒未満）目安を満たすこと。

    NFR-04 / FUNC-05
    """
    game = GameLogic()

    start = time.perf_counter()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            game.make_move(r, c)
    elapsed = time.perf_counter() - start

    # 実際のGUI操作では1クリックあたり1秒未満(NFR-04)であればよいが、
    # ここでは225回分をまとめて実行しても十分高速であることを、
    # 余裕を持った閾値で確認する（目安確認であり厳密な性能測定ではない）。
    assert elapsed < 1.0


# ---------------------------------------------------------------------------
# NFR-05: GUIライブラリ非依存の確認
# ---------------------------------------------------------------------------

def test_31_game_logic_module_does_not_depend_on_tkinter():
    """TEST-31: game_logicモジュールがtkinter等のGUIライブラリに依存していないこと。

    docstring等のコメント中に「tkinterに依存しない」という説明文が含まれていても
    誤検知しないよう、単純な文字列検索ではなくASTでimport文のみを解析して判定する。

    NFR-05 / FUNC-02〜FUNC-09（モジュール全体）
    """
    import ast

    import game_logic as game_logic_module

    with open(game_logic_module.__file__, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_names.append(node.module)

    assert not any(name.startswith("tkinter") for name in imported_names), imported_names
    assert not hasattr(game_logic_module, "tkinter")
    assert not hasattr(game_logic_module, "tk")
