import math
import os
import subprocess

class Node:
    def __init__(self, coeffecient, x_exponent, y_exponent):
        self.coeffecient = coeffecient
        self.x_exponent = x_exponent
        self.y_exponent = y_exponent
        self.next = None

def create(c, x, y):
    return Node(c, x, y)

def insert():
    c = x = y = n = e = 0
    head = None
    temp = None
    t = None
    print("\nEnter the number of terms in f(x,y):", end="")
    e = int(input())
    n = e
    while e != 0:
        print("\nEnter the coefficient of this term:", end="")
        c = int(input())
        print("\nEnter the exponent of x:", end="")
        x = int(input())
        print("\nEnter the exponent of y:", end="")
        y = int(input())
        if n == e:
            temp = create(c, x, y)
            head = temp
            t = temp
            e -= 1
        else:
            temp = create(c, x, y)
            t.next = temp
            t = t.next
            e -= 1
    return head

def display(head):
    print("\nF(x,y)=", end="")
    temp = head
    if temp is None:
        print("0")
        return 0
    while temp.next is not None:
        print(f"({temp.coeffecient}(x^{temp.x_exponent})(y^{temp.y_exponent}))+", end="")
        temp = temp.next
    print(f"({temp.coeffecient}(x^{temp.x_exponent})(y^{temp.y_exponent}))")

def maxima(head, maxpt):
    temp = head
    x = maxpt[0]
    y = maxpt[1]
    val = 0
    while temp is not None:
        val += temp.coeffecient * (x**temp.x_exponent) * (y**temp.y_exponent)
        temp = temp.next
    print(f"\nThe local maxima of f(x) is ={val:.4f}")

def minima(head, minpt):
    temp = head
    x = minpt[0]
    y = minpt[1]
    val = 0
    while temp is not None:
        val += temp.coeffecient * (x**temp.x_exponent) * (y**temp.y_exponent)
        temp = temp.next
    print(f"\nThe local minima of f(x) is ={val:.4f}")

def evaluate_points(d2x, d2y, dm, pts, maxpt, minpt, MAX, MIN):
    for i in range(0, 10, 2):
        x = pts[i]
        y = pts[i + 1]
        L = d2x
        N = d2y
        M = dm
        l = 0.0
        n = 0.0
        m = 0.0
        print(f"\n\n##new stationary point##\nfor (x,y)=({x:.2f},{y:.2f})")
        while L is not None:
            l += (x**L.x_exponent) * (y**L.y_exponent) * L.coeffecient
            L = L.next
        while N is not None:
            n += (x**N.x_exponent) * (y**N.y_exponent) * N.coeffecient
            N = N.next
        while M is not None:
            m += (x**M.x_exponent) * (y**M.y_exponent) * M.coeffecient
            M = M.next
        print(f"\nl={l:.4f} n={n:.4f} m={m:.4f}")
        val1 = l * n
        val2 = m * m
        val = val1 - val2
        print(f"\nln-m**2={val:.4f}")
        if val < 0.00:
            print(f"\n({x:.2f},{y:.2f}) is a saddle point.")
        elif val == 0.00:
            print(f"\n({x:.2f},{y:.2f}) is point with no conclusion.")
        else:
            if l < 0.00:
                print(f"\n({x:.2f},{y:.2f}) is a point of maxima.")
                MAX[0] = 1
                maxpt[0] = x
                maxpt[1] = y
            else:
                print(f"\n({x:.2f},{y:.2f}) is a point of minima.")
                MIN[0] = 1
                minpt[0] = x
                minpt[1] = y

def finding_stationary_points(dx, dy, pts):
    temp_dx = dx
    temp_dy = dy
    with open("derivatives.txt", "w") as file:
        if temp_dx is None:
            file.write("0")
        while temp_dx is not None:
            if temp_dx == dx:
                file.write(f"{temp_dx.coeffecient}*x**{temp_dx.x_exponent}*y**{temp_dx.y_exponent}")
            elif temp_dx.coeffecient < 0:
                file.write(f"{temp_dx.coeffecient}*x**{temp_dx.x_exponent}*y**{temp_dx.y_exponent}")
            else:
                file.write(f"+{temp_dx.coeffecient}*x**{temp_dx.x_exponent}*y**{temp_dx.y_exponent}")
            temp_dx = temp_dx.next
        file.write("\n")
        if temp_dy is None:
            file.write("0")
        while temp_dy is not None:
            if temp_dy == dy:
                file.write(f"{temp_dy.coeffecient}*x**{temp_dy.x_exponent}*y**{temp_dy.y_exponent}")
            elif temp_dy.coeffecient < 0:
                file.write(f"{temp_dy.coeffecient}*x**{temp_dy.x_exponent}*y**{temp_dy.y_exponent}")
            else:
                file.write(f"+{temp_dy.coeffecient}*x**{temp_dy.x_exponent}*y**{temp_dy.y_exponent}")
            temp_dy = temp_dy.next
    result = subprocess.run(["python", "finding_stationary_points.py"]).returncode
    if result == 0:
        print("\nPython script executed successfully.Stationary points successfully generated.")
    else:
        print("\nError executing Python script.")
    try:
        with open("points.txt", "r") as f:
            print("\nStationary Points are:")
            s = 0
            for line in f:
                for val in line.split():
                    pts[s] = float(val)
                    if s % 2 == 0:
                        print(f"({pts[s]:.2f},", end="")
                    else:
                        print(f"{pts[s]:.2f})")
                    s += 1
    except:
        print("Error opening file.")

