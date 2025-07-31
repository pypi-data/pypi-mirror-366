"""
Enhanced security and robustness tests for the doubly linked list implementation.
"""
import pytest
import gc
from doubly_linked_list import DoublyLinkedList


class TestDoublyLinkedListSecurity:
    """Security-focused test cases for DoublyLinkedList."""
    
    def test_memory_leak_protection_clear(self):
        """Test that clear() properly breaks circular references."""
        dll = DoublyLinkedList()
        
        # Add elements with potential circular references
        dll.append([1, 2, 3])  # Mutable objects
        dll.append({"key": "value"})
        dll.append(dll)  # Self-reference
        
        # Force garbage collection before clear
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        dll.clear()
        gc.collect()
        
        # Should not have significantly more objects
        final_objects = len(gc.get_objects())
        assert final_objects <= initial_objects + 10  # Allow some margin
        
    def test_integer_overflow_protection(self):
        """Test protection against integer overflow attacks."""
        dll = DoublyLinkedList()
        
        # Import the constant to use the same value
        from doubly_linked_list.doubly_linked_list import _MAX_SAFE_SIZE
        
        # Mock a very large size to test overflow protection
        # Set size to maximum - 1 so the next append would exceed
        dll._size = _MAX_SAFE_SIZE
        
        # Create a minimal valid state for testing
        from doubly_linked_list.node import Node
        dummy_node = Node("dummy")
        dll.head = dll.tail = dummy_node
        
        with pytest.raises(OverflowError, match="exceed maximum safe integer"):
            dll.append("test")
            
        # Reset and test prepend
        dll._size = _MAX_SAFE_SIZE
        with pytest.raises(OverflowError, match="exceed maximum safe integer"):
            dll.prepend("test")
    
    def test_input_validation_constructor(self):
        """Test input validation in constructor."""
        # Valid cases
        dll1 = DoublyLinkedList([1, 2, 3])
        assert list(dll1) == [1, 2, 3]
        
        dll2 = DoublyLinkedList(range(5))
        assert list(dll2) == [0, 1, 2, 3, 4]
        
        # Invalid case
        with pytest.raises(TypeError, match="must be iterable"):
            DoublyLinkedList(42)  # Not iterable
    
    def test_type_validation_insert(self):
        """Test type validation for insert method."""
        dll = DoublyLinkedList()
        dll.append(1)
        
        with pytest.raises(TypeError, match="Index must be an integer"):
            dll.insert("invalid", 42)
        
        with pytest.raises(TypeError, match="Index must be an integer"):
            dll.insert(1.5, 42)
    
    def test_bounds_checking_edge_cases(self):
        """Test bounds checking for edge cases."""
        dll = DoublyLinkedList()
        
        # Test with extremely large negative index
        with pytest.raises(IndexError):
            dll[-1000000]
        
        # Test with extremely large positive index
        with pytest.raises(IndexError):
            dll[1000000]
    
    def test_node_repr_security(self):
        """Test that Node repr doesn't leak sensitive information."""
        from doubly_linked_list.node import Node
        
        # Test with very long string
        long_string = "A" * 100
        node = Node(long_string)
        repr_str = repr(node)
        assert len(repr_str) < 60  # Should be truncated
        assert "..." in repr_str
        
        # Test with unprintable object
        class UnprintableObject:
            def __repr__(self):
                raise Exception("Cannot print this")
        
        node = Node(UnprintableObject())
        repr_str = repr(node)
        assert "unprintable" in repr_str
    
    def test_equality_security(self):
        """Test equality comparisons don't cause issues."""
        dll1 = DoublyLinkedList([1, 2, 3])
        dll2 = DoublyLinkedList([1, 2, 3])
        dll3 = DoublyLinkedList([1, 2, 4])
        
        assert dll1 == dll2
        assert dll1 != dll3
        assert dll1 != "not a list"
        assert dll1 != 42
    
    def test_unhashable_type(self):
        """Test that DoublyLinkedList cannot be hashed."""
        dll = DoublyLinkedList([1, 2, 3])
        
        with pytest.raises(TypeError, match="unhashable type"):
            hash(dll)
    
    def test_extend_validation(self):
        """Test extend method with validation."""
        dll = DoublyLinkedList([1, 2, 3])
        
        # Valid extend
        dll.extend([4, 5, 6])
        assert list(dll) == [1, 2, 3, 4, 5, 6]
        
        # Invalid extend
        with pytest.raises(TypeError, match="must be iterable"):
            dll.extend(42)
    
    def test_circular_reference_handling(self):
        """Test handling of circular references in values."""
        dll = DoublyLinkedList()
        
        # Create circular reference
        circular_list = [1, 2, 3]
        circular_list.append(circular_list)
        
        dll.append(circular_list)
        dll.append("normal_value")
        
        # Should not crash when converting to string
        str_repr = str(dll)
        assert "normal_value" in str_repr
    
    def test_memory_efficiency_slots(self):
        """Test that Node uses __slots__ for memory efficiency."""
        from doubly_linked_list.node import Node
        
        node = Node("test")
        assert hasattr(Node, '__slots__')
        
        # Should not be able to add arbitrary attributes
        with pytest.raises(AttributeError):
            node.arbitrary_attribute = "should fail"


class TestDoublyLinkedListRobustness:
    """Robustness tests for edge cases and stress scenarios."""
    
    def test_large_list_operations(self):
        """Test operations on reasonably large lists."""
        dll = DoublyLinkedList()
        
        # Add 1000 elements
        for i in range(1000):
            dll.append(i)
        
        assert len(dll) == 1000
        assert dll[0] == 0
        assert dll[999] == 999
        
        # Test removal from middle
        dll.remove(500)
        assert 500 not in dll
        assert len(dll) == 999
    
    def test_mixed_type_storage(self):
        """Test storing mixed types safely."""
        dll = DoublyLinkedList()
        
        # Add various types
        dll.append(42)
        dll.append("string")
        dll.append([1, 2, 3])
        dll.append({"key": "value"})
        dll.append(None)
        dll.append(lambda x: x + 1)
        
        assert len(dll) == 6
        assert dll[0] == 42
        assert dll[1] == "string"
        assert dll[4] is None
        assert callable(dll[5])
    
    def test_stress_append_prepend(self):
        """Stress test append and prepend operations."""
        dll = DoublyLinkedList()
        
        # Alternating append and prepend
        for i in range(100):
            if i % 2 == 0:
                dll.append(i)
            else:
                dll.prepend(i)
        
        assert len(dll) == 100
        
        # Verify integrity
        count = 0
        for item in dll:
            count += 1
        assert count == 100
