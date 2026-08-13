"""COMP-01（エントリーポイント `main()`）のテスト。

対応テストモジュールID: TESTMOD-05
テスト仕様書: docs/04_test/test_specification.md（COMP-01節、7.0〜7.2）を参照。

`main()` は `root.mainloop()` を呼び出すとtkinterのイベントループが開始され呼び出し元を
ブロックしてしまうため、そのままでは自動テストで実行できない。本モジュールでは、`main`
モジュール内で参照されている `tk`（`tkinter` モジュール）・`GameLogic`・`MainWindow` の
3つの名前を、それぞれ呼び出し内容（生成回数・引数・呼び出し順序）を記録するだけの軽量な
テスト用ダブルに `monkeypatch` で差し替えることで、実際のtkinterウィンドウ・イベントループを
一切起動せずに、`main()` が関数設計書FUNC-01の副作用仕様（「tk.Tkルートウィンドウを1つ生成し、
GameLogicのインスタンスを1つ生成し、両方を引数としてMainWindowのインスタンスを1つ生成し、
最後にroot.mainloop()を開始する」）どおりに、正しい順序・回数・引数でオブジェクトを
生成・呼び出していることを検証する。`MainWindow` 自身の内部動作は
`tests/test_main_window.py`（TESTMOD-04）で別途検証済みであり、本モジュールの関心は
COMP-01の起動処理の配線（orchestration）のみである。`GameLogic` はtkinterに依存しない
軽量なロジック層のクラス（NFR-05）であり、モックにする必要性が薄いため実際のクラスを
そのまま使用する。

CON-06（対応OSはWindowsのみ）・CON-07（Python 3.11環境上で動作）は、`main()` 自体が実行時に
OS・Pythonバージョンを判定するロジックを持たないため、「本テスト実行環境がCON-06・CON-07の
前提を満たしていること」を確認する環境確認テストとして設計する。これはテスト実行環境の
確認であり、実装が動的にOS・Pythonバージョンを検知・強制していることの証明ではない点に
留意する（7.2節参照）。

各テスト関数のdocstring冒頭に対応するテストケースID（TEST-xx）を明記する。
"""

import ast
import platform
import sys
import types

import pytest

import main as main_module
from game_logic import GameLogic


# ---------------------------------------------------------------------------
# テストダブル・ヘルパー
# ---------------------------------------------------------------------------

class _Recorder:
    """`main()` 内で行われる各処理の呼び出し記録を保持するテスト用の入れ物。

    - `order`: 呼び出された処理を発生順に `"tk"` → `"game_logic"` → `"main_window"` →
      `"mainloop"` の文字列で記録するリスト。
    - `tk_instances`: 生成された `tk.Tk` 代替インスタンスの一覧。
    - `game_logic_instances`: 生成された実際の `GameLogic` インスタンスの一覧。
    - `main_window_instances`: 生成された `MainWindow` 代替インスタンス（コンストラクタに
      渡された `root`・`game_logic` を `.root`・`.game_logic` として保持する）の一覧。
    """

    def __init__(self):
        self.order = []
        self.tk_instances = []
        self.game_logic_instances = []
        self.main_window_instances = []


def _make_tk_namespace(recorder):
    """`main` モジュールへ差し込む、`tkinter` モジュールの代わりとなる名前空間を作る。

    `.Tk` 属性に、実際のTclインタプリタを一切生成せず生成・`mainloop()` 呼び出しのみを
    記録する軽量なテスト用ダブルクラスを持たせる。
    """

    class _RecordingTk:
        def __init__(self):
            self.mainloop_call_count = 0
            recorder.order.append("tk")
            recorder.tk_instances.append(self)

        def mainloop(self):
            self.mainloop_call_count += 1
            recorder.order.append("mainloop")

    return types.SimpleNamespace(Tk=_RecordingTk)


def _make_game_logic_factory(recorder):
    """実際の `GameLogic` を生成しつつ、生成順序・生成されたインスタンスを記録する
    ファクトリ関数を返す。
    """

    def factory():
        recorder.order.append("game_logic")
        instance = GameLogic()
        recorder.game_logic_instances.append(instance)
        return instance

    return factory


def _make_main_window_factory(recorder):
    """`main` モジュールへ差し込む、`MainWindow` の代わりとなるテスト用ダブルクラスを作る。

    実際のGUIウィジェットは一切生成せず、コンストラクタに渡された `root`・`game_logic` を
    記録するのみ。
    """

    class _RecordingMainWindow:
        def __init__(self, root, game_logic):
            self.root = root
            self.game_logic = game_logic
            recorder.order.append("main_window")
            recorder.main_window_instances.append(self)

    return _RecordingMainWindow


