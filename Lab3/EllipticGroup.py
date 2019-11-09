import numpy as np


def phi(n):
    return int(np.sum(np.gcd(n, np.arange(1,n+1)) == 1))


def sqrt(x, M):
    roots = []
    for i in range(1,M):
        if i**2 % M == x:
            roots.append(i)
    return roots


class Element:
    def __init__(self, group, x, y):
        self.group = group
        self.x = x % group.M
        self.y = y % group.M

    def __add__(self, other):
        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y
        M, a = self.group.M, self.group.a
        l = (((3*x1**2+a) % M)*pow(2*y1, phi(M)-1, M)) % M if self.__eq__(other) else (((y2-y1) % M)*pow(x2-x1, phi(M)-1, M)) % M
        x3 = (l**2-x1-x2) % M
        y3 = (l*(x1-x3)-y1) % M
        return Element(self.group, x3, y3)

    def __mul__(self, other):
        assert isinstance(other, int)
        res = self
        for _ in range(other-1):
            res = res + self
        return res

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class EllipticGroup:

    def __init__(self, a, b, M):
        self.a = a
        self.b = b
        self.M = M
        self.elements = []
        f = lambda x: (x**3+a*x+b) % M
        for x in range(1,M):
            roots = sqrt(f(x), M)
            for y in roots:
                self.elements.append(Element(self, x, y))
