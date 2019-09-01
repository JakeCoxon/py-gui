from attr import attrs, attrib
from .core import (
    Context, context_stack, BaseElementWidget, Element, ElementWidget, Visitor, open_node, close_node, decorate
)


@attrs
class Widget(ElementWidget):
    name = attrib()

    class ElementType(Element):
        pass


@attrs
class Decorator(BaseElementWidget):
    name = attrib()

    class ElementType(Element):
        pass



class TestVisitor:

    def test_opening_and_closing(self):
        
        root = Element()
        visitor = Visitor(root)

        w = Widget("A")

        n = open_node(visitor, w)
        assert n.widget is w
        assert visitor.current_parent.widget is w
        assert visitor.current_node is None
        assert root.children[0].widget is w

        w = Widget("B")

        n = open_node(visitor, w)
        assert n.widget is w
        assert visitor.current_parent.widget is w
        assert visitor.current_node is None
        assert root.children[0].children[0].widget is w
        
        close_node(visitor)
        assert visitor.current_parent.widget.name == "A"
        assert visitor.current_node is None
        
        n = open_node(visitor, Widget("C"))
        assert n.widget.name == "C"
        assert visitor.current_parent.widget.name == "C"
        assert visitor.current_node is None
        assert root.children[0].children[1].widget.name == "C"
        
        close_node(visitor)
        assert visitor.current_parent.widget.name == "A"
        assert visitor.current_node is None

        close_node(visitor)
        assert visitor.current_parent == root
        assert visitor.current_node is None

        assert len(root.children) == 1
        assert root.children[0].widget.name == "A"
        assert len(root.children[0].children) == 2
        assert root.children[0].children[0].widget.name == "B"
        assert root.children[0].children[1].widget.name == "C"

        # Reset for second visit
        visitor.reset()

        assert visitor.current_node.widget.name == "A"
        n = open_node(visitor, Widget("A"))
        assert n.widget.name == "A"
        assert visitor.current_parent.widget.name == "A"

        assert visitor.current_node.widget.name == "B"
        n = open_node(visitor, Widget("B"))
        assert n.widget.name == "B"
        assert visitor.current_parent.widget.name == "B"
        assert visitor.current_node is None

        close_node(visitor)
        assert visitor.current_parent.widget.name == "A"
        assert visitor.current_node.widget.name == "C"

        # Closes A without C
        close_node(visitor)
        assert visitor.current_parent == root
        assert visitor.current_node is None
        
        assert len(root.children) == 1
        assert root.children[0].widget.name == "A"
        assert len(root.children[0].children) == 1
        assert root.children[0].children[0].widget.name == "B"


class TestContextManager:
    def test_context_manager(self):

        root = Element()
        visitor = Visitor(root)
        context = Context(root, visitor)

        context_stack.append(context)

        w_a = Widget("A")
        with w_a:
            assert context.staging_node is w_a

            w_b = Widget("B")
            with w_b:
                # w_a is mounted
                assert visitor.current_parent.widget is w_a
                assert visitor.current_node is None
                assert root.children[0].widget is w_a
                
                assert context.staging_node is w_b
            
            assert visitor.current_parent.widget is w_a
            assert visitor.current_node is None
            assert root.children[0].children[0].widget is w_b

            assert visitor.current_parent.widget is w_a
            assert visitor.current_node is None

            w_c = Widget("C")
            with w_c:
                assert context.staging_node is w_c
            
            assert visitor.current_parent.widget is w_a
            assert visitor.current_node is None
            assert root.children[0].children[1].widget is w_c

            w_d = Widget("D")
            with w_d:
                assert context.staging_node is w_d
                d1 = Decorator("decorateA")
                d2 = Decorator("decorateB")
                decorate(d1)
                decorate(d2)
                assert context.staging_node.decorators[0] is d1
                assert context.staging_node.decorators[1] is d2
            
            assert len(root.children[0].children) == 3

            assert root.children[0].children[2].widget is d1
            assert root.children[0].children[2].children[0].widget is d2
            assert root.children[0].children[2].children[0].children[0].widget is w_d

        assert visitor.current_parent == root
        assert visitor.current_node is None

        assert len(root.children) == 1
        assert root.children[0].widget is w_a
        assert root.children[0].children[0].widget is w_b
        assert root.children[0].children[1].widget is w_c
        assert root.children[0].children[2].widget is d1
        assert root.children[0].children[2].children[0].widget is d2
        assert root.children[0].children[2].children[0].children[0].widget is w_d
        
        context_stack.pop()