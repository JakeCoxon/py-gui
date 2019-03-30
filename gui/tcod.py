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
                int(pos.x),
                int(pos.y),
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


@attrs
class Border(ElementWidget):
    color = attrib(default=(255, 255, 255))

    class ElementType(Element):
        def perform_layout(self, constraints):
            inner_constraint = constraints.deflate(gui.EdgeInsets(1, 1, 1, 1))
            self.child.layout(inner_constraint)
            self.child.bounds.pos = Point(1, 1)
            self.bounds.size = constraints.constrain(
                self.child.bounds.size + Point(2, 2)
            )

        def draw(self, renderer, pos):
            
            c = renderer.console
            w = self.bounds.size.x - 1
            h = self.bounds.size.y - 1

            col = self.widget.color

            c.ch[pos.y, pos.x] = tcod.CHAR_NW
            c.ch[pos.y + h, pos.x] = tcod.CHAR_SW
            c.ch[pos.y, pos.x + w] = tcod.CHAR_NE
            c.ch[pos.y + h, pos.x + w] = tcod.CHAR_SE

            c.fg[pos.y, pos.x] = col
            c.fg[pos.y + h, pos.x] = col
            c.fg[pos.y, pos.x + w] = col
            c.fg[pos.y + h, pos.x + w] = col

            c.ch[(pos.y + 1):(pos.y + h), pos.x] = tcod.CHAR_VLINE
            c.ch[(pos.y + 1):(pos.y + h), pos.x + w] = tcod.CHAR_VLINE
            c.ch[pos.y, (pos.x + 1):(pos.x + w)] = tcod.CHAR_HLINE
            c.ch[pos.y + h, (pos.x + 1):(pos.x + w)] = tcod.CHAR_HLINE
           
            c.fg[(pos.y + 1):(pos.y + h), pos.x] = col
            c.fg[(pos.y + 1):(pos.y + h), pos.x + w] = col
            c.fg[pos.y, (pos.x + 1):(pos.x + w)] = col
            c.fg[pos.y + h, (pos.x + 1):(pos.x + w)] = col

            self.child.draw(renderer, pos + self.child.bounds.pos)


@attrs
class Darken(ElementWidget):
    amount = attrib()

    class ElementType(Element):
        def perform_layout(self, constraints):
            self.child.layout(constraints)
            self.bounds.size = self.child.bounds.size

        def draw(self, renderer, pos):

            c = renderer.console
            w = self.bounds.size.x - 1
            h = self.bounds.size.y - 1
            scale = 1 - self.widget.amount

            for x in range(pos.x, pos.x + w):
                for y in range(pos.y, pos.y + h):
                    bg = c.bg[y, x]
                    fg = c.fg[y, x]
                    c.bg[y, x] = (max(bg[0] * scale, 0), max(bg[1] * scale, 0), max(bg[2] * scale, 0))
                    c.fg[y, x] = (max(fg[0] * scale, 0), max(fg[1] * scale, 0), max(fg[2] * scale, 0))
                    # c.ch[y, x] = tcod.CHAR_BLOCK1
            self.child.draw(renderer, pos)



class TcodRootElement(RootElement):
    pass


def start_app(gui_func, title):
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = 50
    LIMIT_FPS = 20
    fullscreen = False
    tcod.sys_set_fps(LIMIT_FPS)

    with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, fullscreen) as root_console:

        while not tcod.console_is_window_closed():

            root = TcodRootElement()
            context = gui.Context(
                root=root,
                visitor=gui.Visitor(root)
            )

            gui.update_ui(context, gui_func)
            
            class Renderer:
                pass

            renderer = Renderer()
            
            renderer.console = root_console
            constraints = gui.BoxConstraints.from_w_h(SCREEN_WIDTH, SCREEN_HEIGHT)
            root.layout(constraints)
            root.draw(renderer, Point(0, 0))

            tcod.console_flush()
            
            tcod.console_wait_for_keypress(True)


