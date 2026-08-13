# テスト仕様書（15×15五目並べ）

## 0. 本書の位置づけ

本書は `docs/03_function_design/function_design.md`（関数設計書、確定済み）および
`docs/02_component_design/component_design.md`（コンポーネント設計書、確定済み）を受けた
テスト工程の成果物である。各コンポーネントについて、関数設計書に記載された入出力仕様・
境界値・異常系をテストケースとして具体化し、対応するテストコード（`tests/test_*.py`）との
対応関係を明示する。

テスト工程はコンポーネント単位で分割して進め、本書は単一ファイルとして工程が進むたびに
コンポーネント節を追記していく（`docs/traceability_matrix.md` と同様の運用方針）。現時点では
COMP-02（ゲームロジック層）・COMP-04（盤面表示層）・COMP-05（ステータス表示・操作パネル層）の
節を収録する。

## 1. ID採番方針

- **テストケースID**: `TEST-01`, `TEST-02`, ... の形式で、本書内を通貫して一意に採番する
  （コンポーネントをまたいで連番とし、コンポーネントごとにリセットしない）。
- **テストモジュールID**: `TESTMOD-01`, `TESTMOD-02`, ... の形式で、実際のテストファイル
  （`tests/test_*.py`）と1対1で対応させる。
- 1つのテストケースIDが、実装上は `pytest.mark.parametrize` により複数のテスト実行
  （複数の入力値パターン）に展開される場合がある。その場合も、境界値・異常系として意味のある
  ケースのまとまり単位でテストケースIDを1つ付与する（実行時のパラメータ数とテストケースID数は
  必ずしも一致しない）。

## 2. テストモジュール一覧

| テストモジュールID | ファイルパス | 対応コンポーネントID |
|---|---|---|
| TESTMOD-01 | `tests/test_game_logic.py` | COMP-02 |
| TESTMOD-02 | `tests/test_board_view.py` | COMP-04 |
| TESTMOD-03 | `tests/test_status_panel.py` | COMP-05 |

`tests/` から `src/` 配下のモジュールをimportできるよう、プロジェクト直下に `conftest.py` を
配置し、`sys.path` に `src` ディレクトリを追加している。

## 3. COMP-02（ゲームロジック層）節

### 3.0 対象・方針

- 対象コンポーネント: COMP-02 ゲームロジック（`GameLogic` クラス、`src/game_logic.py`）
- 対応する関数ID: FUNC-02〜FUNC-09（関数設計書 4.2節）
- 対応する要件ID: REQ-01, REQ-02, REQ-04〜REQ-09, REQ-13, NFR-04, NFR-05, CON-01, CON-02, CON-03, CON-04, CON-05
- 方針: COMP-02はtkinter等のGUIライブラリに一切依存しない純粋ロジック層であるため
  （NFR-05）、`tests/test_game_logic.py` はGUIを一切起動せず、`GameLogic` / `MoveResult` /
  `RestartResult` を直接importして検証する。`GameLogic` の内部属性（`board`,
  `current_turn`, `game_state`）および内部ヘルパーメソッド（`_is_within_board` 等、先頭
  アンダースコア付き）はPython言語上はカプセル化されていないため、テストの前提条件セット
  アップ（例: 勝利まであと1手の盤面状態を直接構築する）や、関数設計書が個別に境界値を定めて
  いる内部ヘルパーの単体検証には、これらを直接参照・呼び出すホワイトボックステストの手法を
  用いる。COMP-03（GUI層）からは、このような内部属性への直接アクセスは行われない
  （4.1節の着手依頼・リスタート依頼の戻り値のみを介する）。

### 3.1 テストケース一覧

