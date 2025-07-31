import numpy as np
from scipy.optimize import fsolve

with open("derivatives.txt", "r") as file2:
    eq1 = file2.readline()
    eq2 = file2.readline()

def system(vars):
    x, y = vars 
    return [eval(eq1), eval(eq2)]

guesses = [[1,1], [0,-1], [-1,0], [-1,-1], [0,0]]
solutions = [fsolve(system, g) for g in guesses]

with open("points.txt", "w") as file:
    for sol in solutions:
        file.write(f"{sol[0]:.2f}\n")
        file.write(f"{sol[1]:.2f}\n")
