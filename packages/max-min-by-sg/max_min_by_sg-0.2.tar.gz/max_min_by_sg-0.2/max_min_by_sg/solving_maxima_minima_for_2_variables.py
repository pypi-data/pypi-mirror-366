import os
import math

class Node:
	def __init__(self, c, x, y):
		self.coeffecient = c
		self.x_exponent = x
		self.y_exponent = y
		self.next = None

def create(c, x, y):
	return Node(c, x, y)

def insert():
	head = None
	print("\nEnter the number of terms in f(x,y):", end="")
	e = int(input())
	n = e
	t = None
	while e != 0:
		print("\nEnter the coefficient of this term:", end="")
		c = int(input())
		print("\nEnter the exponent of x:", end="")
		x = int(input())
		print("\nEnter the exponent of y:", end="")
		y = int(input())
		temp = create(c, x, y)
		if n == e:
			head = temp
			t = temp
		else:
			t.next = temp
			t = temp
		e -= 1
	return head

def display(head):
	print("\nF(x,y)=", end="")
	temp = head
	if temp is None:
		print("0")
		return
	while temp.next is not None:
		print(f"({temp.coeffecient}(x^{temp.x_exponent})(y^{temp.y_exponent}))+", end="")
		temp = temp.next
	print(f"({temp.coeffecient}(x^{temp.x_exponent})(y^{temp.y_exponent}))", end="")

def maxima(head, maxpt):
	temp = head
	x = maxpt[0]
	y = maxpt[1]
	val = 0
	while temp is not None:
		val += temp.coeffecient * math.pow(x, temp.x_exponent) * math.pow(y, temp.y_exponent)
		temp = temp.next
	print(f"\nThe local maxima of f(x) is ={val:.4f}")

def minima(head, minpt):
	temp = head
	x = minpt[0]
	y = minpt[1]
	val = 0
	while temp is not None:
		val += temp.coeffecient * math.pow(x, temp.x_exponent) * math.pow(y, temp.y_exponent)
		temp = temp.next
	print(f"\nThe local minima of f(x) is ={val:.4f}")

def evaluate_points(d2x, d2y, dm, pts, maxpt, minpt, MAX, MIN):
	for i in range(0, 10, 2):
		x = pts[i]
		y = pts[i+1]
		L = d2x
		N = d2y
		M = dm
		l = 0.0
		m = 0.0
		n = 0.0
		print(f"\n\n##new stationary point##\nfor (x,y)=({x:.2f},{y:.2f})")
		while L is not None:
			l += math.pow(x, L.x_exponent) * math.pow(y, L.y_exponent) * L.coeffecient
			L = L.next
		while N is not None:
			n += N.coeffecient * math.pow(x, N.x_exponent) * math.pow(y, N.y_exponent)
			N = N.next
		while M is not None:
			m += math.pow(x, M.x_exponent) * math.pow(y, M.y_exponent) * M.coeffecient
			M = M.next
		print(f"\nl={l:.4f} n={n:.4f} m={m:.4f}")
		val1 = l * n
		val2 = m * m
		val = val1 - val2
		print(f"\nln-m**2={val:.4f}")
		if val < 0.00:
			print(f"\n({x:.2f},{y:.2f}) is a saddle point.")
			continue
		elif val == 0.00:
			print(f"\n({x:.2f},{y:.2f}) is point with no conclusion.")
			continue
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
	os.system("python max_min_by_sg/finding_stationary_points.py")
	with open("points.txt", "r") as file2:
		s = 0
		print("\nStationary Points are:")
		for line in file2:
			num = float(line.strip())
			pts[s] = num
			if s % 2 == 0:
				print(f"({pts[s]:.2f},", end="")
			else:
				print(f"{pts[s]:.2f})")
			s += 1

def solve(head, dx, dy, d2x, d2y, m):
	temp = head
	temp_dx = dx
	temp_dy = dy
	l = 0
	t = None
	print("\nLet d denote partial differentiation:")
	print("df/dx=", end="")
	while temp is not None:
		if temp.x_exponent == 0:
			temp = temp.next
			continue
		c = temp.x_exponent * temp.coeffecient
		new_node = create(c, temp.x_exponent - 1, temp.y_exponent)
		if l == 0:
			dx = new_node
			t = new_node
			l += 1
		else:
			t.next = new_node
			t = new_node
		temp = temp.next
	display(dx)
	temp = head
	l = 0
	t = None
	while temp is not None:
		if temp.y_exponent == 0:
			temp = temp.next
			continue
		c = temp.y_exponent * temp.coeffecient
		new_node = create(c, temp.x_exponent, temp.y_exponent - 1)
		if l == 0:
			dy = new_node
			t = new_node
			l += 1
		else:
			t.next = new_node
			t = new_node
		temp = temp.next
	print("\ndf/dy=", end="")
	display(dy)
	temp_dx = dx
	l = 0
	t = None
	while temp_dx is not None:
		if temp_dx.x_exponent == 0:
			temp_dx = temp_dx.next
			continue
		c = temp_dx.x_exponent * temp_dx.coeffecient
		new_node = create(c, temp_dx.x_exponent - 1, temp_dx.y_exponent)
		if l == 0:
			d2x = new_node
			t = new_node
			l += 1
		else:
			t.next = new_node
			t = new_node
		temp_dx = temp_dx.next
	print("\nd^2f/dx^2=l=", end="")
	display(d2x)
	temp_dy = dy
	l = 0
	t = None
	while temp_dy is not None:
		if temp_dy.y_exponent == 0:
			temp_dy = temp_dy.next
			continue
		c = temp_dy.y_exponent * temp_dy.coeffecient
		new_node = create(c, temp_dy.x_exponent, temp_dy.y_exponent - 1)
		if l == 0:
			d2y = new_node
			t = new_node
			l += 1
		else:
			t.next = new_node
			t = new_node
		temp_dy = temp_dy.next
	print("\nd^2f/dy^2=n=", end="")
	display(d2y)
	temp_m = None
	temp_dy = dy
	l = 0
	t = None
	while temp_dy is not None:
		if temp_dy.x_exponent == 0:
			temp_dy = temp_dy.next
			continue
		c = temp_dy.x_exponent * temp_dy.coeffecient
		new_node = create(c, temp_dy.x_exponent - 1, temp_dy.y_exponent)
		if l == 0:
			temp_m = new_node
			t = new_node
			l += 1
		else:
			t.next = new_node
			t = new_node
		temp_dy = temp_dy.next
	m = temp_m
	print("\nd^2f/dxdy=m=", end="")
	display(m)
	return dx, dy, d2x, d2y, m

def main():
	print("\nMaxima and Minima Calculator for 2 variable equations without the inclusion of Trigonometric and Logarithmic functions:")
	head = insert()
	display(head)
	dx = dy = d2x = d2y = m = None
	pts = [0.0]*10
	maxpt = [0.0]*2
	minpt = [0.0]*2
	MAX = [0]
	MIN = [0]
	dx, dy, d2x, d2y, m = solve(head, dx, dy, d2x, d2y, m)
	finding_stationary_points(dx, dy, pts)
	evaluate_points(d2x, d2y, m, pts, maxpt, minpt, MAX, MIN)
	if MAX[0] != 0:
		maxima(head, maxpt)
	if MIN[0] != 0:
		minima(head, minpt)
	input("\nPress Enter to exit...")

if __name__ == "__main__":
	main()
