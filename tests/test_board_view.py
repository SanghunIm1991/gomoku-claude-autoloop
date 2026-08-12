"""COMP-04（盤面表示層 `BoardView`）の単体テスト。

対応テストモジュールID: TESTMOD-02
テスト仕様書: docs/04_test/test_specification.md（COMP-04節、4.0〜4.2）を参照。

本モジュールは、`src/board_view.py` の `BoardView` を対象に、実際に `tkinter.Tk()` を
生成し（`root.withdraw()` で非表示化）、その配下に `BoardView` を構築したうえで、
`Canvas` 上に実際に描画されたアイテム（`find_all()` / `itemcget()` / `coords()` /
`type()`）を検証するホワイトボックステストを行う。クリックイベントの検証は、
`tkinter.Event` を模した `types.SimpleNamespace(x=.., y=..)` を用いて
`_on_canvas_click` を直接呼び出す方法を採用する。

各テスト関数のdocstring冒頭に対応するテストケースID（TEST-xx）を明記する。
"""

import time
import types

import pytest
import tkinter as tk

from board_view import BOARD_CELLS, BOARD_PIXEL_SIZE, CELL_SIZE, BoardView


# ---------------------------------------------------------------------------
# fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk_root():
    """非表示化した `tk.Tk()` ルートウィンドウをモジュール内で1つだけ共有し、本モジュールの
    全テスト終了後に破棄する。

    `tk.Tk()`（Tclインタプリタの生成）をテスト関数ごとに毎回生成・破棄すると、環境によっては
    Tclライブラリファイルの再読み込みが短時間に連続することで一時的なファイル読み込みエラー
    （`couldn't read file ... tk.tcl` 等）が発生することがある（実際に本モジュール開発時に
    複数のテストで散発的に発生することを確認した。これはPython/tkinter/実装コードの不具合では
    なく、Tclインタプリタの生成回数に起因する環境依存の問題である）。この事象を避けるため、
    `tk.Tk()` の生成・破棄はモジュール全体で1回のみとし、各テストで必要な `Canvas`
    （`BoardView` ごと）はテスト関数単位で生成・破棄する（`board_view` fixture参照）。
    """
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def click_recorder():
    """`on_cell_click` コールバックの呼び出し履歴を記録するための入れ物を返す。"""
    calls = []

    def on_click(row, col):
        calls.append((row, col))

    return calls, on_click


@pytest.fixture
def board_view(tk_root, click_recorder):
    """共有の `tk_root` を親として `BoardView`（と、その内部のCanvas）をテストごとに1つ生成し、
    テスト終了後にCanvasを破棄する（テスト間でのウィジェット・リソースのリーク防止）。
    """
    calls, on_click = click_recorder
    view = BoardView(tk_root, on_click)
    yield view, calls
    view._canvas.destroy()


# ---------------------------------------------------------------------------
# FUNC-14: BoardView.__init__
# ---------------------------------------------------------------------------

def test_32_init_creates_canvas_with_board_pixel_size(board_view):
    """TEST-32: 初期化により、盤面全体サイズ(600x600)のCanvasがparent配下に生成・配置される。

    対応要件ID: REQ-01, REQ-02, CON-02
    テスト対象(関数ID): FUNC-14
    """
    view, _calls = board_view
    canvas = view._canvas
    assert isinstance(canvas, tk.Canvas)
    assert int(canvas.cget("width")) == BOARD_PIXEL_SIZE
    assert int(canvas.cget("height")) == BOARD_PIXEL_SIZE
    assert BOARD_PIXEL_SIZE == BOARD_CELLS * CELL_SIZE == 600


def test_33_init_binds_button1_to_on_canvas_click(board_view):
    """TEST-33: 初期化時、Canvasの<Button-1>イベントに_on_canvas_clickへのバインドが設定される。

    対応要件ID: REQ-04
    テスト対象(関数ID): FUNC-14
    """
    view, _calls = board_view
    binding = view._canvas.bind("<Button-1>")
    assert binding != ""


def test_34_init_calls_draw_empty_board_and_draws_grid_lines_only(board_view):
    """TEST-34: 初期化直後にdraw_empty_board()が呼ばれ、格子線のみが描画され石は存在しない。

    対応要件ID: REQ-01, REQ-02, CON-02
    テスト対象(関数ID): FUNC-14
    """
    view, _calls = board_view
    canvas = view._canvas
    items = canvas.find_all()
    assert len(items) == 32
    for item in items:
        assert canvas.type(item) == "line"
    assert all(canvas.type(item) != "oval" for item in items)


