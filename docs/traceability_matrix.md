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

| 関数ID | TESTMOD-01 | TESTMOD-02 | TESTMOD-03 | TESTMOD-04 |
|---|---|---|---|---|
| FUNC-01 | | | | |
| FUNC-02 | TEST-01, TEST-31 | | | |
| FUNC-03 | TEST-23, TEST-24, TEST-25, TEST-26, TEST-27, TEST-31 | | | |
| FUNC-04 | TEST-01, TEST-23, TEST-24, TEST-25, TEST-26, TEST-27, TEST-31 | | | |
| FUNC-05 | TEST-04, TEST-05, TEST-06, TEST-07, TEST-08, TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-19, TEST-20, TEST-22, TEST-27, TEST-29, TEST-30, TEST-31 | | | |
| FUNC-06 | TEST-02, TEST-03, TEST-12, TEST-31 | | | |
| FUNC-07 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-31 | | | |
| FUNC-08 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-28, TEST-31 | | | |
| FUNC-09 | TEST-20, TEST-21, TEST-31 | | | |
| FUNC-10 | | | | TEST-58, TEST-59, TEST-69 |
| FUNC-11 | | | | TEST-60, TEST-61, TEST-69 |
| FUNC-12 | | | | TEST-62, TEST-63, TEST-64, TEST-65, TEST-66, TEST-67, TEST-70, TEST-71, TEST-72, TEST-73, TEST-75 |
| FUNC-13 | | | | TEST-68, TEST-74 |
| FUNC-14 | | TEST-32, TEST-33, TEST-34 | | |
| FUNC-15 | | TEST-35, TEST-36 | | |
| FUNC-16 | | TEST-36, TEST-37, TEST-38, TEST-46 | | |
| FUNC-17 | | TEST-39, TEST-40, TEST-41, TEST-42, TEST-43 | | |
| FUNC-18 | | TEST-44, TEST-45 | | |
| FUNC-19 | | | TEST-47, TEST-48 | |
| FUNC-20 | | | TEST-49, TEST-50, TEST-56, TEST-57 | |
| FUNC-21 | | | TEST-51, TEST-52, TEST-56 | |
| FUNC-22 | | | TEST-53, TEST-56 | |
| FUNC-23 | | | TEST-54, TEST-55 | |

テストモジュールID一覧: TESTMOD-01 = `tests/test_game_logic.py`（COMP-02対応）、
TESTMOD-02 = `tests/test_board_view.py`（COMP-04対応）、
TESTMOD-03 = `tests/test_status_panel.py`（COMP-05対応）、
TESTMOD-04 = `tests/test_main_window.py`（COMP-03対応）。テストケースの詳細
（目的・入力/前提条件・期待結果）は `docs/04_test/test_specification.md` を参照。

## ④要件×テスト（直接検証トレース、テストモジュール単位）

| 要件ID | TESTMOD-01 | TESTMOD-02 | TESTMOD-03 | TESTMOD-04 |
|---|---|---|---|---|
| REQ-01 | TEST-01, TEST-02, TEST-03 | TEST-32, TEST-34, TEST-35 | | |
| REQ-02 | TEST-01 | TEST-32, TEST-34, TEST-35 | | TEST-60, TEST-61, TEST-69 |
| REQ-03（欠番・REQ-12に統合） | | | | |
| REQ-04 | TEST-04, TEST-05, TEST-06, TEST-07, TEST-12 | TEST-33, TEST-37, TEST-38, TEST-39, TEST-40, TEST-41, TEST-42, TEST-43, TEST-44, TEST-45 | | TEST-59, TEST-63, TEST-64, TEST-65, TEST-66, TEST-67, TEST-70 |
| REQ-05 | TEST-04, TEST-05, TEST-19, TEST-22 | | | TEST-63, TEST-64, TEST-65, TEST-66, TEST-70 |
| REQ-06 | TEST-08, TEST-29 | | | TEST-62, TEST-71 |
| REQ-07 | TEST-09, TEST-10, TEST-11, TEST-19, TEST-29 | | | TEST-62, TEST-72 |
| REQ-08 | TEST-13, TEST-14, TEST-15, TEST-16, TEST-17, TEST-18, TEST-19, TEST-28 | | | |
| REQ-09 | TEST-20, TEST-21, TEST-22 | | | TEST-65, TEST-73 |
| REQ-10 | | | TEST-51, TEST-52, TEST-56 | TEST-63, TEST-64, TEST-72 |
| REQ-11 | | | TEST-53, TEST-56 | TEST-65, TEST-73 |
| REQ-12 | | | TEST-49, TEST-50, TEST-56 | TEST-60, TEST-66, TEST-70 |
| REQ-13 | TEST-01, TEST-23, TEST-24, TEST-25, TEST-26, TEST-27 | TEST-36 | TEST-47, TEST-48, TEST-54, TEST-55, TEST-56 | TEST-59, TEST-68, TEST-74 |
| NFR-01（欠番・CON-06に統合） | | | | |
| NFR-02（欠番・CON-07に統合） | | | | |
| NFR-03（欠番・CON-05に統合） | | | | |
| NFR-04 | TEST-30 | TEST-37, TEST-46 | TEST-57 | TEST-75 |
| NFR-05 | TEST-31 | | | TEST-61, TEST-67, TEST-68 |
| CON-01 | TEST-01 | | | |
| CON-02 | TEST-02, TEST-03, TEST-06, TEST-07, TEST-12 | TEST-32, TEST-34, TEST-35, TEST-38, TEST-39, TEST-40, TEST-41, TEST-42, TEST-43 | | |
| CON-03 | | | | TEST-70 |
| CON-04 | TEST-01, TEST-04, TEST-05 | TEST-37, TEST-38 | TEST-49, TEST-50, TEST-51, TEST-52 | TEST-63, TEST-64, TEST-65, TEST-72 |
| CON-05 | | | TEST-47, TEST-48 | TEST-58, TEST-59 |
| CON-06 | | | | |
| CON-07 | | | | |

