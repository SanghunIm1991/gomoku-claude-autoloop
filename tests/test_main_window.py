"""COMP-03（メインウィンドウ・GUIコントローラ層 `MainWindow`）のテスト。

対応テストモジュールID: TESTMOD-04
テスト仕様書: docs/04_test/test_specification.md（COMP-03節、6.0〜6.2）を参照。

本モジュールは、`src/main_window.py` の `MainWindow` を対象に、以下2種類のテストを
組み合わせる（詳細な使い分けの理由はテスト仕様書6.0節を参照）。

- 単体テスト（FUNC-10〜FUNC-13）: `game_logic` 引数には、`make_move`/`restart` が
  呼ばれたときに任意の `MoveResult`/`RestartResult`（`src/game_logic.py` からimport）を
  返すテスト用のダブル（`_StubGameLogic`）を渡すことで、`MainWindow` 自身の分岐ロジックを
  実際の `GameLogic` の判定ロジックから切り離して検証する。`BoardView`・`StatusPanel` は
  実際のtkinterウィジェットを使い、実際に描画・表示テキストが更新されたかを確認する
  （これらは既にCOMP-04/05で単体テスト済みで信頼できるため、モックにはしない）。
- 結合テスト（統合シナリオ）: 実際の `GameLogic` インスタンスを使い、初期表示・有効な
  着手による表示更新・無効な着手（既着手マス・対局終了後）での表示不変・5連続勝利での
  勝敗表示・盤面満杯での引き分け表示・リスタートによる表示初期化という一連の流れを実際に
  動かして確認する。

`tk.Tk()` の生成・破棄は、プロジェクトルート直下の `conftest.py` に scope="session" で
定義された `tk_root` fixtureを `test_board_view.py`・`test_status_panel.py` と共有する。
本モジュールでは個別に定義しない。

各テスト関数のdocstring冒頭に対応するテストケースID（TEST-xx）を明記する。
"""

import time
import types

import pytest
import tkinter as tk

from board_view import BoardView, CELL_SIZE
from game_logic import GameLogic, MoveResult, RestartResult
from main_window import MainWindow
from status_panel import StatusPanel


# ---------------------------------------------------------------------------
# テストダブル・ヘルパー
# ---------------------------------------------------------------------------

class _StubGameLogic:
    """`GameLogic` の代わりに `MainWindow` へ渡すテスト用ダブル（スタブ）。

    `make_move`/`restart` は、コンストラクタで指定した `MoveResult`/`RestartResult` を
    そのまま返すのみで、実際の盤面・手番・勝敗判定ロジックは一切持たない。呼び出し引数・
    呼び出し回数を記録し、`MainWindow` がCOMP-02をどのように呼び出しているか（引数・
    呼び出しの有無）を検証するために用いる。FUNC-12/FUNC-13の分岐ロジックを、実際の
    `GameLogic` の判定ロジックから切り離して検証する単体テストのためのもの。
    """

    def __init__(self, move_result=None, restart_result=None):
        self.move_result = move_result
        self.restart_result = restart_result
        self.make_move_calls = []
        self.restart_calls = 0

    def make_move(self, row, col):
        self.make_move_calls.append((row, col))
        return self.move_result

    def restart(self):
        self.restart_calls += 1
        return self.restart_result


def _ovals(canvas):
    """Canvas上に描画されている石（`oval`）アイテムの一覧を返す。"""
    return [item for item in canvas.find_all() if canvas.type(item) == "oval"]


def _stone_bbox(row, col):
    """`BoardView.draw_stone` が描画する円のbounding boxを算出する。

    `src/board_view.py` の実装（`center = col*CELL_SIZE + CELL_SIZE//2` または
    `row*CELL_SIZE + CELL_SIZE//2`、`radius = CELL_SIZE//2 - _STONE_MARGIN(4)`）と
    同一の計算式であり、`tests/test_board_view.py` のTEST-37・TEST-38と同じ考え方に基づく。
    """
    cell = CELL_SIZE
    margin = 4  # src/board_view.py の _STONE_MARGIN と同じ値
    center_x = col * cell + cell // 2
    center_y = row * cell + cell // 2
    radius = cell // 2 - margin
    return (center_x - radius, center_y - radius, center_x + radius, center_y + radius)


