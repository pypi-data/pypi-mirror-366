#!/usr/bin/env python3
"""
Python quicksort implementation for GNN testing
"""

def quicksort(arr):
    """
    Divide-and-conquer quicksort algorithm
    Time complexity: O(n log n) average, O(n²) worst case
    Space complexity: O(log n) average due to recursion
    """
    if len(arr) <= 1:
        return arr
    
    # Choose pivot (middle element)
    pivot = arr[len(arr) // 2]
    
    # Partition into three groups
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]  
    right = [x for x in arr if x > pivot]
    
    # Recursively sort and combine
    return quicksort(left) + middle + quicksort(right)

def quicksort_inplace(arr, low=0, high=None):
    """
    In-place quicksort variant for memory efficiency
    """
    if high is None:
        high = len(arr) - 1
        
    if low < high:
        # Partition and get pivot index
        pivot_index = partition(arr, low, high)
        
        # Recursively sort left and right subarrays
        quicksort_inplace(arr, low, pivot_index - 1)
        quicksort_inplace(arr, pivot_index + 1, high)

def partition(arr, low, high):
    """
    Lomuto partition scheme
    """
    pivot = arr[high]  # Choose last element as pivot
    i = low - 1  # Index of smaller element
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # Swap elements
    
    # Place pivot in correct position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Test the implementation
if __name__ == "__main__":
    test_array = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
    print(f"Original: {test_array}")
    
    # Test functional version
    sorted_arr = quicksort(test_array.copy())
    print(f"Sorted (functional): {sorted_arr}")
    
    # Test in-place version  
    inplace_arr = test_array.copy()
    quicksort_inplace(inplace_arr)
    print(f"Sorted (in-place): {inplace_arr}")