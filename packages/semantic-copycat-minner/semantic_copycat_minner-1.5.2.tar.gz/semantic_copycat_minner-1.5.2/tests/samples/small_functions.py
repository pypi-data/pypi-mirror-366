"""
Test file containing small functions for mathematical invariant testing.
"""

def add_numbers(a, b):
    """Simple addition function."""
    return a + b

def multiply_numbers(x, y):
    """Simple multiplication function."""
    return x * y

def calculate_factorial(n):
    """Calculate factorial for small numbers."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def fibonacci_simple(n):
    """Simple Fibonacci implementation."""
    if n <= 1:
        return n
    return fibonacci_simple(n - 1) + fibonacci_simple(n - 2)

def is_prime(num):
    """Check if a number is prime."""
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def gcd(a, b):
    """Calculate greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Calculate least common multiple."""
    return abs(a * b) // gcd(a, b)

def power(base, exponent):
    """Calculate power using recursion."""
    if exponent == 0:
        return 1
    elif exponent == 1:
        return base
    elif exponent % 2 == 0:
        half_power = power(base, exponent // 2)
        return half_power * half_power
    else:
        return base * power(base, exponent - 1) 