def _play_black_horizontal_win(window):
    """(0,0)〜(0,4) の黒5連続で黒を勝利させる一連のクリックを行う（実際のGameLogicとの結合）。

    黒: (0,0),(0,1),(0,2),(0,3),(0,4) / 白: (1,0),(1,1),(1,2),(1,3) の順に交互着手し、
    黒の5個目の着手（(0,4)）で横方向の5連続が完成し黒勝利となる。
    """
    moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4)]
    for row, col in moves:
        window.on_board_click(row, col)


_DRAW_LAST_CELL = (14, 14)


def _draw_pattern_color(row, col):
    """テスト仕様書TEST-20（COMP-02節）と同じ安全パターン。

    `v = (2*row + col) % 5` が0または1なら黒、それ以外（2,3,4）なら白とする。このパターンに
    従えば、縦・横・斜め（右下がり・右上がり）いずれの方向でも、連続する5マス区間には必ず
    5つの余り（0〜4）が1回ずつ現れるため、5マス連続で同色になることがない。
    """
    v = (2 * row + col) % 5
    return "black" if v < 2 else "white"


def _setup_full_board_except_last_cell(game_logic):
    """`_DRAW_LAST_CELL` を残し、他の224マスに `_draw_pattern_color` に従った石を直接
    書き込むことで、あと1手で盤面が埋まる「引き分け確定直前」の状態を作る。

    ホワイトボックスによるセットアップ（`tests/test_game_logic.py` のTEST-20と同じ手法）。
    盤面が埋まるまで225回の実クリックを積み重ねる場合、色の割り当ては純粋に着手順の
    偶奇（先手黒・後手白の交互着手）で決まってしまい、`_draw_pattern_color` が要求する
    マスごとの色（黒113個・白112個という着手順由来の内訳とは一致しない配分）を狙って
    実現することができない。そのため、`GameLogic` の内部状態（`board`, `current_turn`,
    `game_state`）を直接構築したうえで、最後の1マスのみを実際に `MainWindow.on_board_click`
    経由でクリックし、COMP-03↔COMP-02の結合を確認する。
    """
    for row in range(15):
        for col in range(15):
            if (row, col) == _DRAW_LAST_CELL:
                continue
            game_logic.board[row][col] = _draw_pattern_color(row, col)
    game_logic.current_turn = _draw_pattern_color(*_DRAW_LAST_CELL)
    game_logic.game_state = "in_progress"


# ---------------------------------------------------------------------------
# fixture
# ---------------------------------------------------------------------------
#
# `tk_root`（非表示化した `tk.Tk()` ルートウィンドウ）は、プロジェクトルート直下の
# `conftest.py` に scope="session" で定義されたものを、`test_board_view.py`・
# `test_status_panel.py` とテストセッション全体で共有する。本モジュールでは個別に定義しない。

