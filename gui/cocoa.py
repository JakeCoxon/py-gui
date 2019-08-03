from attr import attrs, attrib
from Cocoa import *
from Foundation import NSObject, NSSize, NSPoint
from gui.core import Element, ElementWidget
import gui.core as gui
from .geom import Point


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

    def mount(self, parent):
        super().mount(parent)
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

    def __attrs_post_init__(self):
        self.root = self

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
    on_press = attrib(default=None)

    class ElementType(CocoaElement):
        def create_view(self):
            button = NSButton.alloc().initWithFrame_(((10.0, 10.0), (80.0, 80.0)))
            button.setBezelStyle_(4)
            # button.setTitle_(self.widget.label)
            self.delegate = CallbackWrapper(self.callback)
            button.setTarget_(self.delegate)
            button.setAction_('action:')
            return button

        def set_label(self, label):
            self.view.setTitle_(label)

        def callback(self, sender):
            self.widget.on_press()

        def perform_layout(self, constraints):
            size = Point(80.0, 40.0)
            self.bounds.size = constraints.constrain(size)

@attrs
class Slider(ElementWidget):
    on_change = attrib(default=None)

    class ElementType(CocoaElement):
        def create_view(self):
            slider = NSSlider.alloc().init()
            self.delegate = CallbackWrapper(self.callback)
            slider.setTarget_(self.delegate)
            slider.setAction_('action:')
            return slider

        def callback(self, sender):
            self.widget.on_change(self.view.doubleValue())

        def perform_layout(self, constraints):
            size = Point(80.0, 40.0)
            self.bounds.size = constraints.constrain(size)


@attrs
class Label(ElementWidget):
    label = attrib()

    class ElementType(CocoaElement):
        def create_view(self):
            view = NSTextField.alloc().init()
            view.setEditable_(False)
            view.setSelectable_(False)
            view.setBezeled_(False)
            view.setDrawsBackground_(False)
            return view

        def set_label(self, text):
            self.view.setStringValue_(text)

        def perform_layout(self, constraints):
            # size = Point(80.0, 40.0)
            cell = self.view.cell()
            rect = cell.cellSizeForBounds_((
                (0, 0),
                (constraints.max_width, constraints.max_height)
            ))
            size = Point(rect.width, rect.height)
            self.bounds.size = constraints.constrain(size)


class CallbackWrapper(NSObject):
    # setDelegate_() often does not retain the delegate, so a reference should be maintained elsewhere.

    def __new__(cls, callback):
        return cls.alloc().initWithCallback_(callback)

    def initWithCallback_(self, callback):
        self = self.init()
        self.callback = callback
        return self

    def action_(self, sender):
        # if hasattr(sender, "vanillaWrapper"):
        #     sender = sender.vanillaWrapper()
        if self.callback is not None:
            self.callback(sender)


def start_app(gui_func, title):
    app = NSApplication.sharedApplication()

    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
 
    win = NSWindow.alloc()
    frame = ((200.0, 300.0), (250.0, 200.0))
    win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
    win.setTitle_ (title)
    win.setLevel_ (3)                   # floating window

    class CocoaRenderer:
        is_y_up = True

    root = CocoaRootElement(window=win)
    context = gui.Context(
        root=root,
        visitor=gui.Visitor(root),
        renderer=CocoaRenderer()
    )
    root.context = context

    def gui_func2(ctx):
        gui.Node(gui.Component(gui_func))

    gui.update_ui(context, gui_func2)

    root.layout(gui.BoxConstraints.from_w_h(250.0, 100.0))

    win.display()
    win.orderFrontRegardless()          ## but this one does

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()

