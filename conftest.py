"""pytest共通設定。

`tests/` から `src/` 配下のモジュール（例: `game_logic`）を直接importできるように、
プロジェクトルート直下の `src` ディレクトリを `sys.path` に追加する。

COMP-02（ゲームロジック層）はtkinter等の外部ライブラリに依存しない設計（NFR-05）のため、
本ファイルはパス設定のみを行い、GUI関連の初期化は一切行わない。
"""

import os
import sys

_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