@pytest.fixture
def make_main_window(tk_root):
    """スタブ／実際のいずれかの `game_logic` を受け取り、そのつどテスト用に独立した
    親ウィジェット（`tk.Frame`）配下に `MainWindow` を1つ生成するファクトリ関数を返す。
    テスト終了後、生成した全フレーム（配下の `BoardView`・`StatusPanel` のウィジェットも
    含む）をまとめて破棄する（テスト間でのウィジェット・リソースのリーク防止）。

    `MainWindow.__init__` の `root` 引数の型注釈は `tk.Tk` だが、内部では `BoardView`・
    `StatusPanel` の生成時にそのまま `parent` として渡すのみであり、`tk.Widget` が持つ
    メソッド（`pack` 等）のみを利用する（関数設計書FUNC-10: 型注釈上 `tk.Widget` と `tk.Tk`
    は別クラスだが、tkinterの実装上 `Tk` は `Widget` と共通のメソッド（`Misc` 由来）を持つ
    ため実行時には問題なく動作する）。この性質を利用し、テストではテストごとに独立した
    `tk.Frame` を `root` として渡すことで、テスト間でウィジェットが競合せず、フレーム単位で
    まとめて破棄できるようにする。
    """
    frames = []

    def _make(game_logic):
        frame = tk.Frame(tk_root)
        frames.append(frame)
        window = MainWindow(frame, game_logic)
        return window

    yield _make

    for frame in frames:
        frame.destroy()


# ---------------------------------------------------------------------------
# FUNC-10: MainWindow.__init__（単体テスト、スタブ使用）
# ---------------------------------------------------------------------------

def test_58_init_creates_and_holds_board_view_status_panel_game_logic(make_main_window):
    """TEST-58: __init__によりBoardView・StatusPanelが生成され、self.board_view・
    self.status_panel・self.game_logicとして正しく保持される。

    対応要件ID: REQ-02, CON-05
    テスト対象(関数ID): FUNC-10
    """
    stub = _StubGameLogic()
    window = make_main_window(stub)

    assert isinstance(window.board_view, BoardView)
    assert isinstance(window.status_panel, StatusPanel)
    assert window.game_logic is stub


def test_59_init_wires_board_view_and_status_panel_callbacks_to_main_window(make_main_window):
    """TEST-59: BoardViewにはon_board_click、StatusPanelにはon_restart_clickがコールバック
    として渡され、実際のクリック操作・ボタン押下時にそれぞれが呼び出される。

    対応要件ID: REQ-04, REQ-13, CON-05
    テスト対象(関数ID): FUNC-10
    """
    move_result = MoveResult(
        valid=True, color="black", winner=None, is_draw=False,
        next_turn="white", game_over=False,
    )
    restart_result = RestartResult(success=True, next_turn="black")
    stub = _StubGameLogic(move_result=move_result, restart_result=restart_result)
    window = make_main_window(stub)

    window.board_view._on_canvas_click(types.SimpleNamespace(x=300, y=300))
    assert stub.make_move_calls == [(7, 7)]

    window.status_panel._restart_button.invoke()
    assert stub.restart_calls == 1


# ---------------------------------------------------------------------------
# FUNC-11: MainWindow._show_initial_state（単体テスト、スタブ使用）
# ---------------------------------------------------------------------------

def test_60_show_initial_state_displays_empty_board_and_black_turn(make_main_window):
    """TEST-60: MainWindow生成直後（コンストラクタ内で_show_initial_state()が呼ばれた結果）、
    表示が空の盤面・黒番表示になっている。

    対応要件ID: REQ-02, REQ-12
    テスト対象(関数ID): FUNC-11
    """
    stub = _StubGameLogic()
    window = make_main_window(stub)

    assert _ovals(window.board_view._canvas) == []
    assert window.status_panel._status_label.cget("text") == "黒の番です"


def test_61_show_initial_state_does_not_query_game_logic(make_main_window):
    """TEST-61: 初期表示が、game_logicへの問い合わせ（make_move/restart）を一切行わずに
    行われる。

    対応要件ID: REQ-02, REQ-12
    テスト対象(関数ID): FUNC-11
    """
    stub = _StubGameLogic()
    make_main_window(stub)

    assert stub.make_move_calls == []
    assert stub.restart_calls == 0


# ---------------------------------------------------------------------------
# FUNC-12: MainWindow.on_board_click（単体テスト、スタブ使用）
# ---------------------------------------------------------------------------