@pytest.fixture
def recorder(monkeypatch):
    """`main` モジュール内の `tk`・`GameLogic`・`MainWindow` の3つの参照先を、呼び出し内容を
    記録するテスト用ダブルへ `monkeypatch` で差し替えるfixture。

    差し替え後に `main_module.main()` を呼び出せば、実際のtkinterウィンドウ・イベント
    ループを一切起動せずに、FUNC-01の副作用仕様どおりの生成・呼び出しが行われたかを
    戻り値の `_Recorder` の記録内容から検証できる。`monkeypatch` フィクスチャにより、
    差し替えはテスト関数終了時に自動的に元へ戻される。
    """
    rec = _Recorder()
    monkeypatch.setattr(main_module, "tk", _make_tk_namespace(rec))
    monkeypatch.setattr(main_module, "GameLogic", _make_game_logic_factory(rec))
    monkeypatch.setattr(main_module, "MainWindow", _make_main_window_factory(rec))
    return rec


# ---------------------------------------------------------------------------
# テストケース
# ---------------------------------------------------------------------------

def test_76_main_creates_tk_root_exactly_once(recorder):
    """TEST-76: main()呼び出しにより、tk.Tk相当のルートウィンドウが1回だけ生成される
    ことを確認する。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    main_module.main()
    assert len(recorder.tk_instances) == 1


def test_77_main_creates_game_logic_instance_exactly_once(recorder):
    """TEST-77: main()呼び出しにより、GameLogicのインスタンスが1回だけ生成され、それが
    実際のGameLogicインスタンスであることを確認する。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    main_module.main()
    assert len(recorder.game_logic_instances) == 1
    assert isinstance(recorder.game_logic_instances[0], GameLogic)


def test_78_main_creates_main_window_once_with_root_and_game_logic(recorder):
    """TEST-78: main()呼び出しにより、MainWindowが、生成されたtk.Tk相当のroot・
    GameLogicインスタンスの両方を(root, game_logic)の順序で引数として1回だけ生成される
    ことを確認する。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    main_module.main()
    assert len(recorder.main_window_instances) == 1
    mw = recorder.main_window_instances[0]
    assert mw.root is recorder.tk_instances[0]
    assert mw.game_logic is recorder.game_logic_instances[0]


def test_79_main_calls_root_mainloop_once(recorder):
    """TEST-79: main()呼び出しにより、生成されたrootのmainloop()が1回だけ呼ばれること
    を確認する。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    main_module.main()
    assert recorder.tk_instances[0].mainloop_call_count == 1


def test_80_main_executes_steps_in_correct_order(recorder):
    """TEST-80: main()内の各処理が「tk.Tk生成→GameLogic生成→MainWindow生成→mainloop
    開始」の順序で実行されることを確認する。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    main_module.main()
    assert recorder.order == ["tk", "game_logic", "main_window", "mainloop"]


def test_81_main_returns_none(recorder):
    """TEST-81: main()の戻り値がNoneであることを確認する（関数設計書FUNC-01の出力仕様）。

    対応要件ID: REQ-02
    テスト対象(関数ID): FUNC-01
    """
    result = main_module.main()
    assert result is None


def test_82_main_module_does_not_import_gui_frameworks_other_than_tkinter():
    """TEST-82: src/main.pyモジュールが、tkinter以外のGUIフレームワーク（PyQt、Kivy等）を
    importしていないことを確認する（CON-05）。tests/test_game_logic.pyのTEST-31と同様に、
    ソースをASTで解析してimport文を抽出する方法による。

    対応要件ID: CON-05
    テスト対象(関数ID): FUNC-01
    """
    with open(main_module.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=main_module.__file__)

    imported_top_level_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_top_level_names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_top_level_names.add(node.module.split(".")[0])

    disallowed_gui_frameworks = {
        "PyQt5", "PyQt6", "PySide2", "PySide6", "kivy", "wx", "pygame",
    }
    assert imported_top_level_names.isdisjoint(disallowed_gui_frameworks)
    assert "tkinter" in imported_top_level_names


def test_83_execution_environment_is_windows():
    """TEST-83: テスト実行環境のOSがWindowsであることを確認する環境確認テスト（CON-06）。
    本テストはあくまでテスト実行環境がCON-06の前提を満たしていることの確認であり、main()
    自体がOSを動的に判定・強制していることの証明ではない（テスト仕様書7.2節の限界に関する
    注記を参照）。

    対応要件ID: CON-06
    テスト対象(関数ID): FUNC-01
    """
    assert platform.system() == "Windows"


def test_84_execution_environment_is_python_311():
    """TEST-84: テスト実行環境がPython 3.11であることを確認する環境確認テスト（CON-07）。
    本テストはあくまでテスト実行環境がCON-07の前提を満たしていることの確認であり、main()
    自体がPythonバージョンを動的に判定・強制していることの証明ではない（テスト仕様書7.2節の
    限界に関する注記を参照）。

    対応要件ID: CON-07
    テスト対象(関数ID): FUNC-01
    """
    assert sys.version_info[:2] == (3, 11)
