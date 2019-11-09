import numpy as np

from EllipticGroup import *


group = EllipticGroup(0, 1, 73)

print(group.elements)
e = group.elements[0]
print(4*e)

# def exchange():