def test_62_on_board_click_invalid_result_does_not_update_board_or_status(make_main_window):
    """TEST-62: make_moveの結果がvalid=Falseの場合、BoardView・StatusPanelいずれにも
    更新指示が行われず、表示状態が変化しない（異常系）。

    対応要件ID: REQ-06, REQ-07
    テスト対象(関数ID): FUNC-12
    """
    invalid_result = MoveResult(
        valid=False, color=None, winner=None, is_draw=False,
        next_turn=None, game_over=False,
    )
    stub = _StubGameLogic(move_result=invalid_result)
    window = make_main_window(stub)
    canvas = window.board_view._canvas
    status_before = window.status_panel._status_label.cget("text")

    window.on_board_click(3, 3)

    assert _ovals(canvas) == []
    assert window.status_panel._status_label.cget("text") == status_before


@pytest.mark.parametrize(
    ("color", "cell", "expected_text"),
    [
        ("black", (7, 7), "黒の勝ちです"),
        ("white", (2, 10), "白の勝ちです"),
    ],
    ids=["black", "white"],
)
def test_63_64_on_board_click_winner_draws_stone_and_shows_winner(
    make_main_window, color, cell, expected_text
):
    """TEST-63/TEST-64: 着手により勝敗が確定した場合、盤面に該当色の石が描画され、
    StatusPanelに勝利表示がされる（境界値: 黒・白の両方を確認）。

    対応要件ID: REQ-04, REQ-05, REQ-08, REQ-10, CON-04
    テスト対象(関数ID): FUNC-12
    """
    row, col = cell
    move_result = MoveResult(
        valid=True, color=color, winner=color, is_draw=False,
        next_turn=None, game_over=True,
    )
    stub = _StubGameLogic(move_result=move_result)
    window = make_main_window(stub)

    window.on_board_click(row, col)

    canvas = window.board_view._canvas
    ovals = _ovals(canvas)
    assert len(ovals) == 1
    assert canvas.itemcget(ovals[0], "fill") == color
    assert tuple(int(v) for v in canvas.coords(ovals[0])) == _stone_bbox(row, col)
    assert window.status_panel._status_label.cget("text") == expected_text


def test_65_on_board_click_draw_draws_stone_and_shows_draw(make_main_window):
    """TEST-65: 着手により引き分けが確定した場合、盤面に石が描画され、StatusPanelに
    引き分け表示がされる。

    対応要件ID: REQ-04, REQ-05, REQ-09, REQ-11, CON-04
    テスト対象(関数ID): FUNC-12
    """
    move_result = MoveResult(
        valid=True, color="white", winner=None, is_draw=True,
        next_turn=None, game_over=True,
    )
    stub = _StubGameLogic(move_result=move_result)
    window = make_main_window(stub)

    window.on_board_click(14, 0)

    canvas = window.board_view._canvas
    ovals = _ovals(canvas)
    assert len(ovals) == 1
    assert canvas.itemcget(ovals[0], "fill") == "white"
    assert tuple(int(v) for v in canvas.coords(ovals[0])) == _stone_bbox(14, 0)
    assert window.status_panel._status_label.cget("text") == "引き分けです"


def test_66_on_board_click_continues_draws_stone_and_shows_next_turn(make_main_window):
    """TEST-66: 着手により対局が続行する場合（勝敗・引き分け未確定）、盤面に石が描画され、
    StatusPanelに次の手番表示がされる。

    対応要件ID: REQ-04, REQ-05, REQ-12
    テスト対象(関数ID): FUNC-12
    """
    move_result = MoveResult(
        valid=True, color="black", winner=None, is_draw=False,
        next_turn="white", game_over=False,
    )
    stub = _StubGameLogic(move_result=move_result)
    window = make_main_window(stub)

    window.on_board_click(0, 5)

    canvas = window.board_view._canvas
    ovals = _ovals(canvas)
    assert len(ovals) == 1
    assert canvas.itemcget(ovals[0], "fill") == "black"
    assert tuple(int(v) for v in canvas.coords(ovals[0])) == _stone_bbox(0, 5)
    assert window.status_panel._status_label.cget("text") == "白の番です"


