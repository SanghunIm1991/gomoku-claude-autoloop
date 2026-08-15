# Python初心者向け補足：このプロジェクトが暗黙の前提にしている知識

本書は `docs/01_requirements/` 〜 `docs/05_distribution/` の正式な成果物とは別に、
「コード・テスト・ビルド設定を読み進める際、説明なしに使われているPython/tkinter/pytestの
知識」を補うための資料である。読む順番は `src/main.py` → `src/game_logic.py` →
`src/board_view.py` → `src/main_window.py` / `src/status_panel.py` → `tests/` →
`conftest.py` → `Gomoku.spec` を想定しており、一度説明した事項は再掲しない。

---

## 1. `src/main.py` を読む前に

### 1.1 `py -3.11` と `python` の違い、`sys.path`
このPCには実体を持たない `python`（Microsoft Storeのスタブ）と、実体のある `py` ランチャーが
複数バージョン入っている（詳細は本プロジェクトの `CLAUDE.md` 「実装環境」章）。これはこのPC
固有の事情だが、一般的にも「`python`コマンドが常に使えるとは限らない」「複数バージョンが共存し
うる」という前提は初心者が驚きやすい点である。

### 1.2 仮想環境(venv)を使っていないこと
一般的なPythonプロジェクトでは `python -m venv` で仮想環境を作り、プロジェクトごとに依存
パッケージを分離するのが定石である。本プロジェクトはtkinter（標準ライブラリ）以外に依存
パッケージがなく、テストで使う`pytest`と配布で使う`PyInstorller`だけをAnaconda環境に直接
インストールしている（`docs/05_distribution/distribution_manual.md` 2.1節）。小規模で
標準ライブラリ中心のプロジェクトだからこそ許容される簡略化であり、依存パッケージが増える
プロジェクトではvenv（や`pip freeze`によるrequirements.txt管理）を検討すべき、という点は
どこにも明記されていない。

### 1.3 `import game_logic` がなぜそのまま通るのか（パッケージ構造を取っていない）
`src/` に `__init__.py` が存在しない。つまり `src` はPythonの「パッケージ」ではなく、
ただのディレクトリである。`main.py` を `py -3.11 src\main.py` のように**ファイルパス指定**で
実行すると、Pythonはそのファイルが置かれているディレクトリ（`src`）を自動的に
`sys.path`（importでモジュールを探す場所のリスト）の先頭に追加する。そのため
`main.py` 内の `from game_logic import GameLogic` は `src\game_logic.py` を素直に見つけられる。
これは「`src.game_logic` のようなパッケージパスで書かなくてよい理由」を暗黙に支えている
仕組みであり、`tests/` 側では同じことを `conftest.py` が明示的に行っている（6.1節）。

### 1.4 `if __name__ == "__main__":` の意味
`main.py` 末尾のこのイディオムは、「このファイルが直接実行されたときだけ `main()` を呼ぶ」
という定型句である。モジュールが他のファイルから `import` されたときには実行されない
（`__name__` にはimport元からはモジュール名が、直接実行時には `"__main__"` が入る）。

---

## 2. Python構文・命名の慣習（`game_logic.py` で初出）

### 2.1 型ヒント（`row: int`、`-> bool` など）
`def make_move(self, row: int, col: int) -> MoveResult:` のような記法は「型ヒント」と呼ばれ、
**実行時には一切チェックされない**（間違った型を渡してもエラーにならない）。あくまで人間や
IDE・型チェッカー（mypy等）向けの注釈であり、この記法自体がPythonの実行を変えるわけではない。
`Optional[str]` は「`str`型 または `None`」、`List[List[Optional[str]]]` は「要素が
`Optional[str]` のリストのリスト」を意味する。

### 2.2 `@dataclass` デコレータ
`MoveResult` / `RestartResult` に付いている `@dataclass` は、フィールドを列挙するだけで
`__init__`（コンストラクタ）・`__repr__`（表示用文字列）・`__eq__`（フィールドがすべて等しい
かどうかの比較）を自動生成するPython標準ライブラリの機能である。これにより
`MoveResult(valid=True, ...) == MoveResult(valid=True, ...)` のような比較がフィールド単位で
成立する（普通のクラスでは `==` はデフォルトでオブジェクトの同一性しか見ない）。テストコードの
`assert result == MoveResult(...)`（`tests/test_game_logic.py:110`）はこの自動生成された
`__eq__` に依存している。

