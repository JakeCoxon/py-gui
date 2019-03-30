from attr import attrs, attrib
from gui.core import Element, ElementWidget, RootElement
from gui.geom import Point
import gui
import tcod


@attrs
class Text(ElementWidget):
    label = attrib()
    color = attrib(default=(255, 255, 255))

    class ElementType(Element):
        def perform_layout(self, constraints):
            size = Point(len(self.widget.label), 1)
            size = constraints.constrain(size)
            self.bounds.size = size

        def draw(self, renderer, pos):
            renderer.console.default_fg = self.widget.color
            renderer.console.print_(
                pos.x,
                pos.y,
                self.widget.label
            )


@attrs
class BackgroundColor(ElementWidget):
    r = attrib()
    g = attrib()
    b = attrib()
    
    class ElementType(Element):
        def perform_layout(self, constraints):
            self.child.perform_layout(constraints)
            self.bounds.size = self.child.bounds.size

        def draw(self, renderer, pos):
            x = slice(pos.x, pos.x + self.bounds.size.x)
            y = slice(pos.y, pos.y + self.bounds.size.y)
            renderer.console.bg[y, x] = (self.widget.r, self.widget.g, self.widget.b)
            renderer.console.ch[y, x] = ord(' ')
            self.child.draw(renderer, pos)


class TcodRootElement(RootElement):
    pass

def start_app(gui_func, title):
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = 50
    LIMIT_FPS = 20
    fullscreen = False
    tcod.sys_set_fps(LIMIT_FPS)

    root = TcodRootElement()
    context = gui.Context(
        root=root,
        visitor=gui.Visitor(root)
    )

    gui.update_ui(context, gui_func)

    class Renderer:
        pass

    renderer = Renderer()

    with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, fullscreen) as root_console:

        renderer.console = root_console
        constraints = gui.BoxConstraints.from_w_h(SCREEN_WIDTH, SCREEN_HEIGHT)
        root.layout(constraints)
        root.draw(renderer, Point(0, 0))
        tcod.console_flush()
        

        while not tcod.console_is_window_closed():
            tcod.console_wait_for_keypress(True)