def test_67_on_board_click_calls_make_move_with_given_coordinates(make_main_window):
    """TEST-67: on_board_clickに渡された(row, col)が、そのままgame_logic.make_move(row, col)に
    渡される。

    対応要件ID: REQ-04, NFR-05
    テスト対象(関数ID): FUNC-12
    """
    move_result = MoveResult(
        valid=True, color="black", winner=None, is_draw=False,
        next_turn="white", game_over=False,
    )
    stub = _StubGameLogic(move_result=move_result)
    window = make_main_window(stub)

    window.on_board_click(9, 4)

    assert stub.make_move_calls == [(9, 4)]


# ---------------------------------------------------------------------------
# FUNC-13: MainWindow.on_restart_click（単体テスト、スタブ使用）
# ---------------------------------------------------------------------------

def test_68_on_restart_click_calls_restart_and_reflects_returned_next_turn(make_main_window):
    """TEST-68: on_restart_clickが呼ばれると、game_logic.restart()が呼ばれ、その戻り値の
    next_turnがそのままStatusPanel.show_turnに渡され、盤面表示もクリアされる（実装が
    next_turnを決め打ちせず戻り値をそのまま使っていることを確認するため、実際には常に
    'black'であるはずのnext_turnにあえて'white'を返すスタブを用いる）。

    対応要件ID: REQ-13, NFR-05
    テスト対象(関数ID): FUNC-13
    """
    restart_result = RestartResult(success=True, next_turn="white")
    stub = _StubGameLogic(restart_result=restart_result)
    window = make_main_window(stub)
    window.board_view.draw_stone(4, 4, "black")
    assert len(_ovals(window.board_view._canvas)) == 1

    window.on_restart_click()

    assert stub.restart_calls == 1
    assert _ovals(window.board_view._canvas) == []
    assert window.status_panel._status_label.cget("text") == "白の番です"


# ---------------------------------------------------------------------------
# 結合テスト（実際のGameLogicを使用）
# ---------------------------------------------------------------------------

def test_69_integration_initial_display_is_empty_board_and_black_turn(make_main_window):
    """TEST-69: 実際のGameLogicと組み合わせた場合も、MainWindow生成直後の表示が空の盤面・
    黒番表示であることを確認する（結合テスト）。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-10, FUNC-11
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)

    assert _ovals(window.board_view._canvas) == []
    assert window.status_panel._status_label.cget("text") == "黒の番です"


def test_70_integration_valid_moves_update_board_and_turn_display(make_main_window):
    """TEST-70: 実際のGameLogicと組み合わせ、有効な着手を連続して行った際に、盤面描画と
    手番表示が正しく更新されることを確認する（結合テスト）。

    対応要件ID: REQ-04, REQ-05, REQ-12, CON-03
    テスト対象(関数ID): FUNC-12
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)
    canvas = window.board_view._canvas

    window.on_board_click(7, 7)
    ovals = _ovals(canvas)
    assert len(ovals) == 1
    assert canvas.itemcget(ovals[0], "fill") == "black"
    assert window.status_panel._status_label.cget("text") == "白の番です"

    window.on_board_click(0, 0)
    assert len(_ovals(canvas)) == 2
    assert window.status_panel._status_label.cget("text") == "黒の番です"


