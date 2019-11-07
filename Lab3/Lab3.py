import numpy as np


def find_elements(a, b, M=73):
    f = lambda x: (x**3+a*x+b) % M
    elements = []
    for x in range(1,M):         
        y = int(np.sqrt(f(x)))
        if y > 0 and y**2 % M == f(x):
            elements.append((x,y))
    return elements

elements = find_elements(0,1)

print(elements)