# ---------------------------------------------------------------------------
# FUNC-15: BoardView.draw_empty_board
# ---------------------------------------------------------------------------

def test_35_draw_empty_board_draws_grid_lines_with_correct_coordinates(board_view):
    """TEST-35: draw_empty_board()により、15x15マス分の格子線が正しい座標で描画される。

    対応要件ID: REQ-01, REQ-02, CON-02
    テスト対象(関数ID): FUNC-15
    """
    view, _calls = board_view
    canvas = view._canvas

    view.draw_empty_board()

    items = canvas.find_all()
    actual_coords = {tuple(int(v) for v in canvas.coords(item)) for item in items}

    expected_h = {(0, i * CELL_SIZE, BOARD_PIXEL_SIZE, i * CELL_SIZE) for i in range(BOARD_CELLS + 1)}
    expected_v = {(i * CELL_SIZE, 0, i * CELL_SIZE, BOARD_PIXEL_SIZE) for i in range(BOARD_CELLS + 1)}
    expected = expected_h | expected_v

    assert len(items) == 32
    assert actual_coords == expected
    assert all(canvas.type(item) != "oval" for item in items)


def test_36_draw_empty_board_clears_existing_stones(board_view):
    """TEST-36: 石が描画された状態からdraw_empty_board()を呼ぶと、石が消去され格子線のみになる。

    対応要件ID: REQ-13
    テスト対象(関数ID): FUNC-15, FUNC-16
    """
    view, _calls = board_view
    canvas = view._canvas

    view.draw_stone(5, 5, "black")
    view.draw_stone(2, 2, "white")

    ovals_before = [item for item in canvas.find_all() if canvas.type(item) == "oval"]
    assert len(ovals_before) == 2

    view.draw_empty_board()

    items_after = canvas.find_all()
    assert len(items_after) == 32
    assert all(canvas.type(item) == "line" for item in items_after)
    ovals_after = [item for item in items_after if canvas.type(item) == "oval"]
    assert len(ovals_after) == 0


# ---------------------------------------------------------------------------
# FUNC-16: BoardView.draw_stone
# ---------------------------------------------------------------------------

def test_37_draw_stone_draws_circle_of_specified_color_at_cell_center(board_view):
    """TEST-37: 指定マスの中心に指定色(黒・白)で塗りつぶした円が描画される。

    対応要件ID: REQ-04, CON-04, NFR-04
    テスト対象(関数ID): FUNC-16
    """
    view, _calls = board_view
    canvas = view._canvas

    view.draw_stone(7, 7, "black")
    view.draw_stone(3, 10, "white")

    ovals = [item for item in canvas.find_all() if canvas.type(item) == "oval"]
    assert len(ovals) == 2

    black_oval, white_oval = ovals[0], ovals[1]

    assert tuple(int(v) for v in canvas.coords(black_oval)) == (284, 284, 316, 316)
    assert canvas.itemcget(black_oval, "fill") == "black"

    assert tuple(int(v) for v in canvas.coords(white_oval)) == (404, 124, 436, 156)
    assert canvas.itemcget(white_oval, "fill") == "white"


def test_38_draw_stone_at_board_corners_top_left_and_bottom_right(board_view):
    """TEST-38: 盤面端(0,0)・(14,14)への石描画が正しい中心位置に行われる(境界値)。

    対応要件ID: REQ-04, CON-02, CON-04
    テスト対象(関数ID): FUNC-16
    """
    view, _calls = board_view
    canvas = view._canvas

    view.draw_stone(0, 0, "black")
    view.draw_stone(14, 14, "white")

    ovals = [item for item in canvas.find_all() if canvas.type(item) == "oval"]
    assert len(ovals) == 2

    top_left_oval, bottom_right_oval = ovals[0], ovals[1]

    assert tuple(int(v) for v in canvas.coords(top_left_oval)) == (4, 4, 36, 36)
    assert tuple(int(v) for v in canvas.coords(bottom_right_oval)) == (564, 564, 596, 596)


# ---------------------------------------------------------------------------
# FUNC-17: BoardView._pixel_to_cell
# ---------------------------------------------------------------------------

def test_39_pixel_to_cell_boundary_falls_to_next_cell(board_view):
    """TEST-39: マス境界線ちょうどの座標は、切り捨てにより下側・右側に隣接するマスに属する(境界値)。

    対応要件ID: REQ-04, CON-02
    テスト対象(関数ID): FUNC-17
    """
    view, _calls = board_view

    assert view._pixel_to_cell(40, 0) == (0, 1)
    assert view._pixel_to_cell(0, 40) == (1, 0)
    assert view._pixel_to_cell(40, 40) == (1, 1)


