from attr import attrs, attrib
from gui.core import Element, ElementWidget
from gui.geom import Point
import tcod


@attrs
class Text(ElementWidget):
    label = attrib()
    align = attrib(default='left')

    class ElementType(Element):
        def perform_layout(self, constraints):
            size = Point(len(self.widget.label), 1)
            size = constraints.constrain(size)
            self.bounds.size = size

        def draw(self, renderer, pos):
            x = 0
            if self.widget.align == 'right':
                x = self.bounds.size.x - len(self.widget.label)
            renderer.console.print_(
                pos.x + x,
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


def start_app(gui_func, title):
    tcod.console_set_custom_font(
        'consolas12x12_gs_tc.png',
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = 50
    LIMIT_FPS = 20
    fullscreen = False
    tcod.sys_set_fps(LIMIT_FPS)

    with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, fullscreen) as root_console:

        pass