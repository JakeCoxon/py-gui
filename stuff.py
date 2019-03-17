import json


class Visitor:
    def __init__(self, root):
        self.root = root
        self.parents = [root]
        self.ids = [-1]
        self.current_node = None

    @property
    def current_parent(self):
        return self.parents[-1]

    @property
    def current_id(self):
        return self.ids[-1]

    def get_next_node(self):
        next_id = self.current_id + 1
        if next_id >= len(self.current_parent[1]):
            return None
        node = self.current_parent[1][next_id]
        self.ids[-1] += 1
        return node

    def rest_children(self):
        id = self.current_id
        while id < len(self.current_parent[1]):
            yield self.current_parent[1][id]
            id += 1

    def next_node(self):
        self.current_node = self.get_next_node()

    def enter_node(self):
        self.parents.append(self.current_node)
        self.current_node = None
        self.ids.append(-1)
    
    def exit_node(self):
        self.current_node = self.current_parent
        self.parents.pop()
        self.ids.pop()


def get_matching_node(visitor, match_node, node_type, key):
    if match_node is None:
        return None
    if match_node[0] == node_type:
        return match_node

    for match_node in visitor.rest_children():
        if match_node[0] == node_type:
            return match_node


def create_node(visitor, node_type, key=None):
    print(f"Creating node {node_type} with key {key}")
    return [node_type, []]


def align_with_node(visitor, node_type, key=None):
    existing_node = get_matching_node(visitor, visitor.current_node, node_type, key)
    if existing_node is not None:
        print(f"Removing {existing_node[0]}")
        visitor.current_parent[1].remove(existing_node)
    node = existing_node or create_node(visitor, node_type, key)
    # TODO: Some stuff here
    if node is None:
        return
    print(f"Inserting {node[0]}")
    visitor.current_parent[1].insert(visitor.current_id, node)


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = []
        
    def remove_child(self, child):
        self.children.remove(child)

    def add_child(self, index, child):
        self.children.insert(index, child)

    @classmethod
    def compare_elements(cls, first, second):
        if first.__class__ != second.__class__:
            return False


if __name__ == "__main__":

    root = ["root", [
        [1, [
            [2, [
                [4, []],
                [4, []],
            ]],
            [8, [
                [1, []]
            ]]
        ]]
    ]]
    visitor = Visitor(root)
    container = node_visitor(visitor)

    def node(node_type):
        open_node(visitor, node_type)
        close_node(visitor)

    with container(1):
        with container(2):
            node(4)
            node(2)

            for i in range(3):
                node(7)

    print(json.dumps(root, indent=2))


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