| テストID | テスト対象(関数ID) | 対応要件ID | 目的 | 入力/前提条件 | 期待結果 | 対応テスト関数名 |
|---|---|---|---|---|---|---|
| TEST-01 | FUNC-02, FUNC-04 | REQ-01, REQ-02, REQ-13, CON-01, CON-02, CON-04 | 初期状態が仕様どおり（全マス空・黒番・対局中）であることを確認する | `GameLogic()` を生成した直後 | `board` は15×15すべて `None`。`current_turn == 'black'`。`game_state == 'in_progress'` | `test_01_initial_state_all_empty_black_turn_in_progress` |
| TEST-02 | FUNC-06 | REQ-01, CON-02 | 盤面境界を含む範囲内座標が範囲内と判定されることを確認する（境界値） | `(row, col)` = `(0,0)`, `(14,14)`, `(0,14)`, `(14,0)`, `(7,7)` | いずれも `_is_within_board` が `True` | `test_02_is_within_board_true_on_boundaries` |
| TEST-03 | FUNC-06 | REQ-01, CON-02 | 盤面範囲外座標が範囲外と判定されることを確認する（境界値） | `(row, col)` = `(-1,0)`, `(15,0)`, `(0,-1)`, `(0,15)`, `(-1,-1)`, `(15,15)` | いずれも `_is_within_board` が `False` | `test_03_is_within_board_false_out_of_range` |
| TEST-04 | FUNC-05 | REQ-04, REQ-05, CON-04 | 黒番の正常着手で黒石が配置され、手番が白へ切り替わることを確認する | 初期状態から `make_move(7, 7)` | `valid=True, color='black', winner=None, is_draw=False, next_turn='white', game_over=False`。`board[7][7]=='black'`。`current_turn=='white'` | `test_04_black_move_places_stone_and_switches_turn_to_white` |
| TEST-05 | FUNC-05 | REQ-04, REQ-05, CON-04 | 白番の正常着手で白石が配置され、手番が黒へ切り替わることを確認する | `make_move(0,0)`（黒）の後、`make_move(1,1)`（白） | `valid=True, color='white', next_turn='black'`。`board[1][1]=='white'`。`current_turn=='black'` | `test_05_white_move_places_stone_and_switches_turn_to_black` |
| TEST-06 | FUNC-05 | REQ-04, CON-02 | 盤面端 `(0,0)` への配置が正常に成功することを確認する（境界値） | 初期状態から `make_move(0, 0)` | `valid=True`。`board[0][0]=='black'` | `test_06_move_at_top_left_corner_succeeds` |
| TEST-07 | FUNC-05 | REQ-04, CON-02 | 盤面端 `(14,14)` への配置が正常に成功することを確認する（境界値） | 初期状態から `make_move(14, 14)` | `valid=True`。`board[14][14]=='black'` | `test_07_move_at_bottom_right_corner_succeeds` |
| TEST-08 | FUNC-05 | REQ-06 | 既に石が置かれているマスへの配置が無効となり、盤面・手番が変化しないことを確認する | `make_move(3,3)` 後、同じ `(3,3)` に再度 `make_move` | `valid=False` かつ他フィールドも全てデフォルト値。`board[3][3]` は上書きされず `'black'` のまま。`current_turn` も変化しない | `test_08_move_on_occupied_cell_is_invalid_and_state_unchanged` |
| TEST-09 | FUNC-05 | REQ-07 | 黒勝利確定後の着手が無効となることを確認する | `game_state='black_win'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[black_win]` |
| TEST-10 | FUNC-05 | REQ-07 | 白勝利確定後の着手が無効となることを確認する | `game_state='white_win'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[white_win]` |
| TEST-11 | FUNC-05 | REQ-07 | 引き分け確定後の着手が無効となることを確認する | `game_state='draw'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[draw]` |
| TEST-12 | FUNC-05, FUNC-06 | REQ-04, CON-02 | 盤面範囲外座標への着手が例外を送出せず無効として扱われることを確認する | `(row, col)` = `(-1,0)`, `(15,0)`, `(0,-1)`, `(0,15)`, `(-1,-1)`, `(15,15)`, `(100,100)` | いずれも例外を送出せず `valid=False`。`current_turn`・`game_state` は変化しない | `test_12_move_out_of_range_is_invalid_no_exception` |
| TEST-13 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 横方向にちょうど5個連続で勝利が確定することを確認する | 横方向に黒石4個を配置済みの状態で5個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_13_horizontal_five_in_a_row_wins` |
| TEST-14 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 縦方向にちょうど5個連続で勝利が確定することを確認する | 縦方向に白石4個を配置済みの状態で5個目を `make_move` | `winner='white'`, `game_over=True`。`game_state=='white_win'` | `test_14_vertical_five_in_a_row_wins` |
| TEST-15 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 斜め右下がり方向にちょうど5個連続で勝利が確定することを確認する | 斜め右下がりに黒石4個を配置済みの状態で5個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_15_diagonal_down_right_five_in_a_row_wins` |
| TEST-16 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 斜め右上がり方向にちょうど5個連続で勝利が確定することを確認する | 斜め右上がりに白石4個を配置済みの状態で5個目を `make_move` | `winner='white'`, `game_over=True`。`game_state=='white_win'` | `test_16_diagonal_up_right_five_in_a_row_wins` |
| TEST-17 | FUNC-05, FUNC-07 | REQ-08 | 5個ちょうどではなく6個以上連続する場合も勝利と判定されることを確認する（境界値） | 横方向に黒石5個を配置済みの状態で6個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_17_six_in_a_row_also_wins` |
| TEST-18 | FUNC-05, FUNC-07 | REQ-08 | 4個連続では勝利判定にならないことを確認する（境界値） | 横方向に黒石3個を配置済みの状態で4個目を `make_move` | `winner=None`, `game_over=False`, `next_turn='white'`。`game_state=='in_progress'` | `test_18_four_in_a_row_does_not_win` |
| TEST-19 | FUNC-05 | REQ-05, REQ-07, REQ-08 | 勝敗が確定した着手では手番が切り替わらないことを確認する | 勝利確定となる `make_move` を実行 | `next_turn is None`。`current_turn` は勝者の色のまま変化しない。続けて空マスへ `make_move` すると `valid=False`（REQ-07の再確認） | `test_19_turn_does_not_switch_when_game_is_won` |
| TEST-20 | FUNC-05, FUNC-09 | REQ-09 | 225マスすべてが埋まり、かつ勝利条件を満たす色がない場合に引き分けが確定することを確認する | 5連続を作らない安全なパターンで224マスを埋め、残り1マスへ `make_move` | `valid=True, winner=None, is_draw=True, game_over=True`。`game_state=='draw'`。`_is_board_full()==True` | `test_20_board_full_without_winner_is_draw` |
| TEST-21 | FUNC-09 | REQ-09 | 224マス埋まり1マスのみ空の場合、盤面充填チェックが `False` となることを確認する（境界値） | 5連続を作らない安全なパターンで224マスを埋め、1マスを空のまま残す | `_is_board_full()==False` | `test_21_board_with_one_empty_cell_is_not_full` |
| TEST-22 | FUNC-05 | REQ-05, REQ-09 | 引き分けが確定した着手では手番が切り替わらないことを確認する | TEST-20と同様の設定で最後の1マスへ `make_move` | `next_turn is None`。`current_turn` は最後に着手した色のまま変化しない | `test_22_turn_does_not_switch_when_draw_is_confirmed` |
| TEST-23 | FUNC-03, FUNC-04 | REQ-13 | 対局中の状態からリスタートすると初期状態に戻ることを確認する | `game_state='in_progress'` の状態で `restart()` | `success=True, next_turn='black'`。`current_turn=='black'`、`game_state=='in_progress'`、全マス空 | `test_23_24_25_26_restart_from_any_state_resets_to_initial[in_progress]` |
| TEST-24 | FUNC-03, FUNC-04 | REQ-13 | 黒勝利確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='black_win'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[black_win]` |
| TEST-25 | FUNC-03, FUNC-04 | REQ-13 | 白勝利確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='white_win'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[white_win]` |
| TEST-26 | FUNC-03, FUNC-04 | REQ-13 | 引き分け確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='draw'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[draw]` |
| TEST-27 | FUNC-03, FUNC-04, FUNC-05 | REQ-13 | リスタート後、盤面がクリアされ、通常どおり着手を受け付けることを確認する | 1手着手した後 `restart()` し、同じマスへ再度 `make_move` | `restart()` 後 `board[6][6] is None`。再着手は `valid=True`, `color='black'` | `test_27_move_is_accepted_after_restart_and_board_is_clear` |
| TEST-28 | FUNC-08 | REQ-08 | 起点の隣接マスが盤面外・空・異色のいずれかの場合、連続数が0を返すことを確認する（境界値） | (a) 盤面端で方向が盤面外に出る、(b) 隣接マスが空、(c) 隣接マスが異色、の3パターンで `_count_consecutive` を直接呼び出す | いずれも戻り値が `0` | `test_28_count_consecutive_returns_zero_when_blocked` |
| TEST-29 | FUNC-05 | REQ-06, REQ-07 | 無効な着手の場合、`MoveResult` の全フィールドが仕様どおりのデフォルト値であることを確認する | 既着手マスへ再度 `make_move` | `valid=False, color=None, winner=None, is_draw=False, next_turn=None, game_over=False` | `test_29_invalid_move_result_fields_are_all_default` |
| TEST-30 | FUNC-05 | NFR-04 | 盤面全マス相当（225回）分の `make_move` 呼び出しが体感遅延なく完了する目安（1秒未満）を満たすことを確認する | 15×15全マスに対して順に `make_move` を225回呼び出す | 225回分の合計実行時間が1秒未満 | `test_30_many_moves_complete_without_noticeable_delay` |
| TEST-31 | FUNC-02〜FUNC-09（モジュール全体） | NFR-05 | `game_logic` モジュールがtkinter等のGUIライブラリをimportしていないことを確認する | `game_logic` モジュールのソースをASTで解析し、`import` 文を抽出する | `tkinter` を起点とするimportが存在しない。モジュールに `tkinter`／`tk` 属性が存在しない | `test_31_game_logic_module_does_not_depend_on_tkinter` |

