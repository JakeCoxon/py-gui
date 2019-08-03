import itertools
import math
import attr
from attr import attrs, attrib
from .geom import Point


class Visitor:
    def __init__(self, root):
        self.root = root
        self.parents = [root]
        self.ids = [-1]
        self.staging_nodes = []
        # self.current_node = None

    def reset(self):
        self.staging_nodes = []
        self.parents = [self.root]
        self.ids = [-1]

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
    if compare_types(match_node, node_type):
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
        visitor.current_parent.remove_child(existing_node)
    node = existing_node or create_node(visitor, node_type, key)
    # TODO: Some stuff here
    node.set_widget(node_type)
    # node.widget = node_type
    if node is None:
        return
    visitor.current_parent.add_child(visitor.current_id, node)


def clear_unvisited(visitor, parent, node):
    pass


def clear_staging_nodes(visitor):
    num_staging = len(visitor.staging_nodes)
    while visitor.staging_nodes:
        prev_node = visitor.staging_nodes.pop(0)
        decorators = prev_node.decorators
        visitor.staging_nodes = [
            x for x in visitor.staging_nodes
            if x not in decorators
        ]
        for decorator in decorators:
            open_node(visitor, decorator)
        open_node(visitor, prev_node)
        close_node(visitor)
        for _ in reversed(decorators):
            close_node(visitor)
        assert len(visitor.staging_nodes) < num_staging
        num_staging = len(visitor.staging_nodes)


def enter_exit_staging_nodes(visitor, staging_node):
    num_staging = len(visitor.staging_nodes)
    while visitor.staging_nodes:
        prev_node = visitor.staging_nodes.pop(0)
        decorators = prev_node.decorators
        visitor.staging_nodes = [
            x for x in visitor.staging_nodes
            if x not in decorators
        ]
        for decorator in decorators:
            open_node(visitor, decorator)
        open_node(visitor, prev_node)

        if prev_node == staging_node:
            yield
            
        clear_staging_nodes(visitor)

        close_node(visitor)
        for _ in reversed(decorators):
            close_node(visitor)
        assert len(visitor.staging_nodes) < num_staging
        num_staging = len(visitor.staging_nodes)

        if prev_node == staging_node:
            return


def pop_staging_node(visitor):
    return visitor.staging_nodes.pop()


def push_staging_node(visitor, node):
    visitor.staging_nodes.append(node)


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


def compare_types(element, new_widget):
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
    root = attrib(default=None)
    # layout = attrib(default=None)
    # draw = attrib(default=None)
    bounds = attrib(factory=Bounds)
    children = attrib(factory=list)

    def remove_child(self, child):
        child.unmount()
        self.children.remove(child)

    def add_child(self, index, child):
        self.children.insert(index, child)
        child.mount(self)

    def mount(self, parent):
        self.parent = parent
        self.root = parent.root

    def unmount(self):
        self.parent = None
        self.root = None

    def layout(self, constraints):
        return self.perform_layout(constraints)

    def perform_layout(self, constraints):
        raise NotImplementedError()

    def set_widget(self, widget):
        self.widget = widget
        try:
            for field, value in attr.asdict(widget, recurse=False).items():
                if hasattr(self, f'set_{field}'):
                    getattr(self, f'set_{field}')(value)
        except attr.exceptions.NotAnAttrsClassError:
            pass
    
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
        self.root = self

    def perform_layout(self, constraints):
        self.child.layout(constraints)
        
    def draw(self, renderer, pos):
        self.child.draw(renderer, pos)


@attrs
class Decoratable:
    def __attrs_post_init__(self):
        self.decorators = []
        visitor = get_current_context().visitor
        push_staging_node(visitor, self)

    def __enter__(self):
        visitor = get_current_context().visitor
        self.gen = enter_exit_staging_nodes(visitor, self)
        next(self.gen)
        
    def __exit__(self, type, value, traceback):
        next(self.gen, None)

    def decorate(self, *widgets):
        self.decorators.append(*widgets)
        return self


