# Implementing Red-Black Tree in Python
# Adapted from https://www.programiz.com/dsa/red-black-tree
from enum import Enum
from typing import Generic, Iterator, Optional, TypeVar

from ._overlay import EventPoint


class Color(Enum):
    BLACK = "black"
    RED = "red"


Value = TypeVar(
    "Value",
    int,
    EventPoint,
)


class Node(Generic[Value]):
    def __init__(self, value: Value) -> None:
        self.parent: Node[Value] = NullNode()
        self.left: Node[Value] = NullNode()
        self.right: Node[Value] = NullNode()
        self._color = Color.RED
        self._value: Value = value

    def __repr__(self) -> str:
        return f"{self.value} ({self.color.value})"

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, color: Color) -> None:
        self._color = color

    @property
    def value(self) -> Value:
        return self._value

    @value.setter
    def value(self, value: Value) -> None:
        self._value = value

    @property
    def is_null(self) -> bool:
        return isinstance(self, NullNode)

    @property
    def is_red(self) -> bool:
        return self._color == Color.RED

    @property
    def is_black(self) -> bool:
        return self._color == Color.BLACK


class TreeVisit(Enum):
    PREORDER = "preorder"
    INORDER = "inorder"
    POSTORDER = "postorder"


class RedBlackTree(Generic[Value]):
    def __init__(self) -> None:
        self._root: Node[Value] = NullNode()
        self._size: int = 0
        self._iter_style: TreeVisit = TreeVisit.PREORDER

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._size == 0

    @property
    def root(self) -> Node[Value]:
        return self._root

    def __iter__(self) -> Iterator[Node[Value]]:
        match self._iter_style:
            case TreeVisit.PREORDER:
                yield from self.preorder()
            case TreeVisit.INORDER:
                yield from self.inorder()
            case TreeVisit.POSTORDER:
                yield from self.postorder()

    def preorder(self) -> Iterator[Node[Value]]:
        """
        Preorder traversal of the tree (node, left child, right child).
        """
        yield from self._preorder(self._root)

    def inorder(self) -> Iterator[Node[Value]]:
        """
        Inorder traversal of the tree (left child, node, right child).
        """
        yield from self._inorder(self._root)

    def postorder(self) -> Iterator[Node[Value]]:
        """
        Postorder traversal of the tree (left child, right child, node).
        """
        yield from self._postorder(self._root)

    def levelorder(self) -> Iterator[Node[Value]]:
        """
        Levelorder traversal of the tree (parnt, left sibling, right sibling).
        """
        yield from self._levelorder(self._root)

    def search(self, value: Value) -> Optional[Node[Value]]:
        """
        Search for a node with the given value.

        Returns:
            Node: The node with the given value, or None if not found.
        """
        node = self._search(self._root, value)
        return node

    def minimum(self, node: Node[Value]) -> Node[Value]:
        while not node.left.is_null:
            node = node.left
        return node

    def maximum(self, node: Node[Value]) -> Node[Value]:
        while not node.right.is_null:
            node = node.right
        return node

    def successor(self, node: Node[Value]) -> Optional[Node[Value]]:
        """
        Find the successor of the given node. The successor is the node with the smallest value greater than
        the given node and it's either the minimum node in the right subtree if the right subtree exists or
        the first ancestor whose left child is also an ancestor of the given node.

        Returns:
            Node: The successor of the given node, or None if not found."""
        if not node.right.is_null:
            return self.minimum(node.right)
        parent = node.parent
        while not parent.is_null and node == parent.right:
            node = parent
            parent = parent.parent
        return parent

    def predecessor(self, node: Node[Value]) -> Optional[Node[Value]]:
        """
        Find the predecessor of the given node. The predecessor is the node with the largest value smaller than
        the given node and it's either the maximum node in the left subtree if the left subtree exists or
        the first ancestor whose right child is also an ancestor of the given node."""
        if not node.left.is_null:
            return self.maximum(node.left)
        parent = node.parent
        while not parent.is_null and node == parent.left:
            node = parent
            parent = parent.parent
        return parent

    def insert(self, value: Value) -> Node[Value]:
        """
        Insert a new node with the given value as a new leaf keeping the tree balanced.

        Returns:
            Node: The inserted node."""
        existing_node = self.search(value)
        if existing_node:
            print(f"Node {value} already exists in the tree.")
            return existing_node
        node: Node[Value] = self._insert(value)
        self._size += 1
        return node

    def delete(self, value: Value) -> None:
        """
        Delete the node with the given value from the tree.
        """
        node: Optional[Node[Value]] = self.search(value)
        if node is None:
            return

        y_original_color = node.color
        if node.left.is_null:
            x = node.right
            self._transplant(node, node.right)
        elif node.right.is_null:
            x = node.left
            self._transplant(node, node.left)
        else:
            y = self.minimum(node.right)
            y_original_color = y.color
            x = y.right
            if y.parent == node:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = node.right
                y.right.parent = y
            self._transplant(node, y)
            y.left = node.left
            y.left.parent = y
            y.color = node.color
        if y_original_color == Color.BLACK:
            self._delete_fixup(x)
        self._size -= 1

    def print_tree(self) -> None:
        """
        Print the tree horizontally in the following format:
                right_child
        root
                left_child
        """
        self._print(self._root, 1)

    def leaves(self) -> Iterator[Node[Value]]:
        """
        Return an iterator over the leaves of the tree from left to right.

        Returns:
            Iterator[Node[Value]]: An iterator over the leaves of the tree.
        """
        for node in self:
            if node.left.is_null and node.right.is_null:
                yield node

    ############################################
    # Private methods
    ############################################

    def _preorder(self, node: Node[Value]) -> Iterator[Node[Value]]:
        if node.is_null:
            return
        yield node
        yield from self._preorder(node.left)
        yield from self._preorder(node.right)

    def _inorder(self, node: Node[Value]) -> Iterator[Node[Value]]:
        if node.is_null:
            return
        yield from self._inorder(node.left)
        yield node
        yield from self._inorder(node.right)

    def _postorder(self, node: Node[Value]) -> Iterator[Node[Value]]:
        if node.is_null:
            return
        yield from self._postorder(node.left)
        yield from self._postorder(node.right)
        yield node

    def _levelorder(self, node: Node[Value]) -> Iterator[Node[Value]]:
        if node.is_null:
            return
        queue = [node]
        while queue:
            node = queue.pop(0)
            yield node
            if not node.left.is_null:
                queue.append(node.left)
            if not node.right.is_null:
                queue.append(node.right)

    def _search(self, node: Node[Value], value: Value) -> Optional[Node[Value]]:
        if node.is_null:
            return None
        if node.value == value:
            return node
        if node.value < value:
            return self._search(node.right, value)
        return self._search(node.left, value)

    def _left_rotate(self, node: Node[Value]) -> None:
        right_node: Node[Value] = node.right

        # Left subtree of right_node becomes right subtree of node
        node.right = right_node.left
        if not right_node.left.is_null:
            right_node.left.parent = node
        right_node.parent = node.parent

        if node.parent.is_null:
            # If node is root, make right_node the new root
            self._root = right_node
        elif node == node.parent.left:
            # if node is left child, make right_node the new left child
            node.parent.left = right_node
        else:
            # if node is right child, make right_node the new right child
            node.parent.right = right_node

        # node becomes left child of right_node and right_node becomes parent of node
        right_node.left = node
        node.parent = right_node

    def _right_rotate(self, node: Node[Value]) -> None:
        left_node: Node[Value] = node.left
        node.left = left_node.right

        # Right subtree of left_node becomes left subtree of node
        if not left_node.right.is_null:
            left_node.right.parent = node
        left_node.parent = node.parent

        if node.parent.is_null:
            # If node is root, make left_node the new root
            self._root = left_node
        elif node == node.parent.right:
            # if node is right child, make left_node the new right child
            node.parent.right = left_node
        else:
            # if node is left child, make left_node the new left child
            node.parent.left = left_node

        # node becomes right child of left_node and left_node becomes parent of node
        left_node.right = node
        node.parent = left_node

    def _insert(self, value: Value) -> Node[Value]:
        node = Node(value)
        parent: Node[Value] = NullNode()
        current = self._root
        # Seach the leaf node where the new node will be inserted
        while not current.is_null:
            parent = current
            if node.value < current.value:
                current = current.left
            else:
                current = current.right
        node.parent = parent
        if parent.is_null:
            self._root = node
        elif node.value < parent.value:
            parent.left = node
        else:
            parent.right = node
        node.left = NullNode()
        node.right = NullNode()
        node.color = Color.RED
        self._insert_fixup(node)
        return node

    def _insert_fixup(self, node: Node[Value]) -> None:
        while node.parent.is_red:
            # node's parent is the left child of its parent
            if node.parent == node.parent.parent.left:
                # node's parent right sibling
                uncle = node.parent.parent.right
                if uncle.is_red:
                    node.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    node.parent.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    self._right_rotate(node.parent.parent)
            else:
                # node's parent left sibling
                uncle = node.parent.parent.left
                if uncle.is_red:
                    node.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    node.parent.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    self._left_rotate(node.parent.parent)
        self._root.color = Color.BLACK

    def _delete_fixup(self, node: Node[Value]) -> None:
        # Only needed when the deleted node is black as it violates the black depth property
        while node != self._root and node.is_black:
            # node is the left child of its parent
            if node == node.parent.left:
                sibling = node.parent.right
                if sibling.is_red:
                    sibling.color = Color.BLACK
                    node.parent.color = Color.RED
                    self._left_rotate(node.parent)
                    sibling = node.parent.right
                if sibling.left.is_black and sibling.right.is_black:
                    sibling.color = Color.RED
                    node = node.parent
                else:
                    if sibling.right.is_black:
                        sibling.left.color = Color.BLACK
                        sibling.color = Color.RED
                        self._right_rotate(sibling)
                        sibling = node.parent.right

                    sibling.color = node.parent.color
                    node.parent.color = Color.BLACK
                    sibling.right.color = Color.BLACK
                    self._left_rotate(node.parent)
                    node = self._root
            # node is the right child of its parent
            else:
                sibling = node.parent.left
                if sibling.is_red:
                    sibling.color = Color.BLACK
                    node.parent.color = Color.RED
                    self._right_rotate(node.parent)
                    sibling = node.parent.left
                if sibling.right.is_black and sibling.left.is_black:
                    sibling.color = Color.RED
                    node = node.parent
                else:
                    if sibling.left.is_black:
                        sibling.right.color = Color.BLACK
                        sibling.color = Color.RED
                        self._left_rotate(sibling)
                        sibling = node.parent.left
                    sibling.color = node.parent.color
                    node.parent.color = Color.BLACK
                    sibling.left.color = Color.BLACK
                    self._right_rotate(node.parent)
                    node = self._root
        node.color = Color.BLACK

    def _transplant(self, node1: Node[Value], node2: Node[Value]) -> None:
        if node1.parent.is_null:
            self._root = node2
        elif node1 == node1.parent.left:
            node1.parent.left = node2
        else:
            node1.parent.right = node2
        node2.parent = node1.parent

    def _print(self, node: Node[Value], depth: int) -> None:
        if not node.is_null:
            self._print(node.right, depth + 1)
            print("   " * depth + f"{node}")
            self._print(node.left, depth + 1)
        # else:
        #     print("   " * depth + "NullNode (black)")


class NullNode(Node[Value]):
    def __init__(self) -> None:
        self.parent: Node[Value]
        self.left: Node[Value]
        self.right: Node[Value]
        self._value: Value
        self.color = Color.BLACK

    def __repr__(self) -> str:
        return "NullNode"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NullNode):
            return True

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