### 3.2 補足

- TEST-09〜TEST-11、TEST-23〜TEST-26は、それぞれ `pytest.mark.parametrize` により
  1つのテスト関数（`test_09_10_11_move_after_game_over_is_invalid` /
  `test_23_24_25_26_restart_from_any_state_resets_to_initial`）内で複数パターンを検証している。
  pytest実行時のテストID（`test_09_10_11_move_after_game_over_is_invalid[black_win]` 等）が
  本表のテストIDと1対1で対応する。
- TEST-13〜TEST-16（4方向の勝敗判定）・TEST-20/TEST-22（引き分け）の前提条件セットアップでは、
  `GameLogic` の内部属性（`board`, `current_turn`, `game_state`）を直接書き換えるホワイト
  ボックス手法を用いている（3.0節参照）。これは `make_move` を都度呼び出して盤面を構築する
  よりも、テストが検証したい境界（「ちょうど5個」「4個」等）を明確かつ確実に再現できるための
  意図的な設計判断である。
- TEST-20・TEST-21・TEST-22で用いる「5連続を作らない安全なパターン」は、座標 `(row, col)` に
  対し `v = (2*row + col) % 5` を計算し、`v < 2` なら黒、そうでなければ白を配置するという
  規則である。横・縦・斜め（右下がり・右上がり）いずれの方向でも、連続する5マスの移動量と
  `v` の変化量の組が5と互いに素であるため、どの5マス区間を見ても `v` は0〜4を必ず1回ずつ
  取り、5マス連続で同色になることがない。これにより「勝敗が生じない盤面」を機械的に生成し、
  引き分け判定のみを独立して検証できる。
