import numpy as np
from hashlib import sha256

from elliptic_group import *


def print_header(header, w=21):
    print('='*w)
    print(header.center(w))
    print('-'*w)


def exchange(group):
    print_header('Key Exchange')

    g, c = group.find_g()
    print(f'G: {g}, c: {c}')

    n_a = np.random.randint(1, group.M)
    n_b = np.random.randint(1, group.M)
    print(f'n_A: {n_a}\nn_B: {n_b}')

    p_a = n_a*g
    p_b = n_b*g
    print(f'p_A: {p_a}\np_B: {p_b}')

    ka = n_a * p_b
    kb = n_b * p_a
    print(f'K_A: {ka}\nK_B: {kb}')


def ecdsa_sign(m, h, n_a, g, q):
    s = 0
    while s == 0:
        r = 0
        while r == 0:
            k = np.random.randint(1, q)
            kg = k*g
            r = kg.x % q
        s = (((h(m) + n_a*r) % q) * (pow(k, phi(q)-1, q))) % q
    return r, s


def ecdsa_check(m, h, p_a, g, q, signature):
    r, s = signature
    if max(r, s) >= q or min(r, s) < 1:
        return False
    w = pow(s, phi(q)-1, q)
    u1 = (h(m)*w) % q
    u2 = (r*w) % q
    ug_up = u1*g + u2*p_a
    r_ = ug_up.x % q
    return r == r_


def ecdsa(group):
    print_header('ECDSA')

    m = 'bsdfbsa4fgtn'
    print(f'Message: {m}')

    g, q = group.find_g()
    n_a = np.random.randint(1, group.M)
    p_a = n_a*g
    print(f'G: {g}, q: {q}')
    print(f'n_A: {n_a}\nP_A: {p_a}')

    def h(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        hashed = int.from_bytes(sha256(data).digest(), 'big')
        return hashed

    signature = ecdsa_sign(m, h, n_a, g, q)
    print(f'Signature: {signature}')

    is_valid = ecdsa_check(m, h, p_a, g, q, signature)
    print(f'Check: {is_valid}')


def main():
    M = 73
    # gen = EllipticGroup.generate_good_ab(M, progress=True)
    # a, b = next(gen)
    # print(a, b)
    # a, b = next(gen)
    # print(a, b)

    a = 1
    b = 13  # 60
    group = EllipticGroup(a, b, M)
    print(group)

    np.random.seed(42)

    exchange(group)
    ecdsa(group)


if __name__ == "__main__":
    main()
