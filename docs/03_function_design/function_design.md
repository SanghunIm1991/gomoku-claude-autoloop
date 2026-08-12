# 関数設計書（15×15五目並べ）

## 0. 本書の位置づけ

本書は `docs/01_requirements/requirements.md`（要件定義書、確定済み）および `docs/02_component_design/component_design.md`（コンポーネント設計書、確定済み。COMP-01〜05）を受けた関数設計（詳細設計）工程の成果物である。各コンポーネントが実装すべき具体的な関数・メソッドについて、シグネチャ（引数・戻り値の型）、副作用の有無、対応要件ID・コンポーネントIDを定義する。

ID採番方針: 関数IDは `FUNC-01`, `FUNC-02`, ... の形式で、コンポーネントID順（COMP-01→02→03→04→05）に本書内で一意に採番する。

CLAUDE.mdの品質方針（テスト容易性）に従い、特にCOMP-02（ロジック層）の各関数は、入力と出力（戻り値）が明確な単位に分割し、自身のインスタンス状態の変更以外の副作用を持たない設計とする。COMP-03/04/05（GUI層）の関数はtkinterウィジェット操作を伴ってよい。

## 1. モジュール構成（想定ファイル）

実装工程（`src/`）での想定ファイル構成を以下に示す（ファイル名は実装工程で変更してよいが、本書ではこれを前提に関数を設計する）。

| コンポーネントID | 想定ファイル | 想定クラス/関数 |
|---|---|---|
| COMP-01 | `src/main.py` | `main()`（モジュールレベル関数） |
| COMP-02 | `src/game_logic.py` | `class GameLogic` |
| COMP-03 | `src/main_window.py` | `class MainWindow` |
| COMP-04 | `src/board_view.py` | `class BoardView` |
| COMP-05 | `src/status_panel.py` | `class StatusPanel` |

## 2. 共通データ型・共通仕様

関数シグネチャの記述を簡潔にするため、以下の共通の型・値の表現を定義する。実装時はこれらを `dataclass`（標準ライブラリ `dataclasses`）または同等の型ヒントで表現することを想定する。

### 2.1 色・状態の値の表現

- **色（color）**: `str` 型。`'black'`（黒）または `'white'`（白）のいずれか。
- **盤面のマス状態**: `None`（空）／ `'black'`（黒石）／ `'white'`（白石）のいずれか。
- **対局状態**: `'in_progress'`（対局中）／ `'black_win'`（黒勝利）／ `'white_win'`（白勝利）／ `'draw'`（引き分け）のいずれか。
- **座標**: `row`, `col` はいずれも `int` 型。盤面サイズが15×15（CON-02）であるため、有効範囲は `0 <= row <= 14`, `0 <= col <= 14`。

### 2.2 `MoveResult`（着手処理の戻り値、COMP-02が定義）

| フィールド | 型 | 意味 |
|---|---|---|
| `valid` | `bool` | 着手が有効であったか。無効（既着手マス、または対局終了後）の場合 `False`。 |
| `color` | `Optional[str]` | 配置された石の色。`valid=False` の場合は `None`。 |
| `winner` | `Optional[str]` | この着手により勝敗が確定した場合、勝利した色。未確定または `valid=False` の場合は `None`。 |
| `is_draw` | `bool` | この着手により引き分けが確定したか。`valid=False` の場合は `False`。 |
| `next_turn` | `Optional[str]` | 次の手番の色。勝敗確定・引き分け確定・`valid=False` のいずれかの場合は `None`（＝手番を切り替えないことを戻り値のみで判別可能にする）。 |
| `game_over` | `bool` | この着手の結果、対局が終了した（`winner` が確定 または `is_draw=True`）か。`valid=False` の場合は `False`。 |

### 2.3 `RestartResult`（リスタート処理の戻り値、COMP-02が定義）

| フィールド | 型 | 意味 |
|---|---|---|
| `success` | `bool` | リスタート処理が完了したか。リスタート処理は入力を取らず失敗しうる分岐が存在しないため、常に `True`。 |
| `next_turn` | `str` | リセット後の手番。常に `'black'`。 |

## 3. 関数一覧