- REQ-01, REQ-02は主にTEST-01（初期状態）・TEST-02/TEST-03（範囲判定）・TEST-04〜TEST-07
  （着手による盤面状態の反映）で間接的に検証される。CON-01（CPU機能を持たない）は、
  `GameLogic` が外部からの `make_move` 呼び出しなしに自律的に石を配置しないこと（TEST-01の
  初期状態確認、および他の全テストで `make_move` を明示的に呼び出さない限り盤面が変化しない
  ことが一貫して確認されている点）をもって検証したものとする。CON-03（ネットワーク非対応）・
  CON-05（tkinterのみ使用）はGUI層・実行環境に関わる制約であり、本テストモジュール
  （COMP-02単体テスト）ではTEST-01（ロジック層の独立動作確認、CON-01と同様の趣旨）・
  TEST-31（tkinter非依存の直接確認）を通じて間接的に確認する。

## 4. COMP-04（盤面表示層）節

### 4.0 対象・方針

- 対象コンポーネント: COMP-04 盤面表示（`BoardView` クラス、`src/board_view.py`）
- 対応する関数ID: FUNC-14〜FUNC-18（関数設計書 4.4節）
- 対応する要件ID: REQ-01, REQ-02, REQ-04, REQ-13, NFR-04, CON-02, CON-04
- 方針: COMP-04は実際に `tkinter.Canvas` を生成して描画するGUI層のコンポーネントであるため、
  `tests/test_board_view.py` では実際に `tkinter.Tk()`（ルートウィンドウ）を生成し、
  `root.withdraw()` により非表示化した上で、その配下に `BoardView` を構築して検証する。
  `tk.Tk()` の生成はモジュール内で1つの `Tk` インスタンスを共有する構成とし
  （`scope="module"` のfixture）、本テストモジュールの全テスト終了後に `root.destroy()` を
  1回呼び出して破棄する。これはテスト関数ごとに毎回 `tk.Tk()` を生成・破棄すると、環境に
  よってはTclライブラリファイルの再読み込みが短時間に連続することに起因する一時的な
  ファイル読み込みエラーが散発的に発生することを確認したためであり（Python/tkinter/実装
  コード自体の不具合ではない）、これを避ける目的である。各テストで検証対象となる
  `Canvas`（`BoardView` インスタンス）はテスト関数単位で生成し、テスト終了後に
  `canvas.destroy()` で個別に破棄する（テスト間でのウィジェット・リソースのリーク防止）。
  検証は、`BoardView` が内部で保持するCanvas（`_canvas`）に対して `find_all()` /
  `itemcget()` / `coords()` / `type()` を用いてCanvas上の描画アイテムを直接調べる方法、
  および内部ヘルパー `_pixel_to_cell` / `_on_canvas_click` を直接呼び出す方法による、
  COMP-02節（3.0節）と同様のホワイトボックステストの手法を用いる。
  クリックイベントの検証（FUNC-18）は、`tkinter.Event` を模した単純なオブジェクト
  （`x`, `y` 属性のみを持つ `types.SimpleNamespace`）を用いて `_on_canvas_click` を直接
  呼び出す方法を採用する（`canvas.event_generate` によるTkイベントキュー経由の方法と比べ、
  非表示ウィンドウ・自動テスト環境でも実行結果が安定するため）。

### 4.1 テストケース一覧