### 2.3 先頭アンダースコアの命名規則（`_check_win` 等）
Pythonには他言語にあるような`private`修飾子は存在しない。`_check_win` や `_is_within_board` の
ように名前の先頭に`_`を付けるのは、「クラス外から直接呼ぶことを想定していない」という**慣習
上の合図**にすぎず、実際には外部から普通に呼び出せてしまう（テストコードが
`game._is_within_board(...)` を直接呼んでいるのはこのため）。

### 2.4 大文字の定数（`BOARD_SIZE`、`CELL_SIZE`）
`BOARD_SIZE = 15` のようにモジュールの先頭で大文字スネークケースの変数を定義するのは
「これは定数として扱ってほしい」という慣習（PEP 8）であり、言語的に変更を禁止する機能では
ない（`const`のような仕組みはPythonにはない）。

### 2.5 連結比較 `0 <= row <= BOARD_SIZE - 1`
`_is_within_board` の条件式は数学の不等式のように書けており、`0 <= row and row <= 14` と
同じ意味になる。多くの言語では書けない書き方である。

### 2.6 タプルによる多重代入・アンパック
`for d_row, d_col in _DIRECTIONS:` は、`_DIRECTIONS` の各要素（`(0, 1)` のようなタプル）を
その場で2つの変数に分解して受け取っている。`row, col = cell`（`board_view.py:93`）も同様に、
タプル `(row, col)` を2変数へ分解する代入である。

### 2.7 `None` を「石が置かれていない」の目印に使うこと
盤面は `Optional[str]` のリストで表現され、石が無いマスは文字列ではなく `None` で表す。
「空文字列 `""` ではなく `None` を『値が無いこと』の印にする」というのはPythonでは非常によく
使われる慣習だが、そう明記されているわけではない。

### 2.8 文字列を状態のラベルとして使うこと（Enumではなく）
`self.game_state` は `'in_progress'` / `'black_win'` / `'white_win'` / `'draw'` という
生の文字列で管理されている。より厳密にやるなら `enum.Enum` を使ってタイプミスをコード側で
防ぐ選択肢もあるが、本プロジェクトでは意図的にシンプルな文字列比較を採用している（設計書に
明記された選定理由はない）。

### 2.9 ネストしたリスト内包表記と「浅いコピーの罠」
`self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]`
（`game_logic.py:46-48`）は15行×15列の二次元リストを作っている。一見遠回りに見えるが、これは
`[[None] * BOARD_SIZE] * BOARD_SIZE` と書いてしまうとPython特有の罠にはまる、という背景を
暗黙に踏まえている。後者は「同じ1つの内側リストへの参照」を15個並べてしまうため、
どこか1マスを書き換えると別の行まで一緒に変わってしまう（内側リストが使い回されるため）。
このプロジェクトのコードは内包表記を2重にすることでこの罠を正しく回避しているが、その理由は
コメントに書かれていない。

---

## 3. tkinter（GUI）の基礎知識（`board_view.py` で初出）

### 3.1 ルートウィンドウとイベントループ
`tk.Tk()`（`main.py:10`）はGUIアプリの一番外側のウィンドウを作る。続く `root.mainloop()`
は「ユーザーの操作（クリック等）を待ち受け続けるループ」に入る呼び出しで、このループが終わる
までプログラムはこの行で待機し続ける（ウィンドウを閉じるまで`main()`の残りの行には進まない）。
GUIプログラムに特有の「イベント駆動」というパラダイムを支えている。

### 3.2 ウィジェットの親子関係と配置マネージャ（`.pack()`）
`tk.Canvas(parent, ...)` のように、tkinterのウィジェットは生成時に「どのウィジェットの中に
入るか」（`parent`）を指定する。生成しただけでは画面に表示されず、`.pack()` を呼んで初めて
実際に配置される。tkinterには`pack`の他に`grid`・`place`という配置方法もあるが、本プロジェクト
は一貫して`pack`（上から順に積む単純な配置）のみを使っており、その選定理由は設計書に書かれて
いない。

### 3.3 Canvasの座標系
`tk.Canvas` 上の座標は、画面のグラフィックス全般と同様に**左上が原点(0, 0)**で、
x は右方向、y は**下**方向に増える（数学のグラフのようにyが上に増えるわけではない）。
`board_view.py`の交点計算（`center_y = row * cell + cell // 2`）はこの前提の上に成り立っている。

