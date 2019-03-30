import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import tcod
from gui.core import Container, Node, Padding, Size, ColumnLayout, Align, StackLayout
from gui.tcod import BackgroundColor, Text, Border, Darken, start_app
from random import random as r


def gui_func(ctx):
    with Container(StackLayout()):
        with Container(
            BackgroundColor(3, 71, 50),
            Padding.all(1),
            ColumnLayout(spacing=1)
        ):
            Node(
                BackgroundColor(0, 129, 72),
                Padding.all(1),
                Align.right,
                Text("Hello")
            )
            Node(
                BackgroundColor(0, 129, 72),
                Padding.all(1),
                Align.centerX,
                Text("Hello")
            )
            Node(
                BackgroundColor(221, 215, 22),
                Padding.all(4),
                Text("Some text", color=(0, 129, 72))
            )
            with Container(
                BackgroundColor(239, 138, 23),
                Border(),
                ColumnLayout(),
            ):
                Node(Border(), Text("Some text"))
                Node(
                    BackgroundColor(239, 41, 23),
                    Border(color=(87, 15, 9)),
                    Padding.all(1),
                    Text("Some text", color=(87, 15, 9))
                )
                Node(Text("Some text"))
        
        Node(
            Padding.all(5),
            Darken(0.8),
            Border(),
            Padding.all(5),
            Text("Hello")
        )


if __name__ == "__main__":
    tcod.console_set_custom_font(
        'examples/consolas12x12_gs_tc.png',
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )

    start_app(gui_func, title="Hello World")
