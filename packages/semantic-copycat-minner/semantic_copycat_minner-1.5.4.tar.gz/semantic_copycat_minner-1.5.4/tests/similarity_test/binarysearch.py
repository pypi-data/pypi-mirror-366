#!/usr/bin/env python3
"""
Python Binary Search Implementation - Divide and Conquer Search
Time Complexity: O(log n)
"""

def binary_search(arr, target):
    """Iterative binary search implementation"""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def binary_search_recursive(arr, target, left=0, right=None):
    """Recursive binary search implementation"""
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

# Test data
sorted_array = [11, 12, 22, 25, 34, 64, 90]
target = 25
result = binary_search(sorted_array, target)
print(f"Found {target} at index: {result}")