| テストID | テスト対象(関数ID) | 対応要件ID | 目的 | 入力/前提条件 | 期待結果 | 対応テスト関数名 |
|---|---|---|---|---|---|---|
| TEST-32 | FUNC-14 | REQ-01, REQ-02, CON-02 | `BoardView` の初期化により、指定ピクセルサイズ（盤面全体, 600×600）の `Canvas` がparent配下に生成・配置されることを確認する | `tk.Tk()` を親として `BoardView(root, on_click)` を生成した直後 | `board_view._canvas` が `tk.Canvas` のインスタンスである。`int(canvas.cget('width')) == BOARD_PIXEL_SIZE`（600）。`int(canvas.cget('height')) == BOARD_PIXEL_SIZE`（600） | `test_32_init_creates_canvas_with_board_pixel_size` |
| TEST-33 | FUNC-14 | REQ-04 | 初期化時、Canvasの `<Button-1>` イベントに `_on_canvas_click` へのバインドが設定されていることを確認する | `BoardView(root, on_click)` を生成した直後 | `canvas.bind('<Button-1>')` が空文字列でない（Tclコマンド名が返り、バインドが存在することを示す） | `test_33_init_binds_button1_to_on_canvas_click` |
| TEST-34 | FUNC-14 | REQ-01, REQ-02, CON-02 | 初期化直後に `draw_empty_board()` が呼ばれ、格子線のみが描画され石が1つも存在しないことを確認する | `BoardView(root, on_click)` を生成した直後（`draw_empty_board()` を明示的に呼ばない） | `canvas.find_all()` の件数が32（15×15マス分の格子線: 横16本+縦16本）。すべてのアイテムの `canvas.type(item) == 'line'`。`'oval'` 型のアイテムは存在しない | `test_34_init_calls_draw_empty_board_and_draws_grid_lines_only` |
| TEST-35 | FUNC-15 | REQ-01, REQ-02, CON-02 | `draw_empty_board()` により、15×15マス分の格子線が正しい座標で描画されることを確認する（正常系） | `BoardView` 生成後、`draw_empty_board()` を明示的に呼び出す | 格子線の座標の集合が、`{(0, i*40, 600, i*40) for i in range(16)} ∪ {(i*40, 0, i*40, 600) for i in range(16)}`（計32本）と一致する。石（`oval`）は存在しない | `test_35_draw_empty_board_draws_grid_lines_with_correct_coordinates` |
| TEST-36 | FUNC-15, FUNC-16 | REQ-13 | 石が描画された状態から `draw_empty_board()` を呼ぶと、石を含む描画内容がすべて消去され格子線のみの状態に戻ることを確認する（リスタート時の盤面クリアに相当） | `BoardView` 生成後、`draw_stone(5, 5, 'black')` と `draw_stone(2, 2, 'white')` を呼び出して石を2つ描画した状態で `draw_empty_board()` を呼ぶ | `draw_empty_board()` 呼び出し後、`canvas.find_all()` の件数が32、すべて `type == 'line'` であり、`'oval'` 型のアイテムが1つも存在しない（呼び出し前は `oval` が2つ存在したことも確認する） | `test_36_draw_empty_board_clears_existing_stones` |
| TEST-37 | FUNC-16 | REQ-04, CON-04, NFR-04 | 指定マスの中心に指定色（黒・白）で塗りつぶした円が描画されることを確認する | `draw_stone(7, 7, 'black')` および `draw_stone(3, 10, 'white')` を呼び出す | (7,7)黒: 生成された `oval` の `coords` が `(284, 284, 316, 316)`（中心 (300,300)、半径16）、`itemcget('fill') == 'black'`。(3,10)白: `coords` が `(404, 124, 436, 156)`（中心 (420,140)、半径16）、`itemcget('fill') == 'white'` | `test_37_draw_stone_draws_circle_of_specified_color_at_cell_center` |
| TEST-38 | FUNC-16 | REQ-04, CON-02, CON-04 | 盤面端 `(0,0)`・`(14,14)` への石描画が正しい中心位置に行われることを確認する（境界値） | `draw_stone(0, 0, 'black')` と `draw_stone(14, 14, 'white')` を呼び出す | `(0,0)`: `coords` が `(4, 4, 36, 36)`（中心 (20,20)）。`(14,14)`: `coords` が `(564, 564, 596, 596)`（中心 (580,580)） | `test_38_draw_stone_at_board_corners_top_left_and_bottom_right` |
| TEST-39 | FUNC-17 | REQ-04, CON-02 | マス目の境界線ちょうどのピクセル座標は、整数除算の切り捨てにより下側・右側に隣接するマスに属すると判定されることを確認する（境界値） | `_pixel_to_cell(x, y)` に `(40, 0)`, `(0, 40)`, `(40, 40)` を渡す | `(40,0) -> (0,1)`。`(0,40) -> (1,0)`。`(40,40) -> (1,1)`（いずれも境界線を挟んで手前のマス `(0,0)` ではなく、次のマスに属する） | `test_39_pixel_to_cell_boundary_falls_to_next_cell` |
| TEST-40 | FUNC-17 | REQ-04, CON-02 | 盤面左上端のピクセル `(0, 0)` が `(0, 0)` セルに対応することを確認する（境界値） | `_pixel_to_cell(0, 0)` | 戻り値が `(0, 0)` | `test_40_pixel_to_cell_top_left_pixel_is_cell_0_0` |
| TEST-41 | FUNC-17 | REQ-04, CON-02 | 盤面右下端の最終ピクセル（`BOARD_PIXEL_SIZE - 1` = 599）が `(14, 14)` セルに対応し、範囲内の値を返すことを確認する（境界値） | `_pixel_to_cell(599, 599)` | 戻り値が `(14, 14)` | `test_41_pixel_to_cell_last_pixel_is_cell_14_14` |
| TEST-42 | FUNC-17 | REQ-04, CON-02 | 盤面ピクセルサイズ（600）と**ちょうど等しい**座標は `None` を返すことを確認する（境界値。「超える」場合だけでなく「等しい」場合も `None` になる点を検証する） | `_pixel_to_cell(x, y)` に `(600, 600)`, `(600, 300)`, `(300, 600)` を渡す | いずれも戻り値が `None` | `test_42_pixel_to_cell_equal_to_board_pixel_size_returns_none` |
| TEST-43 | FUNC-17 | REQ-04, CON-02 | 負の座標、および盤面ピクセルサイズを超える座標は `None` を返すことを確認する（異常系） | `_pixel_to_cell(x, y)` に `(-1, -1)`, `(-1, 300)`, `(300, -1)`, `(601, 601)`, `(1000, 1000)` を渡す | いずれも戻り値が `None` | `test_43_pixel_to_cell_negative_and_over_board_pixel_size_returns_none` |
| TEST-44 | FUNC-18 | REQ-04 | 盤面内クリックで、`_pixel_to_cell` の変換結果をもとに `on_cell_click` コールバックが正しい `(row, col)` で1回呼ばれることを確認する | `x`, `y` 属性を持つ模擬イベントオブジェクトで `_on_canvas_click(event)` を呼び出す。`(x, y) = (300, 300)` および `(45, 125)` の2パターン | `(300,300) -> (7,7)` でコールバックが呼ばれる。`(45,125) -> (3,1)`（`row` は `y` 由来、`col` は `x` 由来であることを区別して確認）でコールバックが呼ばれる。いずれもコールバックの呼び出し回数は1回 | `test_44_on_canvas_click_inside_board_invokes_callback_with_correct_cell` |
| TEST-45 | FUNC-18 | REQ-04 | 盤面外クリック（`_pixel_to_cell` が `None` を返す座標）では `on_cell_click` コールバックが呼ばれないことを確認する | `x`, `y` 属性を持つ模擬イベントオブジェクトで `_on_canvas_click(event)` を呼び出す。`(x, y) = (600, 600)` および `(-1, -1)` の2パターン | いずれもコールバックが1度も呼ばれない（呼び出し回数0） | `test_45_on_canvas_click_outside_board_does_not_invoke_callback` |
| TEST-46 | FUNC-16 | NFR-04 | 盤面全マス相当（225回）分の `draw_stone` 呼び出しが体感遅延なく完了する目安（1秒未満）を満たすことを確認する | 15×15全マスに対して順に `draw_stone(row, col, color)` を225回呼び出す（色は市松状に黒/白を交互指定） | 225回分の合計実行時間が1秒未満 | `test_46_many_draw_stone_calls_complete_without_noticeable_delay` |