REQ-10, REQ-11, REQ-12はCOMP-03/COMP-05（GUI層）の責務であり、COMP-02のテストモジュール
（TESTMOD-01）では検証対象外。CON-03（ネットワーク非対応）・
CON-05（tkinterのみ使用）・CON-06（Windows限定）・CON-07（Python 3.11環境）は、いずれもGUI層・
実行環境に関する制約であり、GUIに依存しないCOMP-02の単体テストでは直接検証しない
（CON-05はNFR-05の検証（TEST-31、game_logicモジュールがtkinterに依存しないことの確認）が
間接的な裏付けとなる）。

TESTMOD-02（`tests/test_board_view.py`、COMP-04対応）は、コンポーネント設計書・関数設計書上
COMP-04が対応する要件のうちREQ-01, REQ-02, REQ-04, REQ-13, NFR-04, CON-02, CON-04を検証対象
とする（`docs/04_test/test_specification.md` 4.0節参照）。REQ-05〜REQ-12はCOMP-02/COMP-03/
COMP-05の責務でありCOMP-04のテストモジュールでは検証対象外。CON-05（tkinterのみ使用）は
COMP-04の対応要件としてコンポーネント設計書・関数設計書に記載があるものの、本テスト工程回
（COMP-04分）では明示的な検証対象に含めていない（COMP-01/03/05を含めたGUI層全体としての
tkinter専用確認は今後のテスト工程で検討する）。

TESTMOD-03（`tests/test_status_panel.py`、COMP-05対応）は、コンポーネント設計書・関数設計書上
COMP-05が対応する要件のうちREQ-10, REQ-11, REQ-12, REQ-13, NFR-04, CON-04, CON-05を検証対象と
する（`docs/04_test/test_specification.md` 5.0節参照）。これによりREQ-10・REQ-11・REQ-12は
本表で初めてテストIDが記載され、TESTMOD-01（COMP-02）・TESTMOD-02（COMP-04）の行の空欄が
補われた。REQ-01〜REQ-09はCOMP-02/COMP-03/COMP-04の責務でありCOMP-05のテストモジュールでは
検証対象外。CON-01〜CON-03, CON-06, CON-07はGUI表示・操作パネル自体とは直接関係しない制約
（CPU非搭載、盤面サイズ、通信方式、対応OS、実行環境）であり、COMP-05単体テストでは直接検証
しない。

TESTMOD-04（`tests/test_main_window.py`、COMP-03対応）は、コンポーネント設計書・関数設計書上
COMP-03が対応する要件のうちREQ-02, REQ-04, REQ-05, REQ-06, REQ-07, REQ-10, REQ-11,
REQ-12, REQ-13, NFR-04, NFR-05, CON-03, CON-05を検証対象とする
（`docs/04_test/test_specification.md` 6.0節参照）。COMP-03はGUI層の中でCOMP-02（ロジック層）
を呼び出す唯一のコンポーネントであるため、スタブの`game_logic`を用いた単体テスト（自身の
分岐ロジックの検証）と、実際の`GameLogic`を用いた結合テスト（COMP-02〜COMP-05の結合動作の
確認）を組み合わせている。これによりREQ-10・REQ-11・REQ-12の行にTESTMOD-03に続きTESTMOD-04の
テストIDが追加され、TESTMOD-01・TESTMOD-02の当該行の空欄はCOMP-02/COMP-04の責務外として
今後も空欄のままとなる。REQ-08・REQ-09（勝敗判定・引き分け判定ロジックそのもの）はCOMP-02の
責務、CON-04（黒・白2色の描画）はCOMP-02/COMP-04/COMP-05の責務であり、いずれもCOMP-03の
公式な対応要件ではないためCOMP-03のテストモジュールでは検証対象外だが、TESTMOD-04では
これらの判定結果・性質を受けた表示分岐の確認において間接的に利用しており、REQ-09・CON-04の
行にはTESTMOD-04のテストIDが記載されている（詳細は`docs/04_test/test_specification.md`
6.2節を参照）。REQ-01, CON-01, CON-02,
CON-06, CON-07はCOMP-03の対応要件外またはGUI表示・実行環境そのものに関する制約でありCOMP-03
単体テストでは直接検証しない。

テスト工程完了時には、④の全要件ID（REQ/NFR/CON）の行に最低1つのテストIDが記載されていることを確認し、網羅性チェックとする。ただし、REQ-03・NFR-01・NFR-02・NFR-03は要件定義書上で廃止（欠番）とし統合先（それぞれREQ-12・CON-06・CON-07・CON-05）に一本化されているため、この網羅性チェックの対象からは除外し、統合先IDの行でカバーされていることをもって足りるものとする。
