"""
Example usage of the DoublyLinkedList class.

This module demonstrates various ways to use the doubly linked list
implementation with practical examples.
"""

from doubly_linked_list import DoublyLinkedList


def basic_usage_example():
    """Demonstrate basic list operations."""
    print("=== Basic Usage Example ===")
    
    # Create a new list
    dll = DoublyLinkedList()
    print(f"Empty list: {dll}")
    print(f"Is empty: {dll.is_empty}")
    
    # Add elements
    dll.append(1)
    dll.append(2)
    dll.append(3)
    print(f"After appending 1, 2, 3: {dll}")
    
    # Prepend elements
    dll.prepend(0)
    print(f"After prepending 0: {dll}")
    
    # Access elements
    print(f"First element (index 0): {dll[0]}")
    print(f"Last element (index -1): {dll[-1]}")
    
    # Check length and membership
    print(f"Length: {len(dll)}")
    print(f"Contains 2: {2 in dll}")
    print(f"Contains 5: {5 in dll}")


def iteration_example():
    """Demonstrate different ways to iterate."""
    print("\n=== Iteration Example ===")
    
    dll = DoublyLinkedList()
    for i in range(1, 6):
        dll.append(i)
    
    print(f"List: {dll}")
    
    # Forward iteration
    print("Forward iteration:")
    for item in dll:
        print(f"  {item}")
    
    # Reverse iteration
    print("Reverse iteration:")
    for item in reversed(dll):
        print(f"  {item}")


def modification_example():
    """Demonstrate list modification operations."""
    print("\n=== Modification Example ===")
    
    dll = DoublyLinkedList()
    for i in range(1, 6):
        dll.append(i)
    
    print(f"Original list: {dll}")
    
    # Insert at specific position
    dll.insert(2, 99)
    print(f"After inserting 99 at index 2: {dll}")
    
    # Remove by value
    dll.remove(99)
    print(f"After removing 99: {dll}")
    
    # Pop elements
    last = dll.pop()
    print(f"Popped last element: {last}")
    print(f"List after pop: {dll}")
    
    first = dll.pop(0)
    print(f"Popped first element: {first}")
    print(f"List after pop(0): {dll}")
    
    # Modify by index
    dll[1] = 100
    print(f"After setting index 1 to 100: {dll}")


def search_and_count_example():
    """Demonstrate search and count operations."""
    print("\n=== Search and Count Example ===")
    
    dll = DoublyLinkedList()
    elements = [1, 2, 2, 3, 2, 4, 5]
    for elem in elements:
        dll.append(elem)
    
    print(f"List: {dll}")
    
    # Find index of elements
    print(f"Index of first 2: {dll.index(2)}")
    print(f"Count of 2: {dll.count(2)}")
    print(f"Count of 1: {dll.count(1)}")
    print(f"Count of 99: {dll.count(99)}")


def advanced_operations_example():
    """Demonstrate advanced operations."""
    print("\n=== Advanced Operations Example ===")
    
    dll = DoublyLinkedList()
    for i in range(1, 6):
        dll.append(i)
    
    print(f"Original list: {dll}")
    
    # Copy the list
    dll_copy = dll.copy()
    print(f"Copied list: {dll_copy}")
    print(f"Are they the same object? {dll is dll_copy}")
    
    # Reverse the original
    dll.reverse()
    print(f"Original after reverse: {dll}")
    print(f"Copy unchanged: {dll_copy}")
    
    # Clear a list
    dll_copy.clear()
    print(f"Copy after clear: {dll_copy}")
    print(f"Copy is empty: {dll_copy.is_empty}")


def performance_comparison():
    """Compare with Python's built-in list for some operations."""
    print("\n=== Performance Notes ===")
    
    dll = DoublyLinkedList()
    python_list = []
    
    # Both have O(1) append
    dll.append(1)
    python_list.append(1)
    
    # DoublyLinkedList has O(1) prepend, list has O(n)
    dll.prepend(0)
    python_list.insert(0, 0)  # O(n) operation
    
    print("DoublyLinkedList advantages:")
    print("- O(1) prepend operation")
    print("- O(1) append operation") 
    print("- Bidirectional iteration")
    print("- Memory efficient for frequent insertions/deletions")
    
    print("\nPython list advantages:")
    print("- O(1) random access by index")
    print("- Better cache locality")
    print("- Native C implementation")


if __name__ == "__main__":
    """Run all examples."""
    basic_usage_example()
    iteration_example()
    modification_example()
    search_and_count_example()
    advanced_operations_example()
    performance_comparison()
