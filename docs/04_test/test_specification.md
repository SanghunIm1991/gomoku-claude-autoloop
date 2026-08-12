# テスト仕様書（15×15五目並べ）

## 0. 本書の位置づけ

本書は `docs/03_function_design/function_design.md`（関数設計書、確定済み）および
`docs/02_component_design/component_design.md`（コンポーネント設計書、確定済み）を受けた
テスト工程の成果物である。各コンポーネントについて、関数設計書に記載された入出力仕様・
境界値・異常系をテストケースとして具体化し、対応するテストコード（`tests/test_*.py`）との
対応関係を明示する。

テスト工程はコンポーネント単位で分割して進め、本書は単一ファイルとして工程が進むたびに
コンポーネント節を追記していく（`docs/traceability_matrix.md` と同様の運用方針）。現時点では
COMP-02（ゲームロジック層）の節のみを収録する。

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

`tests/` から `src/` 配下のモジュールをimportできるよう、プロジェクト直下に `conftest.py` を
配置し、`sys.path` に `src` ディレクトリを追加している。

## 3. COMP-02（ゲームロジック層）節

### 3.0 対象・方針

- 対象コンポーネント: COMP-02 ゲームロジック（`GameLogic` クラス、`src/game_logic.py`）
- 対応する関数ID: FUNC-02〜FUNC-09（関数設計書 4.2節）
- 対応する要件ID: REQ-01, REQ-02, REQ-04〜REQ-09, REQ-13, NFR-04, NFR-05, CON-01, CON-02, CON-04
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
| TEST-06 | FUNC-05 | REQ-04 | 盤面端 `(0,0)` への配置が正常に成功することを確認する（境界値） | 初期状態から `make_move(0, 0)` | `valid=True`。`board[0][0]=='black'` | `test_06_move_at_top_left_corner_succeeds` |
| TEST-07 | FUNC-05 | REQ-04 | 盤面端 `(14,14)` への配置が正常に成功することを確認する（境界値） | 初期状態から `make_move(14, 14)` | `valid=True`。`board[14][14]=='black'` | `test_07_move_at_bottom_right_corner_succeeds` |
| TEST-08 | FUNC-05 | REQ-06 | 既に石が置かれているマスへの配置が無効となり、盤面・手番が変化しないことを確認する | `make_move(3,3)` 後、同じ `(3,3)` に再度 `make_move` | `valid=False` かつ他フィールドも全てデフォルト値。`board[3][3]` は上書きされず `'black'` のまま。`current_turn` も変化しない | `test_08_move_on_occupied_cell_is_invalid_and_state_unchanged` |
| TEST-09 | FUNC-05 | REQ-07 | 黒勝利確定後の着手が無効となることを確認する | `game_state='black_win'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[black_win]` |
| TEST-10 | FUNC-05 | REQ-07 | 白勝利確定後の着手が無効となることを確認する | `game_state='white_win'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[white_win]` |
| TEST-11 | FUNC-05 | REQ-07 | 引き分け確定後の着手が無効となることを確認する | `game_state='draw'` の状態で空マスへ `make_move` | `valid=False`。盤面・`game_state` は変化しない | `test_09_10_11_move_after_game_over_is_invalid[draw]` |
| TEST-12 | FUNC-05, FUNC-06 | REQ-04, CON-02 | 盤面範囲外座標への着手が例外を送出せず無効として扱われることを確認する | `(row, col)` = `(-1,0)`, `(15,0)`, `(0,-1)`, `(0,15)`, `(-1,-1)`, `(15,15)`, `(100,100)` | いずれも例外を送出せず `valid=False`。`current_turn`・`game_state` は変化しない | `test_12_move_out_of_range_is_invalid_no_exception` |
| TEST-13 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 横方向にちょうど5個連続で勝利が確定することを確認する | 横方向に黒石4個を配置済みの状態で5個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_13_horizontal_five_in_a_row_wins` |
| TEST-14 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 縦方向にちょうど5個連続で勝利が確定することを確認する | 縦方向に白石4個を配置済みの状態で5個目を `make_move` | `winner='white'`, `game_over=True`。`game_state=='white_win'` | `test_14_vertical_five_in_a_row_wins` |
| TEST-15 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 斜め右下がり方向にちょうど5個連続で勝利が確定することを確認する | 斜め右下がりに黒石4個を配置済みの状態で5個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_15_diagonal_down_right_five_in_a_row_wins` |
| TEST-16 | FUNC-05, FUNC-07, FUNC-08 | REQ-08 | 斜め右上がり方向にちょうど5個連続で勝利が確定することを確認する | 斜め右上がりに白石4個を配置済みの状態で5個目を `make_move` | `winner='white'`, `game_over=True`。`game_state=='white_win'` | `test_16_diagonal_up_right_five_in_a_row_wins` |
| TEST-17 | FUNC-05, FUNC-07 | REQ-08（境界値） | 5個ちょうどではなく6個以上連続する場合も勝利と判定されることを確認する | 横方向に黒石5個を配置済みの状態で6個目を `make_move` | `winner='black'`, `game_over=True`。`game_state=='black_win'` | `test_17_six_in_a_row_also_wins` |
| TEST-18 | FUNC-05, FUNC-07 | REQ-08（境界値） | 4個連続では勝利判定にならないことを確認する | 横方向に黒石3個を配置済みの状態で4個目を `make_move` | `winner=None`, `game_over=False`, `next_turn='white'`。`game_state=='in_progress'` | `test_18_four_in_a_row_does_not_win` |
| TEST-19 | FUNC-05 | REQ-05, REQ-08 | 勝敗が確定した着手では手番が切り替わらないことを確認する | 勝利確定となる `make_move` を実行 | `next_turn is None`。`current_turn` は勝者の色のまま変化しない。続けて空マスへ `make_move` すると `valid=False`（REQ-07の再確認） | `test_19_turn_does_not_switch_when_game_is_won` |
| TEST-20 | FUNC-05, FUNC-09 | REQ-09 | 225マスすべてが埋まり、かつ勝利条件を満たす色がない場合に引き分けが確定することを確認する | 5連続を作らない安全なパターンで224マスを埋め、残り1マスへ `make_move` | `valid=True, winner=None, is_draw=True, game_over=True`。`game_state=='draw'`。`_is_board_full()==True` | `test_20_board_full_without_winner_is_draw` |
| TEST-21 | FUNC-09 | REQ-09（境界値） | 224マス埋まり1マスのみ空の場合、盤面充填チェックが `False` となることを確認する（境界値） | 5連続を作らない安全なパターンで224マスを埋め、1マスを空のまま残す | `_is_board_full()==False` | `test_21_board_with_one_empty_cell_is_not_full` |
| TEST-22 | FUNC-05 | REQ-05, REQ-09 | 引き分けが確定した着手では手番が切り替わらないことを確認する | TEST-20と同様の設定で最後の1マスへ `make_move` | `next_turn is None`。`current_turn` は最後に着手した色のまま変化しない | `test_22_turn_does_not_switch_when_draw_is_confirmed` |
| TEST-23 | FUNC-03 | REQ-13 | 対局中の状態からリスタートすると初期状態に戻ることを確認する | `game_state='in_progress'` の状態で `restart()` | `success=True, next_turn='black'`。`current_turn=='black'`、`game_state=='in_progress'`、全マス空 | `test_23_24_25_26_restart_from_any_state_resets_to_initial[in_progress]` |
| TEST-24 | FUNC-03 | REQ-13 | 黒勝利確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='black_win'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[black_win]` |
| TEST-25 | FUNC-03 | REQ-13 | 白勝利確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='white_win'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[white_win]` |
| TEST-26 | FUNC-03 | REQ-13 | 引き分け確定後の状態からリスタートすると初期状態に戻ることを確認する | `game_state='draw'` の状態で `restart()` | 同上（TEST-23と同一の期待結果） | `test_23_24_25_26_restart_from_any_state_resets_to_initial[draw]` |
| TEST-27 | FUNC-03, FUNC-05 | REQ-13 | リスタート後、盤面がクリアされ、通常どおり着手を受け付けることを確認する | 1手着手した後 `restart()` し、同じマスへ再度 `make_move` | `restart()` 後 `board[6][6] is None`。再着手は `valid=True`, `color='black'` | `test_27_move_is_accepted_after_restart_and_board_is_clear` |
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
  ことが一貫して確認されている点）をもって検証したものとする。
