import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Container, Node, Padding, Size, ColumnLayout
from gui.tcod import BackgroundColor, Text, start_app
from random import random as r


def gui_func(ctx):
    with Container(
        Padding.all(2),
        ColumnLayout(spacing=2)
    ):
        Node(
            BackgroundColor(255, 0, 0),
            Size.height(4)
        )
        Node(
            BackgroundColor(0, 255, 0),
            Text("Hello")
        )


if __name__ == "__main__":
    start_app(gui_func, title="Hello World")
