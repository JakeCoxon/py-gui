import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Container, Node, Padding, Size, ColumnLayout
from gui.kivy import BackgroundColor, start_app
from random import random as r


def gui_func(ctx):
    with Container(
        ColumnLayout()
    ):
        Node(
            Padding.all(50.0),
            BackgroundColor(color=(r(), 1, 1)),
            Size.height(100)
        )
        Node(
            Padding.all(50.0),
            BackgroundColor(color=(r(), 1, 1)),
            Size.height(100)
        )


if __name__ == "__main__":
    start_app(gui_func, title="Hello World")