| 関数ID | 所属コンポーネント | 関数名 | 概要 |
|---|---|---|---|
| FUNC-01 | COMP-01 | `main()` | アプリケーション起動処理 |
| FUNC-02 | COMP-02 | `GameLogic.__init__(self)` | ゲームロジックの初期化（コンストラクタ） |
| FUNC-03 | COMP-02 | `GameLogic.restart(self)` | リスタート処理 |
| FUNC-04 | COMP-02 | `GameLogic._reset_state(self)` | 盤面初期化（内部ヘルパー） |
| FUNC-05 | COMP-02 | `GameLogic.make_move(self, row, col)` | 着手処理 |
| FUNC-06 | COMP-02 | `GameLogic._is_within_board(self, row, col)` | 座標が盤面範囲内か判定（内部ヘルパー） |
| FUNC-07 | COMP-02 | `GameLogic._check_win(self, row, col, color)` | 勝敗判定（内部ヘルパー） |
| FUNC-08 | COMP-02 | `GameLogic._count_consecutive(self, row, col, color, d_row, d_col)` | 指定方向への連続石数カウント（内部ヘルパー） |
| FUNC-09 | COMP-02 | `GameLogic._is_board_full(self)` | 引き分け判定用の盤面充填チェック（内部ヘルパー） |
| FUNC-10 | COMP-03 | `MainWindow.__init__(self, root, game_logic)` | メインウィンドウの初期化（コンストラクタ） |
| FUNC-11 | COMP-03 | `MainWindow._show_initial_state(self)` | 起動直後の初期表示（内部ヘルパー） |
| FUNC-12 | COMP-03 | `MainWindow.on_board_click(self, row, col)` | 盤面クリック通知の受信・着手依頼・表示更新指示 |
| FUNC-13 | COMP-03 | `MainWindow.on_restart_click(self)` | リスタート通知の受信・リスタート依頼・表示初期化指示 |
| FUNC-14 | COMP-04 | `BoardView.__init__(self, parent, on_cell_click)` | 盤面表示の初期化（コンストラクタ） |
| FUNC-15 | COMP-04 | `BoardView.draw_empty_board(self)` | 盤面描画（格子線のみのクリア再描画） |
| FUNC-16 | COMP-04 | `BoardView.draw_stone(self, row, col, color)` | 石の描画 |
| FUNC-17 | COMP-04 | `BoardView._pixel_to_cell(self, x, y)` | ピクセル座標→行列インデックス変換（内部ヘルパー） |
| FUNC-18 | COMP-04 | `BoardView._on_canvas_click(self, event)` | 盤面クリックイベントハンドラ |
| FUNC-19 | COMP-05 | `StatusPanel.__init__(self, parent, on_restart_click)` | ステータス表示・操作パネルの初期化（コンストラクタ） |
| FUNC-20 | COMP-05 | `StatusPanel.show_turn(self, color)` | 手番表示への更新 |
| FUNC-21 | COMP-05 | `StatusPanel.show_winner(self, color)` | 勝敗表示への更新 |
| FUNC-22 | COMP-05 | `StatusPanel.show_draw(self)` | 引き分け表示への更新 |
| FUNC-23 | COMP-05 | `StatusPanel._on_restart_button_click(self)` | リスタートボタンのイベントハンドラ |

コンポーネントごとの関数数: COMP-01=1（FUNC-01）／COMP-02=8（FUNC-02〜09）／COMP-03=4（FUNC-10〜13）／COMP-04=5（FUNC-14〜18）／COMP-05=5（FUNC-19〜23）。全23関数。全コンポーネント（COMP-01〜05）が最低1つの関数に対応している。

## 4. 各関数の詳細

### 4.1 COMP-01: エントリーポイント

#### FUNC-01: `main()`

- **所属コンポーネント**: COMP-01
- **入力**: なし（コマンドライン引数を取らない）
- **出力**: なし（戻り値 `None`）
- **副作用**: あり。tkinterのルートウィンドウ（`tk.Tk`）を1つ生成し、`GameLogic`（COMP-02, FUNC-02）のインスタンスを1つ生成し、生成した `tk.Tk` のルートウィンドウと生成した `GameLogic` インスタンスの両方を引数として `MainWindow`（COMP-03, FUNC-10）のインスタンスを1つ生成する。最後にtkinterのイベントループ（`root.mainloop()`）を開始し、ウィンドウが閉じられるまで処理をブロックする。
- **境界値・異常系**: 本関数は起動処理であり外部からの入力を受け取らないため、入力バリデーションの対象外とする。tkinter初期化に失敗した場合（例: ディスプレイ利用不可等の実行環境起因のエラー）は、本関数内で例外を捕捉せずそのまま送出させる（起動失敗として扱う）。
- **対応要件ID・コンポーネントID**: REQ-02, CON-05, CON-06, CON-07 ／ COMP-01