### 4.2 補足

- TEST-32〜TEST-46はいずれも、実際に `tk.Tk()` を生成し `root.withdraw()` で非表示化した上で
  `BoardView` を構築し、Canvas上の実際の描画結果を検証する（4.0節参照）。`conftest.py` は
  `sys.path` への `src` 追加のみを行いGUI関連の初期化は行わないため、`import tkinter` および
  `tk.Tk()` の呼び出しは `tests/test_board_view.py` 側で行う。
- TEST-37・TEST-38（`draw_stone` の描画位置検証）で用いる中心座標・円の座標は、
  `src/board_view.py` の実装（`center = col*40+20` または `row*40+20`、
  `radius = 20 - _STONE_MARGIN(4) = 16`）から機械的に算出した値であり、関数設計書FUNC-16の
  「指定マスの中心に、指定色で塗りつぶした円を描画する」という仕様どおりの位置に描画されて
  いることの確認である。
- TEST-39〜TEST-43（`_pixel_to_cell` の境界値）は、関数設計書FUNC-17の境界値・異常系の記述
  （「境界線は下側・右側に隣接するマスに属する」「盤面の描画領域サイズと**等しい**場合も
  `None` になる」）を1件ずつ網羅する形で設計している。
- TEST-44・TEST-45（`_on_canvas_click` のクリックハンドラ検証）は、4.0節の方針に従い
  `tkinter.Event` を模した `types.SimpleNamespace(x=.., y=..)` を用いて直接呼び出す方法を
  採用している。盤面範囲外座標に対するFUNC-17（`_pixel_to_cell`）自体の`None`判定の網羅性は
  TEST-42・TEST-43で別途検証済みのため、TEST-45では代表的な2パターン（ちょうど等しい座標・
  負の座標）のみを確認する。
- REQ-01・REQ-02・CON-02は主にTEST-32・TEST-34・TEST-35（Canvasサイズ・初期格子線描画）で、
  REQ-04は主にTEST-33・TEST-37〜TEST-45（クリック→座標変換→石描画・コールバック通知の一連の
  流れ）で、REQ-13はTEST-36（リスタート時の盤面クリアに相当する `draw_empty_board()` による
  石の消去）で、CON-04はTEST-37・TEST-38（黒・白2色の描画）で、それぞれ検証する。NFR-04は
  TEST-37・TEST-46（実際の描画処理の体感遅延なしでの完了）で検証する。

