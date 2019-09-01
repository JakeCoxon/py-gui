import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from gui.core import Padding, ColumnLayout, RowLayout, use_state, decorate
from gui.cocoa import Button, Slider, Label, start_app


# TODO: Class component is it easier?
# class CocoaExample(Component):
#     value = state(0)

#     def press(self):
#         print(f"Click with {self.value}")

#     def press2(self):
#         print(f"Click the other one {self.value}")

#     def change(self, value):
#         self.value = value

#     def build(self):

#         with ColumnLayout(spacing=8):
#             decorate(Padding.all(8.0))

#             with Label(f"Value is {self.value}"):
#                 pass

#             with RowLayout(spacing=8):
#                 if self.value < 0.5:
#                     with Button("First button", on_press=self.press):
#                         pass
#                 else:
#                     with Button("Second button", on_press=self.press2):
#                         pass
                
#             with Slider(value=self.value, on_change=self.change):
#                 pass
            
#             with Slider(value=2 * self.value):
#                 pass


def cocoa_example(ctx):
    value, set_value = use_state(0)

    def press():
        print(f"Click with {value}")

    def press2():
        print(f"Click the other one {value}")

    def change(value):
        set_value(value)

    with ColumnLayout(spacing=8):
        decorate(Padding.all(8.0))

        with Label(f"Value is {value}"):
            pass

        with RowLayout(spacing=8):
            if value < 0.5:
                btn = Button("First button", on_press=press)
            else:
                btn = Button("Second button", on_press=press2)
            with btn:
                pass
            
        with Slider(value=value, on_change=change):
            pass
        
        with Slider(value=2 * value):
            pass


if __name__ == "__main__":
    start_app(cocoa_example, title="Hello World")
