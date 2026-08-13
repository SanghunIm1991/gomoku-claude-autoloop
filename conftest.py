"""pytest共通設定。

`tests/` から `src/` 配下のモジュール（例: `game_logic`）を直接importできるように、
プロジェクトルート直下の `src` ディレクトリを `sys.path` に追加する。

また、GUI関連のテストモジュール（`test_board_view.py`, `test_status_panel.py` 等）が共有する
`tk_root` fixture（scope="session"）をここで定義する。`tk.Tk()`（Tclインタプリタの生成）を
テストモジュールごとに個別に生成・破棄すると、同一プロセス内で `tk.Tk()` の生成→破棄→再生成が
繰り返されることになり、Windows環境ではTclのライブラリ探索用グローバル状態が壊れ、
`_tkinter.TclError: invalid command name "tcl_findLibrary"` が散発することを確認した
（Python/tkinter/実装コードの不具合ではなく、Tclインタプリタの生成・破棄回数に起因する
環境依存の問題）。この事象を避けるため、`tk.Tk()` の生成・破棄はテストセッション全体で1回のみとし、
各テストモジュール・各テスト関数で必要な子ウィジェット（Canvas・Frame等）はそれぞれのテスト
モジュール側の fixture でテスト関数単位に生成・破棄する。
"""

import os
import sys

import pytest
import tkinter as tk

_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


@pytest.fixture(scope="session")
def tk_root():
    """非表示化した `tk.Tk()` ルートウィンドウをテストセッション全体で1つだけ共有し、
    全テスト終了後に破棄する。

    `tk.Tk()` の生成・破棄をセッション全体で1回のみに抑えることで、複数のGUI関連テスト
    モジュールをまとめて実行した際のTclライブラリ再読み込みエラーの散発を避ける。
    """
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
