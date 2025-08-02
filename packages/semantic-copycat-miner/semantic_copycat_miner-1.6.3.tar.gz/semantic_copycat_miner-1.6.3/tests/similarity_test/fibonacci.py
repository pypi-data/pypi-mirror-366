#!/usr/bin/env python3
"""
Python Fibonacci Implementation - Mathematical Sequence
Time Complexity: O(2^n) recursive, O(n) iterative
"""

def fibonacci_recursive(n):
    """Classic recursive fibonacci with exponential time"""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def fibonacci_iterative(n):
    """Iterative fibonacci with linear time"""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b

def fibonacci_memoized(n, memo={}):
    """Memoized fibonacci with linear time and space"""
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]

# Test data
n = 10
print(f"Fibonacci({n}) = {fibonacci_iterative(n)}")