def test_40_pixel_to_cell_top_left_pixel_is_cell_0_0(board_view):
    """TEST-40: 盤面左上端のピクセル(0,0)が(0,0)セルに対応する(境界値)。

    対応要件ID: REQ-04, CON-02
    テスト対象(関数ID): FUNC-17
    """
    view, _calls = board_view

    assert view._pixel_to_cell(0, 0) == (0, 0)


def test_41_pixel_to_cell_last_pixel_is_cell_14_14(board_view):
    """TEST-41: 盤面右下端の最終ピクセル(BOARD_PIXEL_SIZE-1)が(14,14)セルに対応する(境界値)。

    対応要件ID: REQ-04, CON-02
    テスト対象(関数ID): FUNC-17
    """
    view, _calls = board_view

    assert view._pixel_to_cell(BOARD_PIXEL_SIZE - 1, BOARD_PIXEL_SIZE - 1) == (14, 14)


def test_42_pixel_to_cell_equal_to_board_pixel_size_returns_none(board_view):
    """TEST-42: 盤面ピクセルサイズとちょうど等しい座標はNoneを返す(境界値)。

    対応要件ID: REQ-04, CON-02
    テスト対象(関数ID): FUNC-17
    """
    view, _calls = board_view

    assert view._pixel_to_cell(BOARD_PIXEL_SIZE, BOARD_PIXEL_SIZE) is None
    assert view._pixel_to_cell(BOARD_PIXEL_SIZE, 300) is None
    assert view._pixel_to_cell(300, BOARD_PIXEL_SIZE) is None


def test_43_pixel_to_cell_negative_and_over_board_pixel_size_returns_none(board_view):
    """TEST-43: 負の座標、および盤面ピクセルサイズを超える座標はNoneを返す(異常系)。

    対応要件ID: REQ-04, CON-02
    テスト対象(関数ID): FUNC-17
    """
    view, _calls = board_view

    assert view._pixel_to_cell(-1, -1) is None
    assert view._pixel_to_cell(-1, 300) is None
    assert view._pixel_to_cell(300, -1) is None
    assert view._pixel_to_cell(BOARD_PIXEL_SIZE + 1, BOARD_PIXEL_SIZE + 1) is None
    assert view._pixel_to_cell(1000, 1000) is None


# ---------------------------------------------------------------------------
# FUNC-18: BoardView._on_canvas_click
# ---------------------------------------------------------------------------

def test_44_on_canvas_click_inside_board_invokes_callback_with_correct_cell(board_view):
    """TEST-44: 盤面内クリックで、on_cell_clickコールバックが正しい(row,col)で1回呼ばれる。

    対応要件ID: REQ-04
    テスト対象(関数ID): FUNC-18
    """
    view, calls = board_view

    view._on_canvas_click(types.SimpleNamespace(x=300, y=300))
    assert calls == [(7, 7)]

    view._on_canvas_click(types.SimpleNamespace(x=45, y=125))
    assert calls == [(7, 7), (3, 1)]


def test_45_on_canvas_click_outside_board_does_not_invoke_callback(board_view):
    """TEST-45: 盤面外クリック(_pixel_to_cellがNoneを返す座標)ではコールバックが呼ばれない。

    対応要件ID: REQ-04
    テスト対象(関数ID): FUNC-18
    """
    view, calls = board_view

    view._on_canvas_click(types.SimpleNamespace(x=BOARD_PIXEL_SIZE, y=BOARD_PIXEL_SIZE))
    view._on_canvas_click(types.SimpleNamespace(x=-1, y=-1))

    assert calls == []


# ---------------------------------------------------------------------------
# NFR-04: 描画処理の体感遅延なし
# ---------------------------------------------------------------------------

def test_46_many_draw_stone_calls_complete_without_noticeable_delay(board_view):
    """TEST-46: 盤面全マス相当(225回)のdraw_stone呼び出しが1秒未満で完了する。

    対応要件ID: NFR-04
    テスト対象(関数ID): FUNC-16
    """
    view, _calls = board_view

    start = time.perf_counter()
    for row in range(BOARD_CELLS):
        for col in range(BOARD_CELLS):
            color = "black" if (row + col) % 2 == 0 else "white"
            view.draw_stone(row, col, color)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0
