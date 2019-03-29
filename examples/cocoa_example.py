import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Padding, ColumnLayout, Node, Container, Component, use_state
from gui.cocoa import Button, Slider, start_app


def gui_func(ctx):
    value, set_value = use_state(0)

    print(f"Render with {value}")

    def press():
        print(f"Click with {value}")

    def change(value):
        set_value(value)

    with Container(
        Padding.all(8.0),
        ColumnLayout()
    ):
        Node(Button("First button", on_press=press))
        Node(Button("Second button", on_press=press))
        Node(Slider(on_change=change))


if __name__ == "__main__":
    start_app(gui_func, title="Hello World")