### 4.2 COMP-02: ゲームロジック（`GameLogic`）

NFR-05（ロジック層の外部ライブラリ非依存・単体テスト可能性）はCOMP-02の全関数に共通する性質であり、個別の関数には付与せずFUNC-05（唯一の状態変更を伴う複合処理でNFR-04の応答性能要件が直接関わる関数）にのみ代表して付与している。

#### FUNC-02: `GameLogic.__init__(self)`

- **所属コンポーネント**: COMP-02
- **入力**: `self` のみ（追加引数なし）
- **出力**: なし（コンストラクタ、戻り値 `None`）
- **副作用**: あり（ただしCOMP-02に許容される範囲）。自身のインスタンス変数（盤面・手番・対局状態）を初期化する。tkinter等の外部ライブラリへのアクセス、ファイルI/O等の外部副作用は一切行わない。
- **処理内容**: 内部で FUNC-04 `_reset_state()` を呼び出し、盤面を15×15マスすべて空(`None`)、手番を `'black'`、対局状態を `'in_progress'` に設定する。
- **境界値・異常系**: 引数を取らないため入力バリデーションの対象外。
- **対応要件ID・コンポーネントID**: REQ-01, REQ-02, CON-02, CON-04 ／ COMP-02

#### FUNC-03: `GameLogic.restart(self) -> RestartResult`

- **所属コンポーネント**: COMP-02
- **入力**: `self` のみ
- **出力**: `RestartResult`。常に `success=True`, `next_turn='black'` を返す。
- **副作用**: あり（自身のインスタンス状態変更のみ）。盤面・手番・対局状態を初期状態（全マス空／黒番／`'in_progress'`）にリセットする。
- **処理内容**: 内部で FUNC-04 `_reset_state()` を呼び出す。
- **境界値・異常系**: 対局中・黒勝利確定後・白勝利確定後・引き分け確定後のいずれの状態から呼び出しても、結果は常に同一（`success=True`, `next_turn='black'`、かつ内部状態が全マス空・黒番・対局中になる）。テストではこの4パターンすべてで同一の結果になることを確認する。
- **対応要件ID・コンポーネントID**: REQ-13 ／ COMP-02

#### FUNC-04: `GameLogic._reset_state(self) -> None`

- **所属コンポーネント**: COMP-02（内部ヘルパー、外部コンポーネントから直接呼び出されない）
- **入力**: `self` のみ
- **出力**: なし
- **副作用**: あり（自身のインスタンス状態変更のみ）。盤面（15×15の内部データ構造、各マス `None`）、手番（`'black'`）、対局状態（`'in_progress'`）を設定する。
- **境界値・異常系**: なし（引数を取らない）。
- **対応要件ID・コンポーネントID**: REQ-01, REQ-02, REQ-13, CON-02, CON-04 ／ COMP-02

#### FUNC-05: `GameLogic.make_move(self, row: int, col: int) -> MoveResult`

- **所属コンポーネント**: COMP-02
- **入力**: `row: int`（行インデックス、想定範囲0〜14）, `col: int`（列インデックス、想定範囲0〜14）
- **出力**: `MoveResult`（2.2節参照）
- **正常系の処理内容**:
  1. 対局状態が `'in_progress'` かつ `(row, col)` が盤面範囲内（FUNC-06）かつ当該マスが空である場合のみ有効な着手として扱う。
  2. 現在の手番の色を `(row, col)` に配置する。`valid=True`, `color=` 配置した色。
  3. 配置直後、FUNC-07 `_check_win(row, col, 配置した色)` で勝敗判定を行う。
     - 勝利確定の場合: `winner=` 勝利色, `game_over=True`, `is_draw=False`, `next_turn=None`。対局状態を `'black_win'` または `'white_win'` に更新する。手番は切り替えない。
     - 勝利未確定の場合、続けて FUNC-09 `_is_board_full()` で引き分け判定を行う。
       - 引き分け確定の場合: `winner=None`, `is_draw=True`, `game_over=True`, `next_turn=None`。対局状態を `'draw'` に更新する。手番は切り替えない。
       - 引き分けでない場合: `winner=None`, `is_draw=False`, `game_over=False`, `next_turn=` 切り替え後の色。手番を切り替える（黒→白／白→黒）。
  - **境界値**: `row`・`col` が盤面端（0または14）であっても正常に配置できることを確認する。
