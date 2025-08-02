#!/usr/bin/env python3
"""
Python Bubble Sort Implementation - Simple Comparison Sort
Time Complexity: O(n²) worst and average case
"""

def bubblesort(arr):
    """Basic bubble sort with adjacent element swapping"""
    n = len(arr)
    
    for i in range(n):
        swapped = False
        
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        if not swapped:
            break
    
    return arr

def optimized_bubblesort(arr):
    """Optimized bubble sort with early termination"""
    n = len(arr)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    return arr

# Test data
test_array = [64, 34, 25, 12, 22, 11, 90]
result = bubblesort(test_array.copy())
print(f"Sorted: {result}")