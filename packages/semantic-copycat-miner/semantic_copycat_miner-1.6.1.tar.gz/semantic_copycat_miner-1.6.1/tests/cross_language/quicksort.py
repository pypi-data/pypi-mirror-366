#!/usr/bin/env python3
"""
Cross-language quicksort implementation for testing algorithm detection consistency.
"""

def quicksort(arr):
    """
    Quicksort algorithm implementation.
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def huffman_encode(data):
    """
    Simple Huffman encoding implementation.
    """
    if not data:
        return "", {}
    
    # Count frequencies
    freq = {}
    for char in data:
        freq[char] = freq.get(char, 0) + 1
    
    # Build Huffman tree (simplified)
    codes = {}
    if len(freq) == 1:
        codes[list(freq.keys())[0]] = "0"
    else:
        # Simple binary assignment for demo
        items = sorted(freq.items(), key=lambda x: x[1])
        for i, (char, _) in enumerate(items):
            codes[char] = format(i, f'0{len(items).bit_length()}b')
    
    # Encode data
    encoded = ""
    for char in data:
        encoded += codes[char]
    
    return encoded, codes


if __name__ == "__main__":
    # Test quicksort
    test_arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    sorted_arr = quicksort(test_arr)
    print(f"Sorted: {sorted_arr}")
    
    # Test huffman
    test_str = "hello world"
    encoded, codes = huffman_encode(test_str)
    print(f"Encoded: {encoded}")
    print(f"Codes: {codes}")