- **異常系の処理内容（いずれも盤面状態・手番・対局状態を一切変更しない）**:
  - 既に石が置かれているマスが指定された場合: `valid=False`, `color=None`, `winner=None`, `is_draw=False`, `next_turn=None`, `game_over=False`。
  - 対局状態が `'in_progress'` でない（勝敗確定後または引き分け確定後）場合: 指定マスが空であっても `valid=False` とし、上記と同じ値を返す。
  - `row` または `col` が盤面範囲外（0未満または14超）の場合: FUNC-06 `_is_within_board` により範囲外と判定し、`valid=False` として扱う（例外は送出しない）。他フィールドは上記と同じ。
  - `row`・`col` に `int` 以外の型（`float`, `str`, `None` 等）が渡された場合: 呼び出し元（COMP-03、ひいてはCOMP-04の座標変換処理）が常に `int` 型を渡すことが呼び出し契約として保証されているため、本関数内での型チェック・例外送出は行わない（未定義動作とする）。単体テストでは正常系および盤面範囲外（`int` 型だが0〜14外）の異常系を必須の検証対象とし、型不正の入力についてはテスト対象としなくてよい。
- **副作用**: 有効な着手の場合、自身のインスタンス状態（盤面・手番・対局状態）を変更する。無効な着手の場合、状態を一切変更しない。GUI描画等の外部副作用は持たない。
- **対応要件ID・コンポーネントID**: REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, CON-01, CON-04, NFR-04, NFR-05 ／ COMP-02

#### FUNC-06: `GameLogic._is_within_board(self, row: int, col: int) -> bool`

- **所属コンポーネント**: COMP-02（内部ヘルパー）
- **入力**: `row: int`, `col: int`
- **出力**: `bool`。`0 <= row <= 14` かつ `0 <= col <= 14` の場合 `True`、それ以外は `False`。
- **副作用**: なし（純粋関数、盤面等の状態を参照・変更しない）。
- **境界値**: `row=0`・`row=14`・`col=0`・`col=14` はいずれも `True`。`row=-1`・`row=15`・`col=-1`・`col=15` はいずれも `False`。
- **対応要件ID・コンポーネントID**: REQ-01, CON-02 ／ COMP-02

#### FUNC-07: `GameLogic._check_win(self, row: int, col: int, color: str) -> bool`

- **所属コンポーネント**: COMP-02（内部ヘルパー）
- **入力**: `row: int`, `col: int`（直前に石を置いたマスの座標）, `color: str`（判定対象の色、`'black'` または `'white'`）
- **出力**: `bool`。`(row, col)` を含む縦・横・斜め（右下がり・右上がり）の4方向のいずれかで `color` の石が5個以上連続している場合 `True`、いずれの方向も5個未満なら `False`。
- **処理内容**: 4方向（横: `(0,1)`、縦: `(1,0)`、斜め右下がり: `(1,1)`、斜め右上がり: `(1,-1)`）それぞれについて、FUNC-08 `_count_consecutive` をその方向の正方向・逆方向（`(d_row,d_col)` とその符号反転）で呼び出し、「`(row,col)` 自身の1個 + 正方向の連続数 + 逆方向の連続数」の合計を求める。いずれかの方向で合計が5以上であれば直ちに `True` を返す。
- **副作用**: なし（盤面を読み取るのみで変更しない）。
- **境界値・異常系**: ちょうど5個連続で `True`。4個連続（両端が空または盤面端で止まる）で `False`。6個以上の連続でも `True`（要件どおり、5個ちょうどに限定しない）。盤面端付近で連続石が盤面外まで伸びようとする状況でも、FUNC-08が範囲外到達時に正しくカウントを打ち切るため、境界を越えた誤判定は発生しない。
- **対応要件ID・コンポーネントID**: REQ-08 ／ COMP-02

#### FUNC-08: `GameLogic._count_consecutive(self, row: int, col: int, color: str, d_row: int, d_col: int) -> int`

