"""
Algorithm patterns for CopycatM.
"""

from typing import Dict, Any, List


def get_algorithm_patterns() -> Dict[str, Any]:
    """Get known algorithm patterns for detection."""
    return {
        "sorting": {
            "quicksort": {
                "patterns": ["partition", "recursive", "pivot"],
                "confidence": 0.9,
                "complexity": "O(n log n)",
                "signatures": [
                    "def partition",
                    "def quicksort", 
                    "pivot = arr",
                    "left = [x for x in arr if x < pivot]",
                    "right = [x for x in arr if x > pivot]"
                ]
            },
            "mergesort": {
                "patterns": ["merge", "divide", "recursive"],
                "confidence": 0.85,
                "complexity": "O(n log n)",
                "signatures": [
                    "def merge",
                    "def mergesort",
                    "mid = len(arr) // 2",
                    "left = arr[:mid]",
                    "right = arr[mid:]"
                ]
            },
            "bubblesort": {
                "patterns": ["swap", "nested_loops"],
                "confidence": 0.8,
                "complexity": "O(n²)",
                "signatures": [
                    "for i in range(len(arr))",
                    "for j in range(len(arr) - 1)",
                    "if arr[j] > arr[j + 1]",
                    "arr[j], arr[j + 1] = arr[j + 1], arr[j]"
                ]
            },
            "heapsort": {
                "patterns": ["heapify", "heap", "extract"],
                "confidence": 0.85,
                "complexity": "O(n log n)",
                "signatures": [
                    "def heapify",
                    "def heapsort",
                    "largest = i",
                    "left = 2 * i + 1",
                    "right = 2 * i + 2"
                ]
            }
        },
        "searching": {
            "binary_search": {
                "patterns": ["midpoint", "divide", "sorted"],
                "confidence": 0.9,
                "complexity": "O(log n)",
                "signatures": [
                    "def binary_search",
                    "left = 0",
                    "right = len(arr) - 1",
                    "mid = (left + right) // 2",
                    "if arr[mid] == target"
                ]
            },
            "linear_search": {
                "patterns": ["loop", "comparison"],
                "confidence": 0.7,
                "complexity": "O(n)",
                "signatures": [
                    "for i in range(len(arr))",
                    "if arr[i] == target",
                    "return i"
                ]
            },
            "depth_first_search": {
                "patterns": ["stack", "recursive", "visited"],
                "confidence": 0.85,
                "complexity": "O(V + E)",
                "signatures": [
                    "def dfs",
                    "visited = set()",
                    "stack = [start]",
                    "while stack",
                    "node = stack.pop()"
                ]
            },
            "breadth_first_search": {
                "patterns": ["queue", "level", "visited"],
                "confidence": 0.85,
                "complexity": "O(V + E)",
                "signatures": [
                    "def bfs",
                    "visited = set()",
                    "queue = [start]",
                    "while queue",
                    "node = queue.pop(0)"
                ]
            }
        },
        "graph": {
            "dijkstra": {
                "patterns": ["priority_queue", "distance", "shortest_path"],
                "confidence": 0.9,
                "complexity": "O((V + E) log V)",
                "signatures": [
                    "def dijkstra",
                    "distances = {node: float('inf')",
                    "priority_queue = [(0, start)]",
                    "current_distance, current = heapq.heappop(priority_queue)"
                ]
            },
            "bellman_ford": {
                "patterns": ["relaxation", "negative_cycles"],
                "confidence": 0.85,
                "complexity": "O(VE)",
                "signatures": [
                    "def bellman_ford",
                    "distances = {node: float('inf')",
                    "for _ in range(V - 1)",
                    "for u, v, weight in edges"
                ]
            },
            "kruskal": {
                "patterns": ["union_find", "minimum_spanning_tree"],
                "confidence": 0.85,
                "complexity": "O(E log E)",
                "signatures": [
                    "def kruskal",
                    "edges.sort(key=lambda x: x[2])",
                    "parent = list(range(V))",
                    "def find(x)",
                    "def union(x, y)"
                ]
            }
        },
        "dynamic_programming": {
            "fibonacci": {
                "patterns": ["memoization", "recursive"],
                "confidence": 0.8,
                "complexity": "O(n)",
                "signatures": [
                    "def fibonacci",
                    "if n <= 1",
                    "return n",
                    "memo = {}",
                    "if n in memo"
                ]
            },
            "longest_common_subsequence": {
                "patterns": ["2d_array", "matching"],
                "confidence": 0.85,
                "complexity": "O(mn)",
                "signatures": [
                    "def lcs",
                    "dp = [[0] * (n + 1) for _ in range(m + 1)]",
                    "for i in range(1, m + 1)",
                    "for j in range(1, n + 1)"
                ]
            },
            "knapsack": {
                "patterns": ["weight", "value", "capacity"],
                "confidence": 0.85,
                "complexity": "O(nW)",
                "signatures": [
                    "def knapsack",
                    "dp = [[0] * (W + 1) for _ in range(n + 1)]",
                    "for i in range(1, n + 1)",
                    "for w in range(W + 1)"
                ]
            }
        },
        "string": {
            "kmp": {
                "patterns": ["pattern_matching", "failure_function"],
                "confidence": 0.9,
                "complexity": "O(m + n)",
                "signatures": [
                    "def kmp",
                    "def compute_lps",
                    "lps = [0] * len(pattern)",
                    "i = j = 0"
                ]
            },
            "rabin_karp": {
                "patterns": ["rolling_hash", "hash_function"],
                "confidence": 0.85,
                "complexity": "O(m + n)",
                "signatures": [
                    "def rabin_karp",
                    "pattern_hash = hash(pattern)",
                    "window_hash = hash(text[:len(pattern)])",
                    "for i in range(len(text) - len(pattern) + 1)"
                ]
            }
        }
    }


def get_pattern_by_name(name: str) -> Dict[str, Any]:
    """Get a specific algorithm pattern by name."""
    patterns = get_algorithm_patterns()
    
    for category in patterns.values():
        if name in category:
            return category[name]
    
    return {}


def get_patterns_by_category(category: str) -> Dict[str, Any]:
    """Get all patterns in a specific category."""
    patterns = get_algorithm_patterns()
    return patterns.get(category, {})


def get_all_pattern_names() -> List[str]:
    """Get all available pattern names."""
    patterns = get_algorithm_patterns()
    names = []
    
    for category in patterns.values():
        names.extend(category.keys())
    
    return names 