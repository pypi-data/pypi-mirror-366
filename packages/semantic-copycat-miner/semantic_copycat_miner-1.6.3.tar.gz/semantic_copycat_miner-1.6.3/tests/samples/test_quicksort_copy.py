def quicksort(arr):
    """
    Quicksort implementation for testing CopycatM.
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def binary_search(arr, target):
    """
    Binary search implementation for testing CopycatM.
    """
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


if __name__ == "__main__":
    # Test the algorithms
    test_array = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    sorted_array = quicksort(test_array)
    print(f"Original: {test_array}")
    print(f"Sorted: {sorted_array}")
    
    # Test binary search
    target = 5
    index = binary_search(sorted_array, target)
    print(f"Index of {target}: {index}") 