def solve(head):
    dx = None
    dy = None
    d2x = None
    d2y = None
    m = None
    temp = head
    temp_dx = dx
    temp_dy = dy
    t = None
    l = 0
    print("\nLet d denote partial differentiation:")
    print("df/dx=", end="")
    while temp is not None:
        if temp.x_exponent == 0:
            temp = temp.next
            continue
        c = temp.x_exponent * temp.coeffecient
        if l == 0:
            dx = create(c, temp.x_exponent - 1, temp.y_exponent)
            t = dx
            l += 1
        else:
            t.next = create(c, temp.x_exponent - 1, temp.y_exponent)
            t = t.next
        temp = temp.next
    display(dx)
    temp = head
    t = None
    l = 0
    while temp is not None:
        if temp.y_exponent == 0:
            temp = temp.next
            continue
        c = temp.y_exponent * temp.coeffecient
        if l == 0:
            dy = create(c, temp.x_exponent, temp.y_exponent - 1)
            t = dy
            l += 1
        else:
            t.next = create(c, temp.x_exponent, temp.y_exponent - 1)
            t = t.next
        temp = temp.next
    print("\ndf/dy=", end="")
    display(dy)
    temp_dx = dx
    t = None
    l = 0
    while temp_dx is not None:
        if temp_dx.x_exponent == 0:
            temp_dx = temp_dx.next
            continue
        c = temp_dx.x_exponent * temp_dx.coeffecient
        if l == 0:
            d2x = create(c, temp_dx.x_exponent - 1, temp_dx.y_exponent)
            t = d2x
            l += 1
        else:
            t.next = create(c, temp_dx.x_exponent - 1, temp_dx.y_exponent)
            t = t.next
        temp_dx = temp_dx.next
    print("\nd^2f/dx^2=l=", end="")
    display(d2x)
    temp_dy = dy
    t = None
    l = 0
    while temp_dy is not None:
        if temp_dy.y_exponent == 0:
            temp_dy = temp_dy.next
            continue
        c = temp_dy.y_exponent * temp_dy.coeffecient
        if l == 0:
            d2y = create(c, temp_dy.x_exponent, temp_dy.y_exponent - 1)
            t = d2y
            l += 1
        else:
            t.next = create(c, temp_dy.x_exponent, temp_dy.y_exponent - 1)
            t = t.next
        temp_dy = temp_dy.next
    print("\nd^2f/dy^2=n=", end="")
    display(d2y)
    temp_dy = dy
    t = None
    l = 0
    while temp_dy is not None:
        if temp_dy.x_exponent == 0:
            temp_dy = temp_dy.next
            continue
        c = temp_dy.x_exponent * temp_dy.coeffecient
        if l == 0:
            m = create(c, temp_dy.x_exponent - 1, temp_dy.y_exponent)
            t = m
            l += 1
        else:
            t.next = create(c, temp_dy.x_exponent - 1, temp_dy.y_exponent)
            t = t.next
        temp_dy = temp_dy.next
    print("\nd^2f/dxdy=m=", end="")
    display(m)
    return dx, dy, d2x, d2y, m

def main():
    print("\nMaxima and Minima Calculator for 2 variable equations without the inclusion of Trigonometric and Logarithmic functions:")
    print("Enter f(x,y):")
    head = insert()
    display(head)
    dx, dy, d2x, d2y, m = solve(head)
    pts = [0.0] * 10
    maxpt = [0.0, 0.0]
    minpt = [0.0, 0.0]
    MAX = [0]
    MIN = [0]
    finding_stationary_points(dx, dy, pts)
    evaluate_points(d2x, d2y, m, pts, maxpt, minpt, MAX, MIN)
    if MAX[0] != 0:
        maxima(head, maxpt)
    if MIN[0] != 0:
        minima(head, minpt)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
