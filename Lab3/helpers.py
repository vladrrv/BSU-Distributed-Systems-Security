import numpy as np


def phi(n):
    return int(np.sum(np.gcd(n, np.arange(1, n + 1)) == 1))


def sqrt(x, M):
    roots = []
    for i in range(M):
        if (i**2) % M == x % M:
            roots.append(i)
    return roots


def is_prime(n):
    return n in prime_range(n, n+1)


def prime_range(lower=1, upper=12):
    for num in range(lower, upper):
        if num > 1:
            for i in range(2, int(np.sqrt(num)) + 1):
                if (num % i) == 0:
                    break
            else:
                yield num