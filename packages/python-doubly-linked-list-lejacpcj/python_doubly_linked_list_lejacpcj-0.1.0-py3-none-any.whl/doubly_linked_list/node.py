"""
Node class for doubly linked list implementation.
"""

from typing import Any, Optional


class Node:
    """
    A node in a doubly linked list.

    Attributes:
        value: The data stored in the node
        next: Reference to the next node
        prev: Reference to the previous node
    """

    __slots__ = (
        "value",
        "next",
        "prev",
    )  # Memory optimization and attribute protection

    def __init__(self, value: Any) -> None:
        """
        Initialize a new node.

        Args:
            value: The value to store in the node
        """
        self.value = value
        self.next: Optional["Node"] = None
        self.prev: Optional["Node"] = None

    def __repr__(self) -> str:
        """Return string representation of the node."""
        # Prevent potential information leakage in repr
        try:
            value_repr = repr(self.value)
            # Truncate very long representations
            if len(value_repr) > 50:
                value_repr = value_repr[:47] + "..."
            return f"Node({value_repr})"
        except Exception:
            return "Node(<unprintable>)"
