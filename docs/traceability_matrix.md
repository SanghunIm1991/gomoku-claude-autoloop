# トレーサビリティマトリックス

要件定義書のID（REQ-xx / NFR-xx / CON-xx）を起点に、隣接する工程どうしの対応表を4つ用意する。各工程の成果物が確定し次第、行・列・○/IDを追記していく。

## ①要件×コンポーネント

| 要件ID | COMP-01 | COMP-02 | COMP-03 | COMP-04 | COMP-05 |
|---|---|---|---|---|---|
| REQ-01 | | ○ | | ○ | |
| REQ-02 | ○ | ○ | ○ | ○ | |
| REQ-03（欠番・REQ-12に統合） | | | | | |
| REQ-04 | | ○ | ○ | ○ | |
| REQ-05 | | ○ | ○ | | |
| REQ-06 | | ○ | ○ | | |
| REQ-07 | | ○ | ○ | | |
| REQ-08 | | ○ | | | |
| REQ-09 | | ○ | | | |
| REQ-10 | | | ○ | | ○ |
| REQ-11 | | | ○ | | ○ |
| REQ-12 | | | ○ | | ○ |
| REQ-13 | | ○ | ○ | ○ | ○ |
| NFR-01（欠番・CON-06に統合） | | | | | |
| NFR-02（欠番・CON-07に統合） | | | | | |
| NFR-03（欠番・CON-05に統合） | | | | | |
| NFR-04 | | ○ | ○ | ○ | ○ |
| NFR-05 | | ○ | ○ | | |
| CON-01 | | ○ | | | |
| CON-02 | | ○ | | ○ | |
| CON-03 | | ○ | ○ | | |
| CON-04 | | ○ | | ○ | ○ |
| CON-05 | ○ | ○ | ○ | ○ | ○ |
| CON-06 | ○ | | | | |
| CON-07 | ○ | | | | |

コンポーネントID一覧: COMP-01 エントリーポイント／COMP-02 ゲームロジック／COMP-03 メインウィンドウ（GUIコントローラ）／COMP-04 盤面表示（BoardView）／COMP-05 ステータス表示・操作パネル（StatusPanel）。詳細は `docs/02_component_design/component_design.md` を参照。

## ②コンポーネント×関数

| コンポーネントID | FUNC-01 | FUNC-02 | FUNC-03 | FUNC-04 | FUNC-05 | FUNC-06 | FUNC-07 | FUNC-08 | FUNC-09 | FUNC-10 | FUNC-11 | FUNC-12 | FUNC-13 | FUNC-14 | FUNC-15 | FUNC-16 | FUNC-17 | FUNC-18 | FUNC-19 | FUNC-20 | FUNC-21 | FUNC-22 | FUNC-23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| COMP-01 | ○ | | | | | | | | | | | | | | | | | | | | | | |
| COMP-02 | | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | | | | | | | | | | | | | | |
| COMP-03 | | | | | | | | | | ○ | ○ | ○ | ○ | | | | | | | | | | |
| COMP-04 | | | | | | | | | | | | | | ○ | ○ | ○ | ○ | ○ | | | | | |
| COMP-05 | | | | | | | | | | | | | | | | | | | ○ | ○ | ○ | ○ | ○ |

関数ID一覧・各関数の入出力・副作用の詳細は `docs/03_function_design/function_design.md` を参照。

## ③関数×テスト（テストモジュール単位）

| 関数ID | TESTMOD-01 |
|---|---|
| FUNC-01 | |
| FUNC-02 | TEST-01, TEST-31 |
| FUNC-03 | TEST-23, TEST-24, TEST-25, TEST-26, TEST-27, TEST-31 |
| FUNC-04 | TEST-01, TEST-23, TEST-24, TEST-25, TEST-26, TEST-27, TEST-31 |
| FUNC-05 | TEST-04, TEST-05, TEST-06, TEST-07, TEST-08, TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-19, TEST-20, TEST-22, TEST-27, TEST-29, TEST-30, TEST-31 |
| FUNC-06 | TEST-02, TEST-03, TEST-12, TEST-31 |
| FUNC-07 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-31 |
| FUNC-08 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-28, TEST-31 |
| FUNC-09 | TEST-20, TEST-21, TEST-31 |
| FUNC-10〜FUNC-23 | （COMP-03〜05分。今後のテスト工程で追記） |

テストモジュールID一覧: TESTMOD-01 = `tests/test_game_logic.py`（COMP-02対応）。テストケースの
詳細（目的・入力/前提条件・期待結果）は `docs/04_test/test_specification.md` を参照。

## ④要件×テスト（直接検証トレース、テストモジュール単位）

| 要件ID | TESTMOD-01 |
|---|---|
| REQ-01 | TEST-01, TEST-02, TEST-03 |
| REQ-02 | TEST-01 |
| REQ-03（欠番・REQ-12に統合） | |
| REQ-04 | TEST-04, TEST-05, TEST-06, TEST-07, TEST-12 |
| REQ-05 | TEST-04, TEST-05, TEST-19, TEST-22 |
| REQ-06 | TEST-08, TEST-29 |
| REQ-07 | TEST-09, TEST-10, TEST-11, TEST-19, TEST-29 |
| REQ-08 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-19, TEST-28 |
| REQ-09 | TEST-20, TEST-21, TEST-22 |
| REQ-10 | |
| REQ-11 | |
| REQ-12 | |
| REQ-13 | TEST-01, TEST-23, TEST-24, TEST-25, TEST-26, TEST-27 |
| NFR-01（欠番・CON-06に統合） | |
| NFR-02（欠番・CON-07に統合） | |
| NFR-03（欠番・CON-05に統合） | |
| NFR-04 | TEST-30 |
| NFR-05 | TEST-31 |
| CON-01 | TEST-01 |
| CON-02 | TEST-02, TEST-03, TEST-06, TEST-07, TEST-12 |
| CON-03 | |
| CON-04 | TEST-01, TEST-04, TEST-05 |
| CON-05 | |
| CON-06 | |
| CON-07 | |

REQ-10, REQ-11, REQ-12はCOMP-03/COMP-05（GUI層）の責務であり、COMP-02のテストモジュール
（TESTMOD-01）では検証対象外（今後のCOMP-03/05分のテスト工程で追記）。CON-03（ネットワーク非対応）・
CON-05（tkinterのみ使用）・CON-06（Windows限定）・CON-07（Python 3.11環境）は、いずれもGUI層・
実行環境に関する制約であり、GUIに依存しないCOMP-02の単体テストでは直接検証しない
（CON-05はNFR-05の検証（TEST-31、game_logicモジュールがtkinterに依存しないことの確認）が
間接的な裏付けとなる）。

テスト工程完了時には、④の全要件ID（REQ/NFR/CON）の行に最低1つのテストIDが記載されていることを確認し、網羅性チェックとする。ただし、REQ-03・NFR-01・NFR-02・NFR-03は要件定義書上で廃止（欠番）とし統合先（それぞれREQ-12・CON-06・CON-07・CON-05）に一本化されているため、この網羅性チェックの対象からは除外し、統合先IDの行でカバーされていることをもって足りるものとする。