def test_71_integration_move_on_occupied_cell_does_not_change_display(make_main_window):
    """TEST-71: 実際のGameLogicと組み合わせ、既に石が置かれているマスへの再クリックで
    盤面・ステータス表示が変化しないことを確認する（結合テスト）。

    対応要件ID: REQ-06
    テスト対象(関数ID): FUNC-12
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)
    canvas = window.board_view._canvas

    window.on_board_click(5, 5)
    ovals_before = _ovals(canvas)
    status_before = window.status_panel._status_label.cget("text")
    assert len(ovals_before) == 1
    assert status_before == "白の番です"

    window.on_board_click(5, 5)

    assert _ovals(canvas) == ovals_before
    assert window.status_panel._status_label.cget("text") == status_before


def test_72_integration_five_in_a_row_shows_winner_and_further_clicks_are_ignored(make_main_window):
    """TEST-72: 実際のGameLogicと組み合わせ、黒が横方向に5連続する着手を行うと勝敗表示が
    され、勝利確定後の追加クリックでは表示が変化しないことを確認する（結合テスト）。

    対応要件ID: REQ-07, REQ-08, REQ-10, CON-04
    テスト対象(関数ID): FUNC-12
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)
    canvas = window.board_view._canvas

    _play_black_horizontal_win(window)

    assert window.status_panel._status_label.cget("text") == "黒の勝ちです"
    ovals_after_win = _ovals(canvas)
    assert len(ovals_after_win) == 9

    window.on_board_click(2, 2)

    assert _ovals(canvas) == ovals_after_win
    assert window.status_panel._status_label.cget("text") == "黒の勝ちです"


def test_73_integration_board_full_shows_draw(make_main_window):
    """TEST-73: 実際のGameLogicと組み合わせ、盤面が全マス埋まり勝者が出ないシナリオで、
    最後の着手により引き分け表示がされることを確認する（結合テスト）。

    対応要件ID: REQ-09, REQ-11
    テスト対象(関数ID): FUNC-12
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)
    _setup_full_board_except_last_cell(game_logic)
    last_row, last_col = _DRAW_LAST_CELL
    expected_color = _draw_pattern_color(last_row, last_col)

    window.on_board_click(last_row, last_col)

    canvas = window.board_view._canvas
    ovals = _ovals(canvas)
    assert len(ovals) == 1
    assert canvas.itemcget(ovals[0], "fill") == expected_color
    assert tuple(int(v) for v in canvas.coords(ovals[0])) == _stone_bbox(last_row, last_col)
    assert window.status_panel._status_label.cget("text") == "引き分けです"


@pytest.mark.parametrize("state", ["in_progress", "win", "draw"])
def test_74_integration_restart_from_any_state_resets_display(make_main_window, state):
    """TEST-74: 実際のGameLogicと組み合わせ、対局中・勝利確定後・引き分け確定後のいずれの
    状態からリスタートしても、盤面表示がクリアされ黒番表示に戻ることを確認する
    （結合テスト、境界値）。

    対応要件ID: REQ-13
    テスト対象(関数ID): FUNC-13
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)

    if state == "in_progress":
        window.on_board_click(6, 6)
    elif state == "win":
        _play_black_horizontal_win(window)
    else:
        _setup_full_board_except_last_cell(game_logic)
        last_row, last_col = _DRAW_LAST_CELL
        window.on_board_click(last_row, last_col)

    window.on_restart_click()

    canvas = window.board_view._canvas
    assert _ovals(canvas) == []
    assert window.status_panel._status_label.cget("text") == "黒の番です"


def test_75_integration_many_board_clicks_complete_without_noticeable_delay(make_main_window):
    """TEST-75: 実際のGameLogicと組み合わせ、盤面全マス相当（225回）分のon_board_click
    呼び出しが体感遅延なく完了する目安（1秒未満）を満たすことを確認する（結合テスト）。
    行を優先して順にクリックするため対局が早期に終了し得るが、対局終了後のクリックは
    無効な着手として例外を出さず即座に処理されるため、計測結果には影響しない。

    対応要件ID: NFR-04
    テスト対象(関数ID): FUNC-12
    """
    game_logic = GameLogic()
    window = make_main_window(game_logic)

    start = time.perf_counter()
    for row in range(15):
        for col in range(15):
            window.on_board_click(row, col)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0