## 5. COMP-05（ステータス表示・操作パネル層）節

### 5.0 対象・方針

- 対象コンポーネント: COMP-05 ステータス表示・操作パネル（`StatusPanel` クラス、`src/status_panel.py`）
- 対応する関数ID: FUNC-19〜FUNC-23（関数設計書 4.5節）
- 対応する要件ID: REQ-10, REQ-11, REQ-12, REQ-13, NFR-04, CON-04, CON-05
- 方針: COMP-05は実際に `tk.Label` / `tk.Button` を生成して表示・操作を行うGUI層のコンポーネント
  であるため、`tests/test_status_panel.py` では実際に `tkinter.Tk()`（ルートウィンドウ）を生成し、
  `root.withdraw()` により非表示化した上で、その配下に `StatusPanel` を構築して検証する。
  `tk.Tk()` の生成は、COMP-04節（4.0節）と同じ理由（Tclライブラリファイルの再読み込みに起因する
  一時的なファイル読み込みエラーの散発を避けるため）により、`tests/test_board_view.py` の
  `tk_root` fixtureと同様にモジュール内で1つの `Tk` インスタンスを共有する構成
  （`scope="module"` のfixture）とし、本テストモジュールの全テスト終了後に `root.destroy()` を
  1回呼び出して破棄する。各テストで検証対象となる `StatusPanel` インスタンスは、テスト関数単位で
  新しい親フレーム（`tk.Frame`）を生成した上でその配下に構築し、テスト終了後に `frame.destroy()`
  で破棄する（テスト間でのウィジェット・リソースのリーク防止）。検証は、`StatusPanel` が内部で
  保持するウィジェット（`_status_label`, `_restart_button`）に対して `cget()` を用いて表示テキスト・
  ウィジェット種別・ボタン設定を直接調べる方法、およびリスタートボタンの押下を模擬するために
  `tkinter.Button.invoke()`（`command` に設定された関数を実行する標準の方法）を用いる、
  COMP-04節（4.0節）と同様のホワイトボックステストの手法を用いる。

### 5.1 テストケース一覧

| テストID | テスト対象(関数ID) | 対応要件ID | 目的 | 入力/前提条件 | 期待結果 | 対応テスト関数名 |
|---|---|---|---|---|---|---|
| TEST-47 | FUNC-19 | REQ-10, REQ-11, REQ-12, REQ-13, CON-05 | 初期化により、ステータス表示用Labelとリスタート用Button（text="リスタート"）がparent配下に生成されることを確認する | `tk.Frame` を親として `StatusPanel(frame, on_restart_click)` を生成した直後 | `panel._status_label` が `tk.Label` のインスタンスである。`panel._restart_button` が `tk.Button` のインスタンスである。`panel._restart_button.cget("text") == "リスタート"` | `test_47_init_creates_label_and_restart_button` |
| TEST-48 | FUNC-19 | REQ-13, CON-05 | 初期化時、Buttonのcommandに `_on_restart_button_click` が設定されていることを確認する（commandが空でないことをもって確認） | `StatusPanel(frame, on_restart_click)` を生成した直後 | `panel._restart_button.cget("command")` が空文字列でない（Tclコマンド名が返り、commandが設定されていることを示す） | `test_48_init_sets_restart_button_command` |
| TEST-49 | FUNC-20 | REQ-12, CON-04 | `show_turn('black')` 呼び出しでLabelに「黒の番です」が表示されることを確認する | `StatusPanel` 生成後、`show_turn('black')` を呼び出す | `panel._status_label.cget("text") == "黒の番です"` | `test_49_show_turn_black_displays_black_turn_text` |
| TEST-50 | FUNC-20 | REQ-12, CON-04 | `show_turn('white')` 呼び出しでLabelに「白の番です」が表示されることを確認する | `StatusPanel` 生成後、`show_turn('white')` を呼び出す | `panel._status_label.cget("text") == "白の番です"` | `test_50_show_turn_white_displays_white_turn_text` |
| TEST-51 | FUNC-21 | REQ-10, CON-04 | `show_winner('black')` 呼び出しでLabelに「黒の勝ちです」が表示されることを確認する | `StatusPanel` 生成後、`show_winner('black')` を呼び出す | `panel._status_label.cget("text") == "黒の勝ちです"` | `test_51_show_winner_black_displays_black_win_text` |
| TEST-52 | FUNC-21 | REQ-10, CON-04 | `show_winner('white')` 呼び出しでLabelに「白の勝ちです」が表示されることを確認する | `StatusPanel` 生成後、`show_winner('white')` を呼び出す | `panel._status_label.cget("text") == "白の勝ちです"` | `test_52_show_winner_white_displays_white_win_text` |
| TEST-53 | FUNC-22 | REQ-11 | `show_draw()` 呼び出しでLabelに「引き分けです」が表示されることを確認する | `StatusPanel` 生成後、`show_draw()` を呼び出す | `panel._status_label.cget("text") == "引き分けです"` | `test_53_show_draw_displays_draw_text` |
| TEST-54 | FUNC-23 | REQ-13 | リスタートボタンを `invoke()` すると、コンストラクタで渡した `on_restart_click` コールバックが1回呼ばれることを確認する | `StatusPanel` 生成後、`panel._restart_button.invoke()` を1回呼び出す | `on_restart_click` コールバックの呼び出し回数が1 | `test_54_restart_button_invoke_calls_on_restart_click_once` |
| TEST-55 | FUNC-23 | REQ-13 | リスタートボタンを複数回 `invoke()` すると、その都度 `on_restart_click` コールバックが呼ばれることを確認する（境界値） | `StatusPanel` 生成後、`panel._restart_button.invoke()` を3回連続で呼び出す | `on_restart_click` コールバックの呼び出し回数が3 | `test_55_restart_button_invoke_multiple_times_calls_callback_each_time` |
| TEST-56 | FUNC-20, FUNC-21, FUNC-22 | REQ-10, REQ-11, REQ-12, REQ-13 | 手番表示→勝敗表示→引き分け表示→手番表示、と複数回呼び出した際に、常に最後の呼び出し内容がLabelに反映されることを確認する（表示遷移の確認。最後の手番表示への呼び出しはリスタート後にCOMP-03が `show_turn('black')` を呼び出す想定の遷移に相当する） | `StatusPanel` 生成後、`show_turn('black')` → `show_turn('white')` → `show_winner('white')` → `show_draw()` → `show_turn('black')` の順に呼び出す | 各呼び出し直後のLabelテキストが順に「黒の番です」「白の番です」「白の勝ちです」「引き分けです」「黒の番です」となる | `test_56_display_transitions_reflect_latest_call` |
| TEST-57 | FUNC-20 | NFR-04 | 手番表示更新処理（`show_turn`）を盤面全マス相当（225回）呼び出しても体感遅延なく完了する目安（1秒未満）を満たすことを確認する | `StatusPanel` 生成後、`show_turn(color)` を225回呼び出す（色は黒/白を交互指定） | 225回分の合計実行時間が1秒未満 | `test_57_many_show_turn_calls_complete_without_noticeable_delay` |

