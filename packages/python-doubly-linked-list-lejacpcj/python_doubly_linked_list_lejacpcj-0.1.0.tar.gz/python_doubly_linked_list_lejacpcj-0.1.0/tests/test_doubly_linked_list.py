"""
Test suite for the doubly linked list implementation.
"""
import pytest
from doubly_linked_list import DoublyLinkedList


class TestDoublyLinkedList:
    """Test cases for DoublyLinkedList."""
    
    def test_empty_list(self):
        """Test empty list behavior."""
        dll = DoublyLinkedList()
        assert len(dll) == 0
        assert dll.is_empty
        assert list(dll) == []
        
    def test_append(self):
        """Test appending elements."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        assert len(dll) == 3
        assert list(dll) == [1, 2, 3]
        assert not dll.is_empty
        
    def test_prepend(self):
        """Test prepending elements."""
        dll = DoublyLinkedList()
        dll.prepend(1)
        dll.prepend(2)
        dll.prepend(3)
        
        assert len(dll) == 3
        assert list(dll) == [3, 2, 1]
        
    def test_indexing(self):
        """Test getting/setting by index."""
        dll = DoublyLinkedList()
        for i in range(5):
            dll.append(i)
            
        assert dll[0] == 0
        assert dll[4] == 4
        assert dll[-1] == 4
        assert dll[-5] == 0
        
        dll[2] = 99
        assert dll[2] == 99
        
    def test_contains(self):
        """Test membership testing."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        assert 1 in dll
        assert 2 in dll
        assert 3 in dll
        assert 4 not in dll
        
    def test_remove(self):
        """Test removing elements."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        dll.remove(2)
        assert list(dll) == [1, 3]
        assert len(dll) == 2
        
        with pytest.raises(ValueError):
            dll.remove(99)
            
    def test_pop(self):
        """Test popping elements."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        assert dll.pop() == 3
        assert dll.pop(0) == 1
        assert list(dll) == [2]
        
    def test_reverse_iteration(self):
        """Test reverse iteration."""
        dll = DoublyLinkedList()
        for i in range(5):
            dll.append(i)
            
        assert list(reversed(dll)) == [4, 3, 2, 1, 0]
        
    def test_copy(self):
        """Test copying."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        dll_copy = dll.copy()
        assert list(dll_copy) == [1, 2, 3]
        assert dll_copy is not dll
        
    def test_reverse(self):
        """Test in-place reversal."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        dll.reverse()
        assert list(dll) == [3, 2, 1]
        
    def test_insert(self):
        """Test insertion at specific positions."""
        dll = DoublyLinkedList()
        dll.insert(0, 1)  # Insert at beginning
        dll.insert(1, 3)  # Insert at end
        dll.insert(1, 2)  # Insert in middle
        
        assert list(dll) == [1, 2, 3]
        
    def test_index_and_count(self):
        """Test index and count methods."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(2)
        dll.append(3)
        
        assert dll.index(2) == 1
        assert dll.count(2) == 2
        assert dll.count(1) == 1
        
        with pytest.raises(ValueError):
            dll.index(99)
            
    def test_clear(self):
        """Test clearing the list."""
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        
        dll.clear()
        assert len(dll) == 0
        assert dll.is_empty
        assert list(dll) == []
