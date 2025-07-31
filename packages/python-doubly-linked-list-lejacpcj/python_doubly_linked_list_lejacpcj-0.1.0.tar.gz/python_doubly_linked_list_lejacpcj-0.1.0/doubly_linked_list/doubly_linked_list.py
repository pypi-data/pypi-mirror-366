"""
Doubly Linked List implementation for Python.

Warning: This implementation is not thread-safe. For concurrent access,
use external synchronization (e.g., threading.Lock).
"""

from typing import Any, Iterator, Optional

from .node import Node

# Configuration constants
_MAX_SAFE_SIZE = 2**63 - 1  # Maximum safe integer size


class DoublyLinkedList:
    """
    A doubly linked list implementation with full Python integration.

    This class provides a complete doubly linked list with all standard
    list operations and Pythonic interfaces.
    """

    def __init__(self, iterable: Optional[Any] = None) -> None:
        """Initialize a doubly linked list.

        Args:
            iterable: Optional iterable to initialize the list with

        Raises:
            TypeError: If iterable is not iterable
        """
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0

        if iterable is not None:
            try:
                for item in iterable:
                    self.append(item)
            except TypeError:
                raise TypeError("Argument must be iterable") from None

    @property
    def is_empty(self) -> bool:
        """Check if the list is empty."""
        return self._size == 0

    def append(self, value: Any) -> None:
        """Add an element to the end of the list.

        Args:
            value: The value to append

        Raises:
            OverflowError: If the list size would exceed maximum safe integer
        """
        if self._size >= _MAX_SAFE_SIZE:
            raise OverflowError("List size would exceed maximum safe integer")

        new_node = Node(value)
        if self.is_empty:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            if self.tail is not None:  # Type guard for mypy
                self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def prepend(self, value: Any) -> None:
        """Add an element to the beginning of the list.

        Args:
            value: The value to prepend

        Raises:
            OverflowError: If the list size would exceed maximum safe integer
        """
        if self._size >= _MAX_SAFE_SIZE:
            raise OverflowError("List size would exceed maximum safe integer")

        new_node = Node(value)
        if self.is_empty:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            if self.head is not None:  # Type guard for mypy
                self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def insert(self, index: int, value: Any) -> None:
        """Insert an element at a specific position.

        Args:
            index: Position to insert at
            value: Value to insert

        Raises:
            TypeError: If index is not an integer
            OverflowError: If the list size would exceed maximum safe integer
        """
        if not isinstance(index, int):
            raise TypeError("Index must be an integer")

        if self._size >= _MAX_SAFE_SIZE:
            raise OverflowError("List size would exceed maximum safe integer")

        if index < 0:
            index += self._size

        if index <= 0:
            self.prepend(value)
        elif index >= self._size:
            self.append(value)
        else:
            new_node = Node(value)
            current = self._get_node_at_index(index)

            new_node.prev = current.prev
            new_node.next = current
            if current.prev is not None:  # Type guard for mypy
                current.prev.next = new_node
            current.prev = new_node
            self._size += 1

    def remove(self, value: Any) -> None:
        """Remove the first occurrence of a value."""
        current = self.head
        while current:
            if current.value == value:
                self._remove_node(current)
                return
            current = current.next
        raise ValueError(f"{value} not in list")

    def pop(self, index: int = -1) -> Any:
        """Remove and return element at index (last by default)."""
        if self.is_empty:
            raise IndexError("pop from empty list")

        if index < 0:
            index += self._size

        if index < 0 or index >= self._size:
            raise IndexError("list index out of range")

        node = self._get_node_at_index(index)
        value = node.value
        self._remove_node(node)
        return value

    def clear(self) -> None:
        """Remove all elements from the list."""
        # Break all node references to prevent memory leaks
        current = self.head
        while current:
            next_node = current.next
            current.next = None
            current.prev = None
            current = next_node

        self.head = self.tail = None
        self._size = 0

    def index(self, value: Any) -> int:
        """Return the index of the first occurrence of value."""
        current = self.head
        for i in range(self._size):
            if current is not None and current.value == value:
                return i
            if current is not None:
                current = current.next
        raise ValueError(f"{value} is not in list")

    def count(self, value: Any) -> int:
        """Return the number of occurrences of value."""
        count = 0
        current = self.head
        while current:
            if current.value == value:
                count += 1
            current = current.next
        return count

    def reverse(self) -> None:
        """Reverse the list in place."""
        current = self.head
        while current:
            current.next, current.prev = current.prev, current.next
            current = current.prev
        self.head, self.tail = self.tail, self.head

    def copy(self) -> "DoublyLinkedList":
        """Return a shallow copy of the list."""
        new_list = DoublyLinkedList()
        current = self.head
        while current:
            new_list.append(current.value)
            current = current.next
        return new_list

    def _get_node_at_index(self, index: int) -> Node:
        """Get the node at a specific index."""
        if index < 0 or index >= self._size:
            raise IndexError("list index out of range")

        # Optimize by starting from head or tail
        if index < self._size // 2:
            current = self.head
            for _ in range(index):
                if current is not None:
                    current = current.next
        else:
            current = self.tail
            for _ in range(self._size - 1 - index):
                if current is not None:
                    current = current.prev

        if current is None:
            raise IndexError("list index out of range")
        return current

    def _remove_node(self, node: Node) -> None:
        """Remove a specific node from the list."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        self._size -= 1

    # Magic methods for Python integration
    def __len__(self) -> int:
        """Return the length of the list."""
        return self._size

    def __getitem__(self, index: int) -> Any:
        """Get element by index."""
        if index < 0:
            index += self._size
        return self._get_node_at_index(index).value

    def __setitem__(self, index: int, value: Any) -> None:
        """Set element by index."""
        if index < 0:
            index += self._size
        self._get_node_at_index(index).value = value

    def __delitem__(self, index: int) -> None:
        """Delete element by index."""
        self.pop(index)

    def __contains__(self, value: Any) -> bool:
        """Check if value exists in list."""
        try:
            self.index(value)
            return True
        except ValueError:
            return False

    def __iter__(self) -> Iterator[Any]:
        """Forward iteration."""
        current = self.head
        while current:
            yield current.value
            current = current.next

    def __reversed__(self) -> Iterator[Any]:
        """Reverse iteration."""
        current = self.tail
        while current:
            yield current.value
            current = current.prev

    def __str__(self) -> str:
        """String representation."""
        return f"[{', '.join(str(item) for item in self)}]"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"DoublyLinkedList({list(self)})"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another list-like object."""
        if not hasattr(other, "__iter__") or not hasattr(other, "__len__"):
            return False

        if len(self) != len(other):
            return False

        return list(self) == list(other)

    def __hash__(self) -> None:  # type: ignore[override]
        """Prevent hashing (mutable object)."""
        raise TypeError("unhashable type: 'DoublyLinkedList'")

    def extend(self, iterable: Any) -> None:
        """Extend the list by appending elements from the iterable.

        Args:
            iterable: An iterable of elements to append

        Raises:
            TypeError: If iterable is not iterable
            OverflowError: If the resulting size would be too large
        """
        try:
            for item in iterable:
                if self._size >= _MAX_SAFE_SIZE:
                    raise OverflowError("List size would exceed maximum safe integer")
                self.append(item)
        except TypeError:
            raise TypeError("Argument must be iterable") from None