### 5.2 補足

- TEST-47〜TEST-57はいずれも、実際に `tk.Tk()` を生成し `root.withdraw()` で非表示化した上で
  `StatusPanel` を構築し、ウィジェットの実際の状態（`cget()` で取得できるテキスト・設定値）を
  検証する（5.0節参照）。`conftest.py` は `sys.path` への `src` 追加のみを行いGUI関連の初期化は
  行わないため、`import tkinter` および `tk.Tk()` の呼び出しは `tests/test_status_panel.py` 側で
  行う。
- TEST-48（Buttonの `command` 設定確認）は、`tests/test_board_view.py` のTEST-33（Canvasの
  `<Button-1>` バインド確認）と同様に、tkinter内部のTclコマンド名が空でないことをもって
  「commandが設定されている」ことの間接的な確認とする。commandが実際に `_on_restart_button_click`
  （ひいては呼び出し元の `on_restart_click`）を呼び出すことの機能的な確認は、TEST-54・TEST-55
  （`invoke()` によるコールバック呼び出しの直接確認）で行う。
- TEST-49・TEST-50（`show_turn`）およびTEST-51・TEST-52（`show_winner`）は、`color` 引数が
  取りうる値（`'black'`／`'white'`）の2パターンをすべて網羅している。関数設計書FUNC-20・
  FUNC-21の記述のとおり、`'black'`／`'white'` 以外の値が渡されることは呼び出し契約上想定しない
  ため、値チェックに関する異常系テストは設けない。
- TEST-56は、FUNC-19〜FUNC-23の個々の単体テストとは別に、`StatusPanel` を複数回にわたって
  呼び出した際に表示状態が正しく最新の呼び出し内容に更新されること（内部状態を持たずLabelの
  テキストのみで表示を管理する設計が、連続した呼び出しに対しても矛盾なく機能すること）を
  確認するために設けている。
- REQ-10は主にTEST-51・TEST-52（`show_winner`）で、REQ-11は主にTEST-53（`show_draw`）で、
  REQ-12は主にTEST-49・TEST-50（`show_turn`）で、REQ-13は主にTEST-47・TEST-48・TEST-54・
  TEST-55（リスタートボタンの生成・押下）およびTEST-56（リスタート後の手番表示への復帰に
  相当する遷移）で、CON-04はTEST-49〜TEST-52（黒・白2色のテキスト表示）で、CON-05はTEST-47・
  TEST-48（tkinterウィジェット（`tk.Label`／`tk.Button`）としての生成確認）で、それぞれ検証する。
  NFR-04はTEST-57（表示更新処理の体感遅延なしでの完了）で検証する。
