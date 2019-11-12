from helpers import *
from tqdm import tqdm


class EllipticGroup:

    class Element:
        def __init__(self, group):
            self.group = group

        def __neg__(self):
            raise NotImplementedError

        def __add__(self, other):
            raise NotImplementedError

        def __sub__(self, other):
            raise NotImplementedError

        def __eq__(self, other):
            raise NotImplementedError

        def __mul__(self, other):
            raise NotImplementedError

        def __rmul__(self, other):
            return self.__mul__(other)

        def __str__(self):
            raise NotImplementedError

        def __repr__(self):
            return self.__str__()

    class ZeroElement(Element):
        def __init__(self, group):
            super().__init__(group)

        def __neg__(self):
            return self

        def __add__(self, other):
            assert isinstance(other, EllipticGroup.Element)
            return other

        def __sub__(self, other):
            assert isinstance(other, EllipticGroup.Element)
            return -other

        def __mul__(self, other):
            assert isinstance(other, int)
            return self

        def __eq__(self, other):
            if other is None:
                return False
            assert self.group == other.group
            if not isinstance(other, EllipticGroup.ZeroElement):
                return False
            return True

        def __str__(self):
            return '( O )'

    class NonZeroElement(Element):
        def __init__(self, group, x, y):
            super().__init__(group)
            self.x = x % group.M
            self.y = y % group.M

        def __add__(self, other):
            assert isinstance(other, EllipticGroup.Element)
            assert self.group == other.group

            zero = self.group.zero
            if self == -other:
                return zero
            if isinstance(other, EllipticGroup.ZeroElement):
                return self

            x1, y1 = self.x, self.y
            x2, y2 = other.x, other.y
            M, a = self.group.M, self.group.a
            if self == other:
                l = (((3 * x1**2 + a) % M) * pow((2*y1) % M, M - 2, M)) % M
            else:
                l = (((y2 - y1) % M) * pow((x2-x1) % M, M - 2, M)) % M
            x3 = (l**2 - x1 - x2) % M
            y3 = (l*(x1 - x3) - y1) % M
            return EllipticGroup.NonZeroElement(self.group, x3, y3)

        def __sub__(self, other):
            assert isinstance(other, EllipticGroup.Element)
            assert self.group == other.group
            return self + (-other)

        def __mul__(self, other):
            assert isinstance(other, int)
            if other == 0:
                return self.group.zero
            res = EllipticGroup.NonZeroElement(self.group, self.x, self.y)
            for _ in range(abs(other) - 1):
                res = res + self
            if other < 0:
                res = -res
            return res

        def __neg__(self):
            return EllipticGroup.NonZeroElement(self.group, self.x, -self.y)

        def __rmul__(self, other):
            return self.__mul__(other)

        def __str__(self):
            return f'({self.x}, {self.y})'

        def __eq__(self, other):
            if other is None:
                return False
            assert isinstance(other, EllipticGroup.Element)
            assert self.group == other.group
            if isinstance(other, EllipticGroup.ZeroElement):
                return False
            return self.x == other.x and self.y == other.y

    @staticmethod
    def check_params(a, b, M):
        return (4*a**3 + 27*b**2) % M != 0

    @staticmethod
    def generate_all_ab(M):
        for a in range(M):
            for b in range(M):
                if EllipticGroup.check_params(a, b, M):
                    yield a, b

    @staticmethod
    def generate_good_ab(M, progress=False):
        all_ab = EllipticGroup.generate_all_ab(M)
        ab = next(all_ab)
        while ab is not None:
            try:
                a, b = ab
                if progress:
                    print(f'Searching for good a, b : {a}, {b}', end='\r')
                group = EllipticGroup(a, b, M)
                group.find_g()
                yield a, b
            except RuntimeError:
                pass
            ab = next(all_ab)

    def __init__(self, a, b, M):
        assert is_prime(M)
        assert EllipticGroup.check_params(a, b, M)
        self.a = a
        self.b = b
        self.M = M
        self.elements = []
        self.zero = EllipticGroup.ZeroElement(self)
        f = lambda x: (x**3 + a*x + b) % M
        for x in range(M):
            roots = sqrt(f(x), M)
            for y in roots:
                e = EllipticGroup.NonZeroElement(self, x, y)
                self.elements.append(e)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.M == other.M

    def __str__(self):
        title = f'Elliptic Group: y^2 = x^3 + {self.a}x + {self.b} (mod {self.M})'
        elements = f' Elements: {self.elements}'
        return title + '\n' + elements

    def __getitem__(self, item):
        return self.elements[item]

    def __len__(self):
        return len(self.elements)

    def find_g(self):
        for g in self.elements:
            c = 2
            while g * c != self.zero:
                # print(c, end='\r')
                c += 1
            if is_prime(c) and c >= self.M:
                return g, c
        raise RuntimeError('G not found')
