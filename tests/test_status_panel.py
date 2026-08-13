"""COMP-05（ステータス表示・操作パネル層 `StatusPanel`）の単体テスト。

対応テストモジュールID: TESTMOD-03
テスト仕様書: docs/04_test/test_specification.md（COMP-05節、5.0〜5.2）を参照。

本モジュールは、`src/status_panel.py` の `StatusPanel` を対象に、実際に `tkinter.Tk()` を
生成し（`root.withdraw()` で非表示化）、その配下に `StatusPanel` を構築したうえで、
生成されたウィジェット（`tk.Label` / `tk.Button`）の属性（`cget("text")` 等）を検証する
ホワイトボックステストを行う。`tk.Tk()` の生成・破棄は、プロジェクトルート直下の
`conftest.py` に scope="session" で定義された `tk_root` fixtureを
`tests/test_board_view.py` と共有する構成とする（複数のGUI関連テストモジュールをまとめて
実行した際の環境依存のTclライブラリ再読み込みエラーの散発を避けるため）。各テストごとに
新しい親フレーム（`tk.Frame`）と `StatusPanel` インスタンスを生成し、テスト終了後に
フレームを破棄することでテスト間の独立性を保つ。

各テスト関数のdocstring冒頭に対応するテストケースID（TEST-xx）を明記する。
"""

import time

import pytest
import tkinter as tk

from status_panel import StatusPanel


# ---------------------------------------------------------------------------
# fixture
# ---------------------------------------------------------------------------
#
# `tk_root`（非表示化した `tk.Tk()` ルートウィンドウ）は、プロジェクトルート直下の
# `conftest.py` に scope="session" で定義されたものを `tests/test_board_view.py` と
# テストセッション全体で共有する。本モジュールでは個別に定義しない。

@pytest.fixture
def restart_recorder():
    """`on_restart_click` コールバックの呼び出し回数を記録するための入れ物を返す。"""
    calls = []

    def on_restart():
        calls.append(None)

    return calls, on_restart


@pytest.fixture
def status_panel(tk_root, restart_recorder):
    """共有の `tk_root` 配下に新しい親フレームを生成し、その上に `StatusPanel` をテストごとに
    1つ生成する。テスト終了後にフレーム（配下のLabel・Buttonも含む）を破棄し、テスト間での
    ウィジェット・リソースのリークを防ぐ。
    """
    calls, on_restart = restart_recorder
    frame = tk.Frame(tk_root)
    panel = StatusPanel(frame, on_restart)
    yield panel, calls
    frame.destroy()


# ---------------------------------------------------------------------------
# FUNC-19: StatusPanel.__init__
# ---------------------------------------------------------------------------

def test_47_init_creates_label_and_restart_button(status_panel):
    """TEST-47: 初期化により、ステータス表示用Labelとリスタート用Button(text="リスタート")がparent配下に生成される。

    対応要件ID: REQ-10, REQ-11, REQ-12, REQ-13, CON-05
    テスト対象(関数ID): FUNC-19
    """
    panel, _calls = status_panel
    assert isinstance(panel._status_label, tk.Label)
    assert isinstance(panel._restart_button, tk.Button)
    assert panel._restart_button.cget("text") == "リスタート"


def test_48_init_sets_restart_button_command(status_panel):
    """TEST-48: 初期化時、Buttonのcommandに_on_restart_button_clickが設定される(commandが空でないことを確認)。

    対応要件ID: REQ-13, CON-05
    テスト対象(関数ID): FUNC-19
    """
    panel, _calls = status_panel
    command = panel._restart_button.cget("command")
    assert command != ""


# ---------------------------------------------------------------------------
# FUNC-20: StatusPanel.show_turn
# ---------------------------------------------------------------------------

def test_49_show_turn_black_displays_black_turn_text(status_panel):
    """TEST-49: show_turn('black')呼び出しでLabelに「黒の番です」が表示される。

    対応要件ID: REQ-12, CON-04
    テスト対象(関数ID): FUNC-20
    """
    panel, _calls = status_panel
    panel.show_turn("black")
    assert panel._status_label.cget("text") == "黒の番です"


def test_50_show_turn_white_displays_white_turn_text(status_panel):
    """TEST-50: show_turn('white')呼び出しでLabelに「白の番です」が表示される。

    対応要件ID: REQ-12, CON-04
    テスト対象(関数ID): FUNC-20
    """
    panel, _calls = status_panel
    panel.show_turn("white")
    assert panel._status_label.cget("text") == "白の番です"