class ElementWidget(Decoratable):
    def create_element(self):
        return self.ElementType(widget=self)


class ComponentElement(Element):
    def mount(self, parent):
        super().mount(parent)
        self.states = []
        self.visitor = Visitor(self)
        self.context = Context(self, self.visitor)
        self.rebuild()

    def rebuild(self):
        self.state_cursor = 0
        build_ui_with_context(self.context, self.build)

    def build(self, context):
        pass

    def perform_layout(self, constraints):
        self.child.layout(constraints)
        self.bounds.size = self.child.bounds.size

    def draw(self, renderer, pos):
        self.child.draw(renderer, pos)

    def push_state(self, initial):
        if len(self.states) < self.state_cursor + 1:
            self.states.append(initial)
        current = self.state_cursor
        self.state_cursor += 1
        return current

    def get_state(self, idx):
        return self.states[idx]

    def set_state(self, idx, value):
        self.states[idx] = value
        self.rebuild()


def use_state(initial):
    element = get_current_context().visitor.current_parent
    idx = element.push_state(initial)
    current_value = element.get_state(idx)

    def set_state(value):
        element.set_state(idx, value)
        
    return current_value, set_state


class Component(ElementWidget):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    class ElementType(ComponentElement):
        def build(self, context):
            self.widget.func(context, *self.widget.args, **self.widget.kwargs)


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
            is_y_up = self.root.context.renderer.is_y_up
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
                y = self.bounds.size.y
                if is_y_up:
                    y = -self.bounds.size.y - child.bounds.size.y
                child.bounds.pos = Point(0, y)
                # todo constrain rest children heights
                self.bounds.size = Point(
                    x=max(self.bounds.size.x, child.bounds.size.x),
                    y=self.bounds.size.y + child.bounds.size.y
                )
            if is_y_up:
                for child in self.children:
                    child.bounds.pos += Point(0, self.bounds.size.y)
            
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
            self.constraints = constraints
            inner_constraint = constraints.deflate(self.widget.inset)
            self.child.layout(inner_constraint)
            self.child.bounds.pos = self.widget.inset.offset
            self.bounds.size = constraints.constrain(
                self.child.bounds.size + self.widget.inset.size
            )

        def set_inset(self, inset):
            if hasattr(self, 'constraints'):
                self.layout(self.constraints)
            
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

    def right():
        return Align(x=1)

    def left():
        return Align(x=0)

    def centerX():
        return Align(x=0.5)

    def bottom():
        return Align(y=1)

    def top():
        return Align(y=0)

    def centerY():
        return Align(y=0.5)



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

@attrs
class ContextProvider(ElementWidget):
    value = attrib()

    class ElementType(Element):
        
        def perform_layout(self, constraints):
            self.child.layout(constraints)
            self.bounds.size = constraints.constrain(self.child.bounds.size)

        def draw(self, renderer, pos):
            self.child.draw(renderer, pos)
        

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
    renderer = attrib(default=None)
    staging_node = attrib(default=None)

    def add_container(self, *args):
        return node_visitor(self.visitor)(*args)

    def add_node(self, *widgets):
        self.visitor.staging_nodes = [
            x for x in self.visitor.staging_nodes
            if x not in widgets
        ]
        for widget in widgets:
            open_node(self.visitor, widget)
        for widget in reversed(widgets):
            close_node(self.visitor)


context_stack = []


def build_ui_with_context(context, func):
    try:
        context.visitor.reset()
        context_stack.append(context)
        func(context)
        clear_staging_nodes(context.visitor)
        context_stack.pop()
    except Exception as e:
        print(e)


def get_current_context():
    return context_stack[-1]
    

def update_ui(context, func, *args, **kwargs):
    if not context:
        root = RootElement()
        visitor = Visitor(root)
        context = Context(root, visitor)

    context.visitor.reset()
    context_stack.append(context)
    func(context, *args, **kwargs)
    context_stack.pop()

    return context


def Container(*widgets):
    return get_current_context().add_container(*widgets)


def Node(*widgets):
    return get_current_context().add_node(*widgets)