- **所属コンポーネント**: COMP-02（内部ヘルパー）
- **入力**: `row: int`, `col: int`（起点座標。この座標自体はカウントに含めない）, `color: str`, `d_row: int`（-1/0/1のいずれか）, `d_col: int`（-1/0/1のいずれか）。ただし `(d_row, d_col)=(0, 0)` は呼び出し元（FUNC-07）から渡されない前提とする。
- **出力**: `int`（0以上）。`(row+d_row, col+d_col)` から `(d_row, d_col)` 方向へ、盤面範囲内かつ `color` と同じ色の石が連続する個数。
- **処理内容**: `(row+d_row, col+d_col)` から順に座標を `(d_row, d_col)` ずつ進めながら、FUNC-06 `_is_within_board` を呼び出して範囲チェックを行い、範囲内かつマスの色が `color` と一致する限りカウントを1ずつ増やす。盤面外に出た、またはマスが空もしくは異なる色であった時点で処理を停止し、その時点までのカウントを返す。
- **副作用**: なし（純粋関数）。
- **境界値・異常系**: 起点の隣接マスが盤面外・空・異色のいずれかであれば `0` を返す。盤面端に到達したら範囲外アクセスを行わずカウントを打ち切る。
- **対応要件ID・コンポーネントID**: REQ-08 ／ COMP-02

#### FUNC-09: `GameLogic._is_board_full(self) -> bool`

- **所属コンポーネント**: COMP-02（内部ヘルパー）
- **入力**: `self` のみ
- **出力**: `bool`。225マスすべてが空でない（いずれかの色の石で埋まっている）場合 `True`、1マスでも空があれば `False`。
- **副作用**: なし。
- **境界値**: 224マス埋まり1マスのみ空の場合 `False`。225マスすべて埋まっている場合 `True`。全マス空（初期状態）の場合 `False`。
- **対応要件ID・コンポーネントID**: REQ-09 ／ COMP-02

### 4.3 COMP-03: メインウィンドウ（GUIコントローラ、`MainWindow`）

#### FUNC-10: `MainWindow.__init__(self, root: tk.Tk, game_logic: GameLogic) -> None`

- **所属コンポーネント**: COMP-03
- **入力**: `root: tk.Tk`（COMP-01が生成したルートウィンドウ）, `game_logic: GameLogic`（COMP-01が生成したCOMP-02のインスタンス）
- **出力**: なし（コンストラクタ）
- **副作用**: あり。`root` 配下に `BoardView`（COMP-04, FUNC-14）と `StatusPanel`（COMP-05, FUNC-19）のインスタンスをそれぞれ生成しウィジェットとして配置する。`BoardView`・`StatusPanel` 生成時に渡す `parent` 引数は、いずれも本関数が受け取った `root` をそのまま渡す（`BoardView.__init__`・`StatusPanel.__init__` の `parent` 引数の型注釈は `tk.Widget` だが、型注釈上は`tk.Widget`と`tk.Tk`は別クラスであるものの、tkinterの実装上`Tk`は`Widget`と共通のメソッド（`Misc`由来）を持つため実行時には問題なく動作する。実体は `root` である）。生成した `BoardView` インスタンスは `self.board_view` として、`StatusPanel` インスタンスは `self.status_panel` として、それぞれインスタンス変数に保持する。`BoardView` 生成時には `self.on_board_click`（FUNC-12）を、`StatusPanel` 生成時には `self.on_restart_click`（FUNC-13）をコールバックとして渡す。`self.game_logic` として `game_logic` の参照を保持する。生成完了後、FUNC-11 `_show_initial_state()` を呼び出す。
- **境界値・異常系**: `root`・`game_logic` は常にCOMP-01から正しい型で渡されることが前提であり、本関数内での型チェックは行わない。
- **対応要件ID・コンポーネントID**: REQ-02, CON-05 ／ COMP-03

#### FUNC-11: `MainWindow._show_initial_state(self) -> None`

- **所属コンポーネント**: COMP-03（内部ヘルパー）
- **入力**: `self` のみ
- **出力**: なし
- **副作用**: あり。COMP-02への問い合わせを一切行わず（COMP-01が生成した直後の `GameLogic` は必ず「全マス空・黒番・対局中」の初期状態であることが設計上保証されているため）、`BoardView.draw_empty_board()`（FUNC-15）と `StatusPanel.show_turn('black')`（FUNC-20）を直接呼び出し、空の盤面と黒番の手番表示を指示する。
- **対応要件ID・コンポーネントID**: REQ-02, REQ-12 ／ COMP-03

