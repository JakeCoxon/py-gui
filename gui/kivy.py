from attr import attrs, attrib
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from .geom import Point
import gui.core as gui


class KivyRootElement(gui.RootElement):
    pass


class KivyElement(gui.Element):
    pass


@attrs
class BackgroundColor(gui.ElementWidget):
    color = attrib()

    class ElementType(KivyElement):
        def perform_layout(self, constraints):
            self.child.layout(constraints)
            self.bounds.size = self.child.bounds.size

        def draw(self, renderer, pos):
            pos += self.bounds.pos
            with renderer.canvas:
                Color(*self.widget.color, mode='hsv')
                Rectangle(pos=(pos.x, pos.y), size=(self.bounds.size.x, self.bounds.size.y))

            # self.child.draw(renderer, pos)


def start_app(gui_func, title):

    w = Widget()

    class KApp(App):
        def get_application_name(self):
            return title

        def build(self):
            return w

        # def on_start(self, arg):
        #     pass

    app = KApp()
    canvas = w.canvas

    root = KivyRootElement()
    context = gui.Context(
        root=root,
        visitor=gui.Visitor(root)
    )

    gui.update_ui(context, gui_func)

    class Renderer:
        pass

    renderer = Renderer()
    renderer.canvas = canvas

    # root.draw(renderer, Point(0, 0))

    def on_draw(window):

        constraints = gui.BoxConstraints.from_w_h(window.width, window.height)
        root.layout(constraints)
        root.draw(renderer, Point(0, 0))

    def on_start(app):
        app.root_window.bind(on_draw=on_draw)

    app.bind(on_start=on_start)
    app.run()

