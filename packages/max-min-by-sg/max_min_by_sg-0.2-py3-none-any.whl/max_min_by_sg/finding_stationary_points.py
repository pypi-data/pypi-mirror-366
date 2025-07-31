import numpy as np
from scipy.optimize import fsolve
from sympy import symbols, lambdify
from sympy import symbols, solve
x, y = symbols('x y')
with open("derivatives.txt", "r") as file2:
        eq1 = file2.readline()
        eq2 = file2.readline()
def system(vars):
    x, y = vars 
    return [eval(eq1), eval(eq2)]
initial_guess1= [1, 1]
initial_guess2= [0, -1]
initial_guess3= [-1, 0]
initial_guess4= [-1, -1]
initial_guess5= [0, 0]
solution1 = fsolve(system, initial_guess1)
solution2 = fsolve(system, initial_guess2)
solution3 = fsolve(system, initial_guess3)
solution4 = fsolve(system, initial_guess4)
solution5 = fsolve(system, initial_guess5)
with open("points.txt", "w") as file:
    file.write(f"{solution1[0]:.2f}\n")
    file.write(f"{solution1[1]:.2f}\n")
    file.write(f"{solution2[0]:.2f}\n")
    file.write(f"{solution2[1]:.2f}\n")
    file.write(f"{solution3[0]:.2f}\n")
    file.write(f"{solution3[1]:.2f}\n")
    file.write(f"{solution4[0]:.2f}\n")
    file.write(f"{solution4[1]:.2f}\n")
    file.write(f"{solution5[0]:.2f}\n")
    file.write(f"{solution5[1]:.2f}\n")
file.close()
