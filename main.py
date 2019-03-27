from gui import Padding, ColumnLayout, Node, Container
from cocoa import Button, Slider, start_app


def gui_func(ctx):
    with Container(
        Padding.all(8.0),
        ColumnLayout()
    ):
        Node(Button("First button"))
        Node(Button("Second button"))
        Node(Slider())


if __name__ == "__main__":
    start_app(gui_func, title="Hello World")







