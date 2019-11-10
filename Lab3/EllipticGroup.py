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


class Element:
    def __init__(self, group, x, y):
        self.group = group
        self.x = x % group.M
        self.y = y % group.M

    def __add__(self, other):
        assert isinstance(other, Element)
        assert self.group == other.group

        zero = self.group.zero
        if self == -other:
            return zero
        if self == zero:
            return other
        if other == zero:
            return self

        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y
        M, a = self.group.M, self.group.a
        if self == other:
            l = (((3 * x1**2 + a) % M) * pow((2*y1) % M, phi(M) - 1, M)) % M
        else:
            l = (((y2 - y1) % M) * pow((x2-x1) % M, phi(M) - 1, M)) % M
        x3 = (l**2 - x1 - x2) % M
        y3 = (l*(x1 - x3) - y1) % M
        return Element(self.group, x3, y3)

    def __sub__(self, other):
        assert isinstance(other, Element)
        assert self.group == other.group
        return self + (-other)

    def __mul__(self, other):
        assert isinstance(other, int)
        if other == 0:
            return self.group.zero
        res = Element(self.group, self.x, self.y)
        for _ in range(abs(other) - 1):
            res = res + self
        if other < 0:
            res = -res
        return res

    def __neg__(self):
        return Element(self.group, self.x, ((-self.y) % self.group.M))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other is None:
            return False
        assert self.group == other.group
        return self.x == other.x and self.y == other.y


class EllipticGroup:

    def __init__(self, a, b, M):
        self.a = a
        self.b = b
        self.M = M
        self.elements = []
        self.zero = None
        f = lambda x: (x**3 + a*x + b) % M
        for x in range(1, M):
            roots = sqrt(f(x), M)
            for y in roots:
                e = Element(self, x, y)
                if y == (-y) % M:
                    self.zero = e
                self.elements.append(e)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.M == other.M
