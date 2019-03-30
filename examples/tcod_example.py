import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import tcod
from gui.core import Container, Node, Padding, Size, ColumnLayout
from gui.tcod import BackgroundColor, Text, start_app
from random import random as r

def gui_func(ctx):
    with Container(
        Padding.all(1),
        ColumnLayout(spacing=1)
    ):
        Node(
            BackgroundColor(200, 0, 0),
            Size.height(4)
        )
        Node(
            BackgroundColor(40, 100, 40),
            Padding.all(1),
            Text("Hello")
        )
        Node(
            BackgroundColor(40, 40, 200),
            Padding.all(4),
            Text("Some text")
        )


if __name__ == "__main__":
    tcod.console_set_custom_font(
        'examples/consolas12x12_gs_tc.png',
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )

    start_app(gui_func, title="Hello World")