### 3.4 イベントバインド `.bind("<Button-1>", handler)`
`"<Button-1>"` は「マウス左ボタンのクリック」を表すtkinter独自の文字列表記（イベントシーケンス）
である。`.bind()` はそのイベントが起きたときに呼ばれる関数（コールバック）を登録する仕組みで、
呼ばれる際にはtkinterが自動的に `tk.Event` オブジェクト（クリック位置などを持つ）を1つ渡して
くる。テストコード側が本物のクリックの代わりに
`types.SimpleNamespace(x=300, y=300)`（`tests/test_board_view.py:345`）という「`.x`と`.y`
属性さえ持っていれば十分」な軽量な代用オブジェクトを渡しているのは、この仕組みを踏まえた
テスト技法である。

### 3.5 ボタンの `command=` にはコールバック関数を渡す（呼び出さない）
`tk.Button(parent, text="リスタート", command=self._on_restart_button_click)`
（`status_panel.py:23-25`）のように、`command=`には関数**そのもの**（丸括弧を付けない状態）を
渡す。丸括弧を付けて`command=self._on_restart_button_click()`と書いてしまうと、ボタン生成の
その場で一度だけ関数が実行されてしまい、ボタンを押しても何も起きなくなる（初心者が非常に
陥りやすい誤り）。また `self._on_restart_button_click` のようにメソッドを`self`付きで参照する
ことで、後で呼ばれたときにも自動的に正しいインスタンス（`self`）に紐づいた状態で実行される
（「バウンドメソッド」と呼ばれる）。

### 3.6 整数の切り捨て除算 `//`
`_pixel_to_cell` の `row = y // self._cell_size` は、割り算の結果を小数点以下切り捨てで
整数にする演算子（負の数の場合は「0方向」ではなく「負の無限大方向」に切り捨てる点に注意）。
盤面外の負の座標や大きすぎる座標は、この演算だけでは弾けないため、続く範囲チェック
（`0 <= row <= BOARD_CELLS - 1`）と組み合わせて初めて安全になっている。

---

## 4. `main_window.py` / `status_panel.py`：設計パターンの暗黙知

### 4.1 コンストラクタでの「依存性の注入」
`MainWindow.__init__(self, root, game_logic)` は `GameLogic` のインスタンスを外から
受け取っている（自分で `GameLogic()` を作らない）。同様に `BoardView` や `StatusPanel` は
コールバック関数（`on_cell_click`、`on_restart_click`）を外から受け取る。これは
「依存性注入（Dependency Injection）」と呼ばれる設計パターンで、`CLAUDE.md`の品質方針
（ロジック層とGUI層の分離、テスト容易性）を実現する具体的な手段になっているが、このパターン名
自体はどの設計書にも明記されていない。テストコードが本物の`tkinter`ウィジェットの代わりに
ダミーの関数・オブジェクトを差し込めるのは、この仕組みのおかげである。

### 4.2 「呼び出し元に指示を仰ぐ」一方向の依存関係
`board_view.py`や`status_panel.py`のモジュールdocstringにある「対局のルール上の状態は保持
しない」という記述は、GUI部品（View）がロジック（Model）を一切知らず、逆に
`MainWindow`（Controller）だけが両方を知っているという一方向の依存関係を意味する。
一般的なMVC（Model-View-Controller）に近い構造だが、その呼称は使われていない。

---

## 5. `tests/` と `conftest.py`：pytest特有の暗黙知

### 5.1 テスト自動収集の命名規則
pytestは「`test_`で始まるファイル名」の中の「`test_`で始まる関数」を自動的にテストとして
見つけて実行する。`import`や登録の記述は一切不要で、ファイル名・関数名の**命名規則だけ**が
唯一の手がかりになっている。

### 5.2 `assert`文だけで検証できる理由
`unittest`（Python標準の別のテストフレームワーク）では`self.assertEqual(a, b)`のような
専用メソッドが必要だが、pytestでは素の`assert a == b`が使える。これはpytestが実行時に
`assert`文を書き換えて、失敗時に`a`と`b`それぞれの実際の値を詳しく表示する機能
（assertion rewriting）を持っているためであり、Python言語自体の`assert`にそこまでの機能は
ない。

### 5.3 `conftest.py` は自動的に読み込まれる特別なファイル名
`conftest.py`（プロジェクトルート直下）は、`import`されなくてもpytestが実行前に自動的に
読み込む特別な名前のファイルである。1.3節で触れた`sys.path`への`src`追加はここで行われており
（`conftest.py:23-25`）、各テストファイルが`from game_logic import ...`と書けるのはこの前処理
のおかげである。

