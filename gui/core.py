import itertools
import math
from attr import attrs, attrib
from .geom import Point


class Visitor:
    def __init__(self, root):
        self.root = root
        self.parents = [root]
        self.ids = [-1]
        # self.current_node = None

    @property
    def current_node(self):
        if self.current_id >= len(self.current_parent.children):
            return None
        return self.current_parent.children[self.current_id]

    @property
    def current_parent(self):
        return self.parents[-1]

    @property
    def current_id(self):
        return self.ids[-1]

    def get_next_node(self):
        next_id = self.current_id + 1
        if next_id >= len(self.current_parent.children):
            return None
        node = self.current_parent.children[next_id]
        return node

    def rest_children(self):
        id = self.current_id
        while id < len(self.current_parent.children):
            yield self.current_parent.children[id]
            id += 1

    def next_node(self):
        current_node = self.get_next_node()
        self.ids[-1] += 1

    def enter_node(self):
        self.parents.append(self.current_node)
        # self.current_node = None
        self.ids.append(-1)
    
    def exit_node(self):
        # self.current_node = self.current_parent
        self.parents.pop()
        self.ids.pop()


def get_matching_node(visitor, match_node, node_type, key):
    if match_node is None:
        return None
    if compare_types(match_node == node_type):
        return match_node

    for match_node in visitor.rest_children():
        if compare_types(match_node, node_type):
            return match_node


def create_node(visitor, node_type, key=None):
    # print(f"Creating node {node_type} with key {key}")
    return node_type.create_element()


def align_with_node(visitor, node_type, key=None):
    existing_node = get_matching_node(visitor, visitor.current_node, node_type, key)
    if existing_node is not None:
        # print(f"Removing {existing_node}")
        visitor.current_parent.remove_remove(existing_node)
    node = existing_node or create_node(visitor, node_type, key)
    # TODO: Some stuff here
    node.widget = node_type
    if node is None:
        return
    # print(f"Inserting {node}")
    visitor.current_parent.add_child(visitor.current_id, node)


def clear_unvisited(visitor, parent, node):
    pass


def open_node(visitor, node_type, key=None):
    # print(f"Open {node_type}")
    visitor.next_node()
    align_with_node(visitor, node_type, key)
    visitor.enter_node()
    return visitor.current_parent


def close_node(visitor):
    clear_unvisited(visitor, visitor.current_parent, visitor.get_next_node())
    visitor.exit_node()


def node_visitor(visitor):
    class Node:
        def __init__(self, node_type):
            self.node_type = node_type

        def __enter__(self):
            open_node(visitor, self.node_type)

        def __exit__(self, type, value, traceback):
            close_node(visitor)
    return Node


def compare_types(cls, element, new_widget):
    if element.widget.__class__ != new_widget.__class__:
        return False
    return True


@attrs
class ConsoleRenderer:
    console = attrib()


@attrs
class EdgeInsets:
    top = attrib(default=0)
    right = attrib(default=0)
    bottom = attrib(default=0)
    left = attrib(default=0)

    @property
    def horizontal(self):
        return self.left + self.right

    @property
    def vertical(self):
        return self.top + self.bottom

    @property
    def size(self):
        return Point(self.horizontal, self.vertical)

    @property
    def offset(self):
        return Point(self.left, self.top)