#### FUNC-12: `MainWindow.on_board_click(self, row: int, col: int) -> None`

- **所属コンポーネント**: COMP-03
- **入力**: `row: int`, `col: int`（COMP-04から通知される、クリックされたマスの行・列インデックス。0〜14の範囲であることはCOMP-04側のFUNC-17で保証済み）
- **出力**: なし
- **処理内容**: `self.game_logic.make_move(row, col)`（FUNC-05）を呼び出し、戻り値の `MoveResult` に応じて以下のように分岐する。
  - `valid=False` の場合: `BoardView`・`StatusPanel` のいずれにも更新指示を行わない（表示状態を一切変化させない）。
  - `valid=True` の場合:
    1. `BoardView.draw_stone(row, col, result.color)`（FUNC-16）を呼び出し、石を描画する。
    2. `result.game_over=True` かつ `result.winner is not None` の場合: `StatusPanel.show_winner(result.winner)`（FUNC-21）を呼び出す。
    3. `result.game_over=True` かつ `result.is_draw=True` の場合: `StatusPanel.show_draw()`（FUNC-22）を呼び出す。
    4. `result.game_over=False` の場合: `StatusPanel.show_turn(result.next_turn)`（FUNC-20）を呼び出す。
- **副作用**: あり。COMP-02の状態を変更する呼び出しを行い、その結果に応じてCOMP-04・COMP-05へ描画・表示更新を指示する。
- **境界値・異常系**: 本関数への入力自体は常に盤面範囲内であることがFUNC-17により保証されるため、盤面範囲外の入力に対するテストは本関数（FUNC-12）ではなくFUNC-05（`GameLogic.make_move`）の単体テストで検証する。FUNC-12では `MoveResult.valid=False` となる残りのケース（既着手マス、対局終了後）で表示更新を行わないことを確認する。
- **対応要件ID・コンポーネントID**: REQ-04, REQ-05, REQ-06, REQ-07, REQ-10, REQ-11, REQ-12, NFR-04, NFR-05, CON-03 ／ COMP-03

#### FUNC-13: `MainWindow.on_restart_click(self) -> None`

- **所属コンポーネント**: COMP-03
- **入力**: なし（`self` のみ）
- **出力**: なし
- **処理内容**: `self.game_logic.restart()`（FUNC-03）を呼び出し、その戻り値 `RestartResult` をもとに `BoardView.draw_empty_board()`（FUNC-15）と `StatusPanel.show_turn(result.next_turn)`（FUNC-20、常に `'black'`）を呼び出し、表示を初期状態に戻す。
- **副作用**: あり。COMP-02の状態をリセットし、COMP-04・COMP-05へ表示初期化を指示する。
- **境界値・異常系**: 対局中・勝敗確定後・引き分け確定後のいずれの表示状態から呼び出されても、同一の初期表示（空の盤面・黒番表示）になることを確認する。
- **対応要件ID・コンポーネントID**: REQ-13, NFR-05 ／ COMP-03

### 4.4 COMP-04: 盤面表示（`BoardView`）

#### FUNC-14: `BoardView.__init__(self, parent: tk.Widget, on_cell_click: Callable[[int, int], None]) -> None`

- **所属コンポーネント**: COMP-04
- **入力**: `parent: tk.Widget`（配置先の親ウィジェット、COMP-03が生成したウィンドウ配下）, `on_cell_click: Callable[[int, int], None]`（クリック時に呼び出すコールバック。実体はCOMP-03の `on_board_click`）
- **出力**: なし
- **副作用**: あり。`parent` 配下にtkinterの `Canvas` ウィジェットを生成し配置する。`Canvas` の `<Button-1>` イベントをFUNC-18 `_on_canvas_click` にバインドする。`on_cell_click` を自身のインスタンス変数として保持する。あわせて、盤面描画に必要な表示用パラメータ（マス目の1辺のピクセルサイズ等。盤面はCanvas原点 `(0, 0)` から余白なく描画される前提で算出する）を算出し、インスタンス変数として保持する（FUNC-17 `_pixel_to_cell` が参照する）。生成直後にFUNC-15 `draw_empty_board()` を呼び出し、初期の格子線を描画する。
- **対応要件ID・コンポーネントID**: REQ-01, REQ-02, CON-02, CON-05 ／ COMP-04