### 5.4 `@pytest.fixture` と引数名によるインジェクション
`tk_root`という名前の関数に`@pytest.fixture`を付けると、テスト関数の**引数名を`tk_root`に
すること自体**が「このフィクスチャの戻り値がほしい」という意味になる
（`def test_32_...(board_view):` のように、明示的なimportや呼び出しをせずに使える）。
`yield`を使うフィクスチャ（`conftest.py`の`tk_root`、`test_board_view.py`の`board_view`）は
`yield`より前が前処理（セットアップ）、テスト関数の実行後に`yield`より後の部分が後処理
（ティアダウン、例:`root.destroy()`）として実行される。

### 5.5 `@pytest.mark.parametrize`
`@pytest.mark.parametrize("row,col", [(0, 0), (14, 14), ...])`
（`tests/test_game_logic.py:78`）は、1つのテスト関数の中身を変えずに、複数の入力値の組で
繰り返し実行させる仕組みである。実行結果には`test_02_..._true_on_boundaries[0-0]`のように
各パラメータの値が自動的にテストIDへ付加される。

### 5.6 セッション全体で`tk.Tk()`を使い回している理由
`conftest.py`のdocstringに書かれている通り、`tk.Tk()`（Tclインタプリタ）をテストごとに
何度も生成・破棄するとWindows環境で内部エラーが散発したという実地の知見に基づき、
`scope="session"`（テスト全体で1回だけ生成）を選んでいる。これはtkinter/Tclという特定の
GUIライブラリの実装都合による対処であり、一般的なpytestの作法として常にこうすべき、
というわけではない。

### 5.7 `ast`モジュールによる「importの静的解析」テスト
`test_31_game_logic_module_does_not_depend_on_tkinter`
（`tests/test_game_logic.py:538`）は、ソースコードの文字列を`ast.parse`でPythonの構文木
（AST）に変換し、`ast.Import`/`ast.ImportFrom`ノードだけを取り出してimport文を検査している。
単純な文字列検索（`"tkinter" in source`）ではdocstring中の説明文にも誤反応してしまうため、
あえて構文解析まで踏み込んだテスト技法が使われている。初心者にはやや高度な部類の手法である。

### 5.8 `time.perf_counter()`による簡易ベンチマーク
`test_30`・`test_46`が使う`time.perf_counter()`は、経過時間の計測に使うPython標準の関数
（`time.time()`より精度が高く、ベンチマーク用途に適している）。ここでの`elapsed < 1.0`という
しきい値は、正確な性能測定ではなく「体感遅延がない」ことの目安確認と位置づけられている
（テストのdocstringに明記あり）。

---

## 6. 配布（`Gomoku.spec`・PyInstaller）の暗黙知

### 6.1 「配布物の実行にPythonのインストールは不要」の意味
PyInstallerは、Pythonのインタプリタ本体・使用している標準ライブラリ・依存DLLをまとめて1つの
実行ファイル（`Gomoku.exe`）に固める。配布マニュアルにある「配布先にPython自体をインストール
する必要がない」というのはこの仕組みを指しており、`Gomoku.spec`はその固め方（何を含め、何を
除外するか）を指定する設定ファイルである。

### 6.2 tkinterがなぜ「隠れた依存」を持つのか
`tkinter`はPythonのコードとしては標準ライブラリだが、実体は`Tcl/Tk`という**Cで書かれた別の
ソフトウェア**へのラッパーであり、`tcl86t.dll`・`tk86t.dll`のようなネイティブDLLに依存して
いる。これは通常のPythonパッケージ（`.py`ファイルの集まり）とは異なる依存の種類であり、
`CLAUDE.md`の「環境メモ」章にある「PATHが通っていないとPyInstallerがこれらのDLLを同梱できず、
ビルド自体は成功するのに生成物の実行時にだけ`ImportError`になる」という事象は、この
「Pythonコードの依存」と「ネイティブライブラリの依存」の違いを暗黙の前提にしている。

### 6.3 `.spec`ファイルはPythonコードそのもの
`Gomoku.spec`は設定ファイルに見えるが、実体は`Analysis`・`PYZ`・`EXE`という専用オブジェクトを
生成するPythonスクリプトであり、`PyInstaller`コマンドがこれをそのまま実行することでビルドを
行う（JSON/YAMLのような静的な設定形式ではない）。
