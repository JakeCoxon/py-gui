import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Container, Node, Padding, Size, ColumnLayout
from gui.kivy import Text, BackgroundColor, start_app
from random import random as r


def gui_func(ctx):
    with Container(
        BackgroundColor(1, 1, 1),
        Padding.all(16),
        ColumnLayout(spacing=16)
    ):
        with Container(
            BackgroundColor(0, 0, 0.5),
            Padding.all(16),
            ColumnLayout(spacing=16)
        ):
            Node(Text("Hello", size=40, color=(1,1,1)))
            Node(Text("Some words here", size=40, color=(1,1,1)))

        Node(
            BackgroundColor(0, 0.7, 0),
            Padding.all(16),
            Text("Some more text", size=40, color=(0,0,0))
        )


if __name__ == "__main__":
    start_app(gui_func, title="Hello World")