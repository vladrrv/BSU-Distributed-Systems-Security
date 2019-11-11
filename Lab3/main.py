import numpy as np

from EllipticGroup import *


def find_c(g):
    c = 2
    while g*c != g.group.zero:
        # print(c, end='\r')
        c += 1
    return c


def find_g(group):
    for g in group.elements:
        c = find_c(g)
        if is_prime(c) and c >= group.M:
            return g, c
    raise RuntimeError('G not found')


def h(m):
    return hash(m)


def exchange(group):
    # ----- EXAMPLE FROM PAPER - WORKING WELL ------
    # group = EllipticGroup(0, -4, 211)
    # print(group)
    # n_a = 121
    # n_b = 203
    # g, c = group[2], 241
    # ----------------------------------------------
    print('Key Exchange')
    g, c = find_g(group)
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
    print('-'*20)


def ecdsa_sign(m, n_a, g, q):
    s = 0
    while s == 0:
        r = 0
        while r == 0:
            k = np.random.randint(1, q)
            kg = k*g
            r = kg.x % q
        s = (((h(m) + n_a*r) % q) * (pow(k, phi(q)-1, q))) % q
    return r, s


def ecdsa_check(m, p_a, g, q, signature):
    r, s = signature
    if max(r, s) >= q or min(r, s) < 1:
        return False
    w = pow(s, phi(q)-1, q)
    u1 = (h(m)*w) % q
    u2 = (r*w) % q
    ug_up = u1*g + u2*p_a
    r_ = ug_up.x % q
    return r == r_


def main():

    group = EllipticGroup(23, 41, 73)
    print(group)

    exchange(group)

    # m = 'bsdfbsa4fgtn'
    # g, q = find_g(group)
    # n_a = np.random.randint(1, group.M)
    # p_a = n_a*g
    # print(f'G: {g}, q: {q}, n_a: {n_a}, P_a: {p_a}')
    # signature = ecdsa_sign(m, n_a, g, q)
    # is_valid = ecdsa_check(m, p_a, g, q, signature)
    #
    # print(signature, is_valid)


if __name__ == "__main__":
    main()
