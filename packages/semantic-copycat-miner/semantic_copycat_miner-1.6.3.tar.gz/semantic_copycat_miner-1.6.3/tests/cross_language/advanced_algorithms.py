#!/usr/bin/env python3
"""
Advanced algorithms with mathematical invariants and complexity for testing CopycatM.
Includes cryptographic and proprietary-style implementations for IP analysis.
"""

import math
import random
from typing import List, Tuple, Optional

def rsa_key_generation(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    RSA key generation algorithm with mathematical invariants.
    
    Mathematical invariants:
    - n = p * q (where p, q are primes)
    - φ(n) = (p-1) * (q-1) (Euler's totient function)
    - e * d ≡ 1 (mod φ(n)) (modular inverse relationship)
    - gcd(e, φ(n)) = 1 (e must be coprime to φ(n))
    """
    # Calculate n = p * q
    n = p * q
    
    # Calculate Euler's totient function φ(n) = (p-1)(q-1)
    phi_n = (p - 1) * (q - 1)
    
    # Choose e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1
    e = 65537  # Common choice, prime and coprime to most φ(n)
    if math.gcd(e, phi_n) != 1:
        # Find alternative e
        for candidate in range(3, phi_n, 2):
            if math.gcd(candidate, phi_n) == 1:
                e = candidate
                break
    
    # Calculate d ≡ e^(-1) (mod φ(n)) using extended Euclidean algorithm
    d = extended_gcd(e, phi_n)[1]
    if d < 0:
        d += phi_n
    
    # Invariant verification: e * d ≡ 1 (mod φ(n))
    assert (e * d) % phi_n == 1, "RSA key generation invariant violated"
    
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm with mathematical invariants.
    
    Mathematical invariants:
    - At each step: gcd(a, b) = gcd(b, a mod b)
    - Bézout's identity: ax + by = gcd(a, b)
    - Loop invariant: gcd(original_a, original_b) = gcd(old_a, old_b) at each iteration
    """
    if a == 0:
        return b, 0, 1
    
    # Recursive case maintaining invariant
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Calculate current coefficients
    x = y1 - (b // a) * x1
    y = x1
    
    # Invariant: a * x + b * y = gcd(a, b)
    assert a * x + b * y == gcd, "Extended GCD invariant violated"
    
    return gcd, x, y

def fast_matrix_exponentiation(matrix: List[List[int]], n: int) -> List[List[int]]:
    """
    Fast matrix exponentiation using binary exponentiation.
    
    Mathematical invariants:
    - Matrix multiplication is associative: (AB)C = A(BC)
    - For Fibonacci: [[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]]
    - Exponentiation by squaring: a^(2k) = (a^k)^2, a^(2k+1) = a * (a^k)^2
    """
    if n == 0:
        # Return identity matrix
        size = len(matrix)
        identity = [[0] * size for _ in range(size)]
        for i in range(size):
            identity[i][i] = 1
        return identity
    
    if n == 1:
        return matrix
    
    # Binary exponentiation with invariant preservation
    if n % 2 == 0:
        # Even exponent: A^(2k) = (A^k)^2
        half_power = fast_matrix_exponentiation(matrix, n // 2)
        return matrix_multiply(half_power, half_power)
    else:
        # Odd exponent: A^(2k+1) = A * (A^k)^2
        half_power = fast_matrix_exponentiation(matrix, n // 2)
        half_squared = matrix_multiply(half_power, half_power)
        return matrix_multiply(matrix, half_squared)

def matrix_multiply(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
    """
    Matrix multiplication with dimension invariants.
    
    Mathematical invariants:
    - Result dimensions: (m×n) × (n×p) = (m×p)
    - Each element c[i][j] = Σ(k=0 to n-1) a[i][k] * b[k][j]
    """
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    
    # Dimension compatibility invariant
    assert cols_a == rows_b, f"Matrix multiplication dimension mismatch: {cols_a} != {rows_b}"
    
    result = [[0] * cols_b for _ in range(rows_a)]
    
    for i in range(rows_a):
        for j in range(cols_b):
            # Mathematical invariant: dot product computation
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    
    return result

def fibonacci_fast(n: int) -> int:
    """
    Fast Fibonacci using matrix exponentiation - proprietary optimization technique.
    
    Mathematical invariants:
    - F(n) = F(n-1) + F(n-2) (Fibonacci recurrence relation)
    - [[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]]
    - Golden ratio relationship: lim(n→∞) F(n+1)/F(n) = φ = (1+√5)/2
    """
    if n <= 1:
        return n
    
    # Matrix representation of Fibonacci recurrence
    fib_matrix = [[1, 1], [1, 0]]
    
    # Fast exponentiation
    result_matrix = fast_matrix_exponentiation(fib_matrix, n)
    
    # Extract F(n) from result matrix
    fibonacci_n = result_matrix[0][1]
    
    # Verification invariant (for small n)
    if n < 50:  # Avoid overflow for verification
        expected = fibonacci_slow(n)
        assert fibonacci_n == expected, f"Fast Fibonacci invariant failed for n={n}"
    
    return fibonacci_n

def fibonacci_slow(n: int) -> int:
    """Slow Fibonacci for invariant verification."""
    if n <= 1:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)

def miller_rabin_primality_test(n: int, k: int = 10) -> bool:
    """
    Miller-Rabin probabilistic primality test - cryptographically significant.
    
    Mathematical invariants:
    - For odd n-1 = d * 2^r where d is odd
    - For each witness a: either a^d ≡ 1 (mod n) or a^(d*2^i) ≡ -1 (mod n) for some i
    - Probability of error ≤ (1/4)^k for k rounds
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as d * 2^r
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Invariant: n - 1 = d * 2^r where d is odd
    assert d * (2 ** r) == n - 1, "Miller-Rabin decomposition invariant failed"
    assert d % 2 == 1, "d must be odd in Miller-Rabin"
    
    # Perform k rounds of testing
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)  # a^d mod n
        
        if x == 1 or x == n - 1:
            continue
        
        # Check a^(d*2^i) mod n for i = 1, 2, ..., r-1
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True

def elliptic_curve_point_addition(p1: Tuple[int, int], p2: Tuple[int, int], 
                                 a: int, b: int, prime: int) -> Tuple[int, int]:
    """
    Elliptic curve point addition - cryptographically valuable IP.
    
    Mathematical invariants:
    - Curve equation: y² ≡ x³ + ax + b (mod prime)
    - Point addition is commutative: P + Q = Q + P
    - Point addition is associative: (P + Q) + R = P + (Q + R)
    - Identity element: P + O = P (where O is point at infinity)
    - Inverse: P + (-P) = O
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # Verify points are on the curve
    assert (y1 * y1) % prime == (x1 * x1 * x1 + a * x1 + b) % prime, "Point 1 not on curve"
    assert (y2 * y2) % prime == (x2 * x2 * x2 + a * x2 + b) % prime, "Point 2 not on curve"
    
    if x1 == x2:
        if y1 == y2:
            # Point doubling: P + P = 2P
            # λ = (3x₁² + a) / (2y₁)
            numerator = (3 * x1 * x1 + a) % prime
            denominator = (2 * y1) % prime
            lambda_val = (numerator * pow(denominator, prime - 2, prime)) % prime
        else:
            # Points are inverses: P + (-P) = O (point at infinity)
            return None  # Represents point at infinity
    else:
        # General case: P + Q where P ≠ Q
        # λ = (y₂ - y₁) / (x₂ - x₁)
        numerator = (y2 - y1) % prime
        denominator = (x2 - x1) % prime
        lambda_val = (numerator * pow(denominator, prime - 2, prime)) % prime
    
    # Calculate result point
    x3 = (lambda_val * lambda_val - x1 - x2) % prime
    y3 = (lambda_val * (x1 - x3) - y1) % prime
    
    # Verify result is on curve (invariant)
    assert (y3 * y3) % prime == (x3 * x3 * x3 + a * x3 + b) % prime, "Result point not on curve"
    
    return (x3, y3)

def proprietary_hash_function(data: bytes, rounds: int = 64) -> int:
    """
    Proprietary hash function with trade secret implementation.
    
    This represents a commercially valuable, potentially patented algorithm
    with specific mathematical properties and transformation resistance.
    """
    # Initialize with proprietary constants (hypothetically trade secrets)
    h0 = 0x6a09e667f3bcc908  # Proprietary initialization vector
    h1 = 0xbb67ae8584caa73b  # Based on mathematical constants
    
    # Proprietary mixing constants
    K = [0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc]
    
    # Process data in proprietary chunks
    hash_value = h0
    
    for round_num in range(rounds):
        # Proprietary transformation with mathematical invariants
        for i, byte_val in enumerate(data):
            # Complex bit manipulation maintaining avalanche effect
            temp = hash_value ^ (byte_val << (i % 32))
            temp = ((temp << 13) | (temp >> (64 - 13))) & 0xffffffffffffffff  # Rotate left 13
            temp ^= K[round_num % len(K)]
            temp = temp ^ (temp >> 17)  # XOR shift
            temp = temp * 0x5bd1e995  # Multiply by prime-like constant
            temp = temp ^ (temp >> 15)  # Final XOR shift
            
            hash_value = temp & 0xffffffffffffffff
        
        # Round-specific transformation (mathematical complexity)
        hash_value = (hash_value + h1) & 0xffffffffffffffff
        hash_value = ((hash_value << 7) | (hash_value >> 57)) & 0xffffffffffffffff
    
    return hash_value & 0xffffffffffffffff

if __name__ == "__main__":
    print("=== Advanced Algorithm Testing ===")
    
    # Test RSA key generation
    print("Testing RSA key generation...")
    pub_key, priv_key = rsa_key_generation(61, 53)  # Small primes for testing
    print(f"Public key: {pub_key}")
    print(f"Private key: {priv_key}")
    
    # Test fast Fibonacci
    print("\nTesting fast Fibonacci...")
    fib_30 = fibonacci_fast(30)
    print(f"Fibonacci(30) = {fib_30}")
    
    # Test primality
    print("\nTesting Miller-Rabin primality...")
    is_prime = miller_rabin_primality_test(1009)  # Known prime
    print(f"1009 is prime: {is_prime}")
    
    # Test elliptic curve (using curve y² = x³ + 7 mod 17)
    print("\nTesting elliptic curve point addition...")
    try:
        result = elliptic_curve_point_addition((5, 1), (6, 3), 0, 7, 17)
        print(f"Point addition result: {result}")
    except AssertionError as e:
        print(f"Curve operation failed: {e}")
    
    # Test proprietary hash
    print("\nTesting proprietary hash function...")
    test_data = b"Hello, World!"
    hash_result = proprietary_hash_function(test_data)
    print(f"Proprietary hash: 0x{hash_result:016x}")