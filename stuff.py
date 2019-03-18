import json


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
    if Element.compare_types(match_node == node_type):
        return match_node

    for match_node in visitor.rest_children():
        if Element.compare_types(match_node, node_type):
            return match_node


def create_node(visitor, node_type, key=None):
    print(f"Creating node {node_type} with key {key}")
    return Element(node_type)


def align_with_node(visitor, node_type, key=None):
    existing_node = get_matching_node(visitor, visitor.current_node, node_type, key)
    if existing_node is not None:
        print(f"Removing {existing_node}")
        visitor.current_parent.remove_remove(existing_node)
    node = existing_node or create_node(visitor, node_type, key)
    # TODO: Some stuff here
    if node is None:
        return
    print(f"Inserting {node}")
    visitor.current_parent.add_child(visitor.current_id, node)


def clear_unvisited(visitor, parent, node):
    pass


def open_node(visitor, node_type, key=None):
    print(f"Open {node_type}")
    visitor.next_node()
    align_with_node(visitor, node_type, key)
    visitor.enter_node()
    return visitor.current_parent


def close_node(visitor):
    print(f"Close")
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


class Element:
    def __init__(self, widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.children = []
        
    def remove_child(self, child):
        self.children.remove(child)

    def add_child(self, index, child):
        self.children.insert(index, child)

    @classmethod
    def compare_types(cls, element, new_widget):
        if element.widget.__class__ != new_widget.__class__:
            return False
        return True






class Background:
    def __init__(self, color):
        self.color = color


class Padding:
    def __init__(self, inset):
        self.inset = inset


class Text:
    def __init__(self, label):
        self.label = label


if __name__ == "__main__":

    root = Element(None)
    visitor = Visitor(root)
    container = node_visitor(visitor)

    def container(node, *args):
        return node_visitor(visitor)(node)

    def node(node_type):
        open_node(visitor, node_type)
        close_node(visitor)

    with container(
        Background('red'),
        # Padding(20)
    ): 
        node(Text("Hello"))
        node(Text("What is this"))

        for i in range(3):
            node(Text(f"Label {i}"))

    print(root)
    # print(json.dumps(root, indent=2))


# def something():

#     def create_button(button):
#         return widget(
#             key(button.id),
#             border_radius(2),
#             background_color('red'),
#             padding(20),
#             label("Hello")
#         )
 
#     return widget(
#         background_color('red'),
#         padding(20),
#         box(),
#         map(create_button, buttons)
#     )