#### FUNC-15: `BoardView.draw_empty_board(self) -> None`

- **所属コンポーネント**: COMP-04
- **入力**: `self` のみ
- **出力**: なし
- **副作用**: あり。`Canvas` 上の描画内容をすべて消去し、15×15マス分の格子線のみを再描画する（石は一切描画しない）。
- **対応要件ID・コンポーネントID**: REQ-01, REQ-02, REQ-13, CON-02 ／ COMP-04

#### FUNC-16: `BoardView.draw_stone(self, row: int, col: int, color: str) -> None`

- **所属コンポーネント**: COMP-04
- **入力**: `row: int`（0〜14）, `col: int`（0〜14）, `color: str`（`'black'` または `'white'`）
- **出力**: なし
- **副作用**: あり。指定マスの中心付近に、指定色で塗りつぶした円（石）を `Canvas` 上に描画する。
- **境界値・異常系**: `row`・`col` は常にCOMP-03経由でCOMP-02が有効性を検証済みの値のみが渡される呼び出し契約であるため、本関数内での範囲チェックは行わない。
- **対応要件ID・コンポーネントID**: REQ-04, CON-04, NFR-04 ／ COMP-04

#### FUNC-17: `BoardView._pixel_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]`

- **所属コンポーネント**: COMP-04（内部ヘルパー）
- **入力**: `x: int`, `y: int`（`Canvas` 上のクリック位置のピクセル座標）
- **出力**: `Optional[Tuple[int, int]]`。盤面の描画範囲内であれば対応する `(row, col)` を返す。本書の前提として、盤面はCanvas原点 `(0, 0)` から余白なく描画される（COMP-04の描画領域は盤面そのものであり、周囲に固定の余白は設けない）。この前提のもと、座標が盤面の描画範囲外（負の値、または盤面の描画領域サイズ以上）である場合は `None` を返す。
- **処理内容**: `row = y // マス目の1辺のピクセルサイズ`、`col = x // マス目の1辺のピクセルサイズ` により算出する（FUNC-14で保持したマス目のピクセルサイズを用いる）。算出した `(row, col)` が盤面範囲内（`0 <= row <= 14` かつ `0 <= col <= 14`）であればそれを返し、範囲外であれば `None` を返す。
- **副作用**: なし。自身が保持する表示用パラメータ（マス目のピクセルサイズ等）を参照するのみで、状態変更やウィジェット操作は行わない。
- **境界値・異常系**: 各マスの境界線ちょうどをクリックした場合は、マス目のピクセルサイズによる整数除算で一意に決定する（切り捨てにより、境界線は下側・右側に隣接するマスに属するものとして扱う）。盤面左上端のピクセル `(0, 0)` は `(0, 0)` セルに対応する（前述の「余白なし」の前提による）。盤面右下端の最終ピクセル（座標が盤面の描画領域サイズ未満の最大値となる場合）は整数除算により `(14, 14)` セルに対応し、範囲内として通常どおり値を返すことをテストで確認する。一方、座標が負の値の場合、または盤面の描画領域サイズと**等しいか、それを超える**場合は、整数除算の結果が範囲外の行・列インデックス（`15` 以上、または負）となるため `None` を返す（「超える」場合だけでなく「ちょうど等しい」場合も `None` となる点に注意）。
- **対応要件ID・コンポーネントID**: REQ-04 ／ COMP-04

#### FUNC-18: `BoardView._on_canvas_click(self, event: tk.Event) -> None`

- **所属コンポーネント**: COMP-04
- **入力**: `event: tk.Event`（tkinterが生成するイベントオブジェクト。`event.x`, `event.y` にクリック位置のピクセル座標を持つ）
- **出力**: なし
- **処理内容**: `event.x`, `event.y` をFUNC-17 `_pixel_to_cell` に渡し `(row, col)` を取得する。`None` が返った場合（盤面外クリック）は何もしない。値が取得できた場合、コンストラクタで保持したコールバック `on_cell_click(row, col)` を呼び出す（実質的にCOMP-03の `on_board_click` を呼び出す）。
- **副作用**: あり。コールバック呼び出しを介して、間接的にCOMP-02の状態変更・COMP-04/05の表示更新を引き起こしうる。
- **対応要件ID・コンポーネントID**: REQ-04 ／ COMP-04