@attrs
class BoxConstraints:
    min_width = attrib(default=0)
    min_height = attrib(default=0)
    max_width = attrib(default=math.inf)
    max_height = attrib(default=math.inf)

    def constrain_width(self, width=math.inf):
        return min(max(width, self.min_width), self.max_width)

    def constrain_height(self, height=math.inf):
        return min(max(height, self.min_height), self.max_height)

    def constrain(self, size):
        return Point(
            self.constrain_width(size.x),
            self.constrain_height(size.y)
        )

    def loosen(self):
        return BoxConstraints(
            min_width=0,
            min_height=0,
            max_width=self.max_width,
            max_height=self.max_height
        )

    def deflate(self, insets):
        deflated_min_w = max(0, self.min_width - insets.horizontal)
        deflated_min_h = max(0, self.min_height - insets.vertical)
        return BoxConstraints(
            min_width=deflated_min_w,
            min_height=deflated_min_h,
            max_width=max(deflated_min_w, self.max_width - insets.horizontal),
            max_height=max(deflated_min_h, self.max_height - insets.vertical),
        )

    @property
    def has_bounded_width(self):
        return self.max_width < math.inf
    
    @property
    def has_bounded_height(self):
        return self.max_height < math.inf

    @classmethod
    def from_size(cls, size):
        return BoxConstraints(size.x, size.y, size.x, size.y)

    @classmethod
    def from_w_h(cls, w, h):
        return BoxConstraints(w, h, w, h)



@attrs
class Bounds:
    pos = attrib(factory=Point)
    size = attrib(factory=Point)


@attrs
class Element:
    widget = attrib(default=None)
    parent = attrib(default=None)
    # layout = attrib(default=None)
    # draw = attrib(default=None)
    bounds = attrib(factory=Bounds)
    children = attrib(factory=list)

    def remove_child(self, child):
        child.detatch_from_parent()
        self.children.remove(child)

    def add_child(self, index, child):
        self.children.insert(index, child)
        child.attach_to_parent(self)

    def attach_to_parent(self, parent):
        self.parent = parent

    def detatch_from_parent(self):
        self.parent = None

    def layout(self, constraints):
        return self.perform_layout(constraints)

    def perform_layout(self, constraints):
        raise NotImplementedError()
    
    @property
    def child(self):
        count = len(self.children)
        if count == 0:
            return
        assert count == 1
        return self.children[0]


class RootElement(Element):
    def __init__(self):
        super().__init__()
        self.widget = None

    def perform_layout(self, constraints):
        self.child.layout(constraints)
        
    def draw(self, renderer, pos):
        self.child.draw(renderer, pos)


class ElementWidget:
    def create_element(self):
        return self.ElementType(widget=self)


@attrs
class Constraint(ElementWidget):
    constraints = attrib(default=BoxConstraints())

    class ElementType(Element):
        def perform_layout(self, constraints):
            child_constraints = BoxConstraints(
                min_width=max(constraints.min_width, self.widget.constraints.min_width),
                min_height=max(constraints.min_height, self.widget.constraints.min_height),
                max_width=min(constraints.max_width, self.widget.constraints.max_width),
                max_height=min(constraints.max_height, self.widget.constraints.max_height),
            )
            self.child.perform_layout(child_constraints)
            self.bounds.size = self.child.bounds.size
            
        def draw(self, renderer, pos):
            self.child.draw(renderer, pos + self.child.bounds.pos)


def MinWidth(min_width):
    return Constraint(BoxConstraints(min_width=min_width))


def MaxWidth(max_width):
    return Constraint(BoxConstraints(max_width=max_width))


def MinHeight(min_height):
    return Constraint(BoxConstraints(min_height=min_height))


def MaxHeight(max_height):
    return Constraint(BoxConstraints(max_height=max_height))

@attrs
class ColumnLayout(ElementWidget):
    spacing = attrib(default=0)

    class ElementType(Element):
        def perform_layout(self, constraints):
            self.bounds.size = Point()
            for child in self.children:
                if self.bounds.size.y and self.widget.spacing:
                    self.bounds.size += Point(0, self.widget.spacing)

                child_constraints = BoxConstraints(
                    min_width=constraints.max_width,
                    min_height=0,
                    max_width=constraints.max_width,
                    max_height=constraints.max_height
                )
                child.layout(child_constraints)
                child.bounds.pos = Point(
                    x=0,
                    y=self.bounds.size.y
                )
                # todo constrain rest children heights
                self.bounds.size = Point(
                    x=max(self.bounds.size.x, child.bounds.size.x),
                    y=self.bounds.size.y + child.bounds.size.y
                )
            
        def draw(self, renderer, pos):
            for child in self.children:
                child.draw(renderer, pos + child.bounds.pos)


