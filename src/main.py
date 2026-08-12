"""アプリケーションのエントリーポイント（COMP-01）。"""

import tkinter as tk

from game_logic import GameLogic
from main_window import MainWindow


def main() -> None:
    root = tk.Tk()
    game_logic = GameLogic()
    MainWindow(root, game_logic)
    root.mainloop()


if __name__ == "__main__":
    main()
