import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Padding, ColumnLayout, RowLayout, use_state
from gui.cocoa import Button, Slider, Label, start_app


def cocoa_example(ctx):
    value, set_value = use_state(0)

    def press():
        print(f"Click with {value}")

    def press2():
        print(f"Click the other one {value}")

    def change(value):
        set_value(value)

    with ColumnLayout(spacing=8).decorate(
        Padding.all(8.0)
    ):
        Label(f"Value is {value}")

        with RowLayout(spacing=8):
            Button("First button", on_press=press)
            Button("Second button", on_press=press2)

        Slider(on_change=change)


if __name__ == "__main__":
    start_app(cocoa_example, title="Hello World")
