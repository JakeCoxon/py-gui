from attr import attrs, attrib
from Cocoa import *
from Foundation import NSObject, NSSize, NSPoint
import gui
from gui import Element, ElementWidget
from geom import Point


class AppDelegate (NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        print("Hello, World!")

    def sayHello_(self, sender):
        print("Hello again, World!")

    def applicationShouldTerminateAfterLastWindowClosed_(self, app):
        return True


@attrs
class CocoaElement(Element):
    view = attrib()

    @view.default
    def view_default(self):
        return self.create_view()

    def find_cocoa_parent(self):
        parent = self.parent
        while parent and not isinstance(parent, CocoaElement):
            parent = parent.parent
        return parent

    def attach_to_parent(self, parent):
        super().attach_to_parent(parent)
        parent = self.find_cocoa_parent()
        if not parent:
            raise RuntimeError("No parent to attach to")
        parent.add_subview(self.view)

    def add_subview(self):
        raise NotImplementedError()

    def create_view(self):
        raise NotImplementedError()

    def layout(self, constraints):
        self.perform_layout(constraints)
        self.view.setFrameSize_(NSSize(self.bounds.size.x, self.bounds.size.y))
        self.layout_children()

    def layout_children(self):
        def traverse_children(element, pos):
            for child in element.children:
                traverse(child, pos)
        
        def traverse(element, pos):
            pos += element.bounds.pos
            if isinstance(element, CocoaElement):
                element.view.setFrameOrigin_(NSPoint(pos.x, pos.y))
                return
            traverse_children(element, pos)
        
        traverse_children(self, self.bounds.pos)


@attrs
class CocoaRootElement(CocoaElement):
    window = attrib(kw_only=True)

    def layout(self, constraints):
        self.child.layout(constraints)
        self.layout_children()

    def add_subview(self, subview):
        self.window.contentView().addSubview_(subview)

    def create_view(self):
        return None



@attrs
class Button(ElementWidget):
    label = attrib()

    class ElementType(CocoaElement):
        def create_view(self):
            button = NSButton.alloc().initWithFrame_(((10.0, 10.0), (80.0, 80.0)))
            button.setBezelStyle_(4)
            button.setTitle_(self.widget.label)
            return button

        def perform_layout(self, constraints):
            size = Point(80.0, 40.0)
            self.bounds.size = constraints.constrain(size)

@attrs
class Slider(ElementWidget):

    class ElementType(CocoaElement):
        def create_view(self):
            button = NSSlider.alloc().init()
            return button

        def perform_layout(self, constraints):
            size = Point(80.0, 40.0)
            self.bounds.size = constraints.constrain(size)


def start_app(gui_func, title):
    app = NSApplication.sharedApplication()

    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
 
    win = NSWindow.alloc()
    frame = ((200.0, 300.0), (250.0, 200.0))
    win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
    win.setTitle_ (title)
    win.setLevel_ (3)                   # floating window

    root = CocoaRootElement(window=win)
    context = gui.Context(
        root=root,
        visitor=gui.Visitor(root)
    )

    gui.update_ui(context, gui_func)

    root.layout(gui.BoxConstraints.from_w_h(250.0, 100.0))

    win.display()
    win.orderFrontRegardless()          ## but this one does

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()