# ---------------------------------------------------------------------------
# FUNC-21: StatusPanel.show_winner
# ---------------------------------------------------------------------------

def test_51_show_winner_black_displays_black_win_text(status_panel):
    """TEST-51: show_winner('black')呼び出しでLabelに「黒の勝ちです」が表示される。

    対応要件ID: REQ-10, CON-04
    テスト対象(関数ID): FUNC-21
    """
    panel, _calls = status_panel
    panel.show_winner("black")
    assert panel._status_label.cget("text") == "黒の勝ちです"


def test_52_show_winner_white_displays_white_win_text(status_panel):
    """TEST-52: show_winner('white')呼び出しでLabelに「白の勝ちです」が表示される。

    対応要件ID: REQ-10, CON-04
    テスト対象(関数ID): FUNC-21
    """
    panel, _calls = status_panel
    panel.show_winner("white")
    assert panel._status_label.cget("text") == "白の勝ちです"


# ---------------------------------------------------------------------------
# FUNC-22: StatusPanel.show_draw
# ---------------------------------------------------------------------------

def test_53_show_draw_displays_draw_text(status_panel):
    """TEST-53: show_draw()呼び出しでLabelに「引き分けです」が表示される。

    対応要件ID: REQ-11
    テスト対象(関数ID): FUNC-22
    """
    panel, _calls = status_panel
    panel.show_draw()
    assert panel._status_label.cget("text") == "引き分けです"


# ---------------------------------------------------------------------------
# FUNC-23: StatusPanel._on_restart_button_click
# ---------------------------------------------------------------------------

def test_54_restart_button_invoke_calls_on_restart_click_once(status_panel):
    """TEST-54: リスタートボタンをinvoke()すると、コンストラクタで渡したon_restart_clickコールバックが1回呼ばれる。

    対応要件ID: REQ-13
    テスト対象(関数ID): FUNC-23
    """
    panel, calls = status_panel
    panel._restart_button.invoke()
    assert len(calls) == 1


def test_55_restart_button_invoke_multiple_times_calls_callback_each_time(status_panel):
    """TEST-55: リスタートボタンを複数回invoke()すると、その都度on_restart_clickコールバックが呼ばれる(境界値)。

    対応要件ID: REQ-13
    テスト対象(関数ID): FUNC-23
    """
    panel, calls = status_panel
    panel._restart_button.invoke()
    panel._restart_button.invoke()
    panel._restart_button.invoke()
    assert len(calls) == 3


# ---------------------------------------------------------------------------
# FUNC-20〜FUNC-22: 表示の遷移
# ---------------------------------------------------------------------------

def test_56_display_transitions_reflect_latest_call(status_panel):
    """TEST-56: 手番表示→勝敗表示→引き分け表示→手番表示、と複数回呼び出した際に、常に最後の呼び出し内容がLabelに反映される(表示遷移の確認)。

    対応要件ID: REQ-10, REQ-11, REQ-12, REQ-13
    テスト対象(関数ID): FUNC-20, FUNC-21, FUNC-22
    """
    panel, _calls = status_panel

    panel.show_turn("black")
    assert panel._status_label.cget("text") == "黒の番です"

    panel.show_turn("white")
    assert panel._status_label.cget("text") == "白の番です"

    panel.show_winner("white")
    assert panel._status_label.cget("text") == "白の勝ちです"

    panel.show_draw()
    assert panel._status_label.cget("text") == "引き分けです"

    # リスタート後、COMP-03がshow_turn('black')を呼び出すことを想定した遷移
    panel.show_turn("black")
    assert panel._status_label.cget("text") == "黒の番です"


# ---------------------------------------------------------------------------
# NFR-04: 表示更新処理の体感遅延なし
# ---------------------------------------------------------------------------

def test_57_many_show_turn_calls_complete_without_noticeable_delay(status_panel):
    """TEST-57: 手番表示更新処理(show_turn)を盤面全マス相当(225回)呼び出しても体感遅延なく完了する(1秒未満)。

    対応要件ID: NFR-04
    テスト対象(関数ID): FUNC-20
    """
    panel, _calls = status_panel

    start = time.perf_counter()
    for i in range(225):
        color = "black" if i % 2 == 0 else "white"
        panel.show_turn(color)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0