@attrs
class Padding(ElementWidget):
    inset = attrib()

    @classmethod
    def all(cls, v):
        return Padding(EdgeInsets(v, v, v, v))

    @classmethod
    def trbl(cls, t, r, b, l):
        return Padding(EdgeInsets(t, r, b, l))

    class ElementType(Element):
        def perform_layout(self, constraints):
            inner_constraint = constraints.deflate(self.widget.inset)
            self.child.layout(inner_constraint)
            self.child.bounds.pos = Point(
                self.widget.inset.left,
                self.widget.inset.top
            )
            self.bounds.size = constraints.constrain(
                self.child.bounds.size + self.widget.inset.size
            )
            
        def draw(self, renderer, pos):
            self.child.draw(renderer, pos + self.child.bounds.pos)


@attrs
class Align(ElementWidget):
    x = attrib(default='default')
    y = attrib(default='default')

    class ElementType(Element):
        def perform_layout(self, constraints):
            child_constraints = constraints.loosen()
            self.child.layout(child_constraints)
            self.bounds.size = constraints.constrain(
                Point(
                    math.inf if self.widget.x != 'default' else self.child.bounds.size.x,
                    math.inf if self.widget.y != 'default' else self.child.bounds.size.y
                )
            )
            self.child.bounds.pos = Point(
                (self.bounds.size.x - self.child.bounds.size.x) * self.widget.x if self.widget.x != 'default' else 0,
                (self.bounds.size.y - self.child.bounds.size.y) * self.widget.y if self.widget.y != 'default' else 0
            )
            
        def draw(self, renderer, pos):
            pos += self.child.bounds.pos
            self.child.draw(renderer, pos)


Align.right = Align(x=1)
Align.left = Align(x=0)
Align.centerX = Align(x=0.5)
Align.bottom = Align(y=1)
Align.top = Align(y=0)
Align.centerY = Align(y=0.5)


@attrs
class Size(ElementWidget):
    w = attrib(default='default')
    h = attrib(default='default')

    class ElementType(Element):
        def perform_layout(self, constraints):
            self.bounds.size = constraints.constrain(
                Point(
                    math.inf if self.widget.w == 'default' else self.widget.w,
                    math.inf if self.widget.h == 'default' else self.widget.h
                )
            )
            
        def draw(self, renderer, pos):
            pass
    
    @classmethod
    def width(cls, w):
        return Size(w=w)
    
    @classmethod
    def height(cls, h):
        return Size(h=h)

@attrs
class StackLayout(ElementWidget):
    class ElementType(Element):
        def perform_layout(self, constraints):
            self.bounds.size = constraints.constrain(Point(math.inf, math.inf))
            for child in self.children:
                child.layout(constraints)

        def draw(self, renderer, pos):
            for child in self.children:
                child.draw(renderer, pos)


def node_visitor(visitor):
    class Node:
        def __init__(self, *widgets):
            self.widgets = widgets

        def __enter__(self):
            for widget in self.widgets:
                open_node(visitor, widget)

        def __exit__(self, type, value, traceback):
            for widget in self.widgets:
                close_node(visitor)
    return Node


@attrs
class Context:
    root = attrib()
    visitor = attrib()

    def add_container(self, *args):
        return node_visitor(self.visitor)(*args)

    def add_node(self, *widgets):
        for widget in widgets:
            open_node(self.visitor, widget)
        for widget in reversed(widgets):
            close_node(self.visitor)


global_context = None


def update_ui(ctx, func, *args, **kwargs):
    global global_context
    if not ctx:
        root = RootElement()
        visitor = Visitor(root)
        ctx = Context(root, visitor)

    global_context = ctx
    func(ctx, *args, **kwargs)

    return ctx


def Container(*widgets):
    return global_context.add_container(*widgets)


def Node(*widgets):
    return global_context.add_node(*widgets)

