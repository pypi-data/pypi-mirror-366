#!/usr/bin/env python3
"""
Python Quicksort Implementation - Divide and Conquer Algorithm
Time Complexity: O(n log n) average, O(n²) worst case
"""

def quicksort(arr):
    """Main quicksort function using divide-and-conquer strategy"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

def partition(arr, low, high):
    """Partition function for in-place quicksort"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quicksort_inplace(arr, low=0, high=None):
    """In-place quicksort implementation"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)

# Test data
test_array = [64, 34, 25, 12, 22, 11, 90]
result = quicksort(test_array.copy())
print(f"Sorted: {result}")