### 4.5 COMP-05: ステータス表示・操作パネル（`StatusPanel`）

#### FUNC-19: `StatusPanel.__init__(self, parent: tk.Widget, on_restart_click: Callable[[], None]) -> None`

- **所属コンポーネント**: COMP-05
- **入力**: `parent: tk.Widget`（配置先の親ウィジェット）, `on_restart_click: Callable[[], None]`（リスタートボタン押下時に呼び出すコールバック。実体はCOMP-03の `on_restart_click`）
- **出力**: なし
- **副作用**: あり。ステータス表示用の `Label` ウィジェットと、リスタート用の `Button` ウィジェットを生成し配置する。`Button` の `command` にFUNC-23 `_on_restart_button_click` を設定する。`on_restart_click` を自身のインスタンス変数として保持する。生成直後の表示テキストは未指定でよい（COMP-03が生成直後にFUNC-20 `show_turn('black')` を呼び出すため、本関数内での初期表示指示は必須としない）。
- **対応要件ID・コンポーネントID**: REQ-10, REQ-11, REQ-12, REQ-13, CON-05 ／ COMP-05

#### FUNC-20: `StatusPanel.show_turn(self, color: str) -> None`

- **所属コンポーネント**: COMP-05
- **入力**: `color: str`（`'black'` または `'white'`）
- **出力**: なし
- **副作用**: あり。`Label` の表示テキストを、現在の手番が `color` であることをユーザーが認識できる文言に更新する（例: 「黒の番です」）。
- **境界値・異常系**: `color` に `'black'`／`'white'` 以外の値が渡されることはCOMP-03からの呼び出し契約上想定しない（本関数内での値チェックは行わない）。
- **対応要件ID・コンポーネントID**: REQ-12 ／ COMP-05

#### FUNC-21: `StatusPanel.show_winner(self, color: str) -> None`

- **所属コンポーネント**: COMP-05
- **入力**: `color: str`（`'black'` または `'white'`、勝利した色）
- **出力**: なし
- **副作用**: あり。`Label` の表示テキストを、`color` が勝利したことをユーザーが認識できる文言に更新する（例: 「黒の勝ちです」）。
- **対応要件ID・コンポーネントID**: REQ-10 ／ COMP-05

#### FUNC-22: `StatusPanel.show_draw(self) -> None`

- **所属コンポーネント**: COMP-05
- **入力**: なし（`self` のみ）
- **出力**: なし
- **副作用**: あり。`Label` の表示テキストを、引き分けであることをユーザーが認識できる文言に更新する（例: 「引き分けです」）。
- **対応要件ID・コンポーネントID**: REQ-11 ／ COMP-05

#### FUNC-23: `StatusPanel._on_restart_button_click(self) -> None`

- **所属コンポーネント**: COMP-05
- **入力**: なし（tkinterの `Button` の `command` に指定するコールバックは引数を取らない仕様のため、引数なし）
- **出力**: なし
- **処理内容**: コンストラクタで保持したコールバック `on_restart_click()` を呼び出す（実質的にCOMP-03の `on_restart_click` を呼び出す）。
- **副作用**: あり。コールバック呼び出しを介して、間接的にCOMP-02の状態リセット・COMP-04/05の表示初期化を引き起こす。
- **対応要件ID・コンポーネントID**: REQ-13 ／ COMP-05

## 5. コンポーネント×関数対応の確認

| コンポーネントID | 対応関数ID |
|---|---|
| COMP-01 | FUNC-01 |
| COMP-02 | FUNC-02, FUNC-03, FUNC-04, FUNC-05, FUNC-06, FUNC-07, FUNC-08, FUNC-09 |
| COMP-03 | FUNC-10, FUNC-11, FUNC-12, FUNC-13 |
| COMP-04 | FUNC-14, FUNC-15, FUNC-16, FUNC-17, FUNC-18 |
| COMP-05 | FUNC-19, FUNC-20, FUNC-21, FUNC-22, FUNC-23 |

上表より、コンポーネント設計書に定義された全コンポーネント（COMP-01〜05）が、それぞれ最低1つの関数に対応していることを確認した。本表の内容は `docs/traceability_matrix.md` の「②コンポーネント×関数」表に転記する。
