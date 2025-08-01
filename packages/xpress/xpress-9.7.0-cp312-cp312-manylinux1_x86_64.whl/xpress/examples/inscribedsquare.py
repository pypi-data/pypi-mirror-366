# Solve the 'inscribedsquare' example from MINLPLIB
#
# (C) Fair Isaac Corp., 2024-2025

# Computes a maximal inscribing square for the curve
# (sin(t)*cos(t), sin(t)*t), t in [-pi,pi]
#
# Source: https://www.minlplib.org/inscribedsquare01.html
#
# x1..x4 are the four values of the parameter t.
# x5 and x6 are the (x,y) coordinates of the first corner of the square.
# (x7, x8) is a vector pointing to a second vertex, all the other vertices
# are given by a combination of these four values.
# The length of the vector (x7,x8) is exactly the side length of the
# square, which we are maximizing, that is, the square of it, to keep it nicer.

import xpress as xp
import math
import numpy as np
from matplotlib import pyplot as plt

p = xp.problem()

# add the variables, note that we force the first point to have positive x- and y-coordinates to break symmetry
x1 = p.addVariable(name='x1', lb=-math.pi, ub=math.pi)
x2 = p.addVariable(name='x2', lb=-math.pi, ub=math.pi)
x3 = p.addVariable(name='x3', lb=-math.pi, ub=math.pi)
x4 = p.addVariable(name='x4', lb=-math.pi, ub=math.pi)
x5 = p.addVariable(name='x5')
x6 = p.addVariable(name='x6')
x7 = p.addVariable(name='x7')
x8 = p.addVariable(name='x8')

# set initial values for the local solvers
p.nlpsetinitval([x1, x2, x4, x5, x6, x7, x8], [-math.pi, -math.pi/2, math.pi/2, 0, 0, 1, 1])

# the first two constraints define x5 and x6 as the coordinates of the first point
p.addConstraint(xp.sin(x1) * xp.cos(x1) - x5 == 0)
p.addConstraint(xp.sin(x1) * x1 - x6 == 0)
# the next two constraints define x7 and x8 as the pointed vector from the first to the second point
p.addConstraint(xp.sin(x2) * xp.cos(x2) - x5 -x7 == 0)
p.addConstraint(xp.sin(x2) * x2 - x6 -x8 == 0)
# the remaining four constraints make sure that we define a square by comparing vectors between the remaining points
p.addConstraint(xp.sin(x3) * xp.cos(x3) - x5 + x8 == 0)
p.addConstraint(xp.sin(x3) * x3 - x6 - x7 == 0)
p.addConstraint(xp.sin(x4) * xp.cos(x4) - x5 - x7 + x8 == 0)
p.addConstraint(xp.sin(x4) * x4 - x6 - x7 - x8 == 0)

# the objective is to maximize the length of one (or each) side of the square
p.setObjective(x7**2 + x8**2, sense=xp.maximize)

# write the model to a file
#p.write("python-inscribedsquare.lp")

# choose between solving with a local or global solver
p.setControl('nlpsolver', 1)
# choose between solving with SLP or Knitro
p.setControl('localsolver', 0)

p.optimize()

# below code approximates the graph of the function
t = np.arange(-math.pi, math.pi, 0.01)
xs = np.sin(t) * np.cos(t)
ys = np.sin(t) * t

# compute the x- and y-coordinates of the four vertices of the square
p11 = np.sin(p.getSolution(x1)) * np.cos(p.getSolution(x1))
p21 = np.sin(p.getSolution(x2)) * np.cos(p.getSolution(x2))
p31 = np.sin(p.getSolution(x3)) * np.cos(p.getSolution(x3))
p41 = np.sin(p.getSolution(x4)) * np.cos(p.getSolution(x4))
p12 = np.sin(p.getSolution(x1)) * p.getSolution(x1)
p22 = np.sin(p.getSolution(x2)) * p.getSolution(x2)
p32 = np.sin(p.getSolution(x3)) * p.getSolution(x3)
p42 = np.sin(p.getSolution(x4)) * p.getSolution(x4)

# plot the graph and the square
fig, ax = plt.subplots()
cells = ax.plot(xs, ys)
plt.plot([p11,p21],[p12,p22], 'ro-')
plt.plot([p21,p41],[p22,p42], 'ro-')
plt.plot([p41,p31],[p42,p32], 'ro-')
plt.plot([p31,p11],[p32,p12], 'ro-')
ax.set_aspect('equal', adjustable='box')

plt.show()

# print the variable values
print('solution: x1:', p.getSolution(x1), ', x2:', p.getSolution(x2), ', x3:', p.getSolution(x3), ', x4:', p.getSolution(x4), ', x5:', p.getSolution(x5), ', x6:', p.getSolution(x6), ', x7:', p.getSolution(x7), ', x8:', p.getSolution(x8))
