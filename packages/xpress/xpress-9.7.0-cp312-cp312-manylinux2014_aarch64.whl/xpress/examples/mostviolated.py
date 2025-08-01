#  Xpress Optimizer Examples
#   =========================
#
#   file mostviolated.py
#   ```````````````````
#   A Branching rule branching on the most violated Integer/Binary.
#
#   Demonstrate the Xpress-MP change branch callbacks.
#
#   (c) 2024-2025 Fair Isaac Corporation

import xpress as xp
import math

# Class for data object to pass to variable selection callback
class SolData:
    def __init__(self, colind, coltype, tol):
        self.colind = colind
        self.coltype = coltype
        self.tol = tol

# This function will be called every time the Optimizer has selected a candidate entity for branching
def varselectioncb(prob, soldata, obranch):

    dsol = prob.getCallbackPresolveSolution() # Get solution in the presolved space

    branchcol = -1 # To store column index of the variable to branch on, if any

    # Find the most fractional column
    greatdist = 0
    for i in soldata.colind:
        updist = math.ceil(dsol[i]) - dsol[i]
        downdist = dsol[i] - math.floor(dsol[i])

        dist = min(updist,downdist)

        if dist > soldata.tol and dist > greatdist:
            branchcol = i
            greatdist = dist

    # If we found a column to branch on then create a branching object
    # (in the presolved space) that reflects branching on that column and
    # return it to the caller.
    if branchcol >= 0:
        UB = math.floor(dsol[branchcol])
        LB = math.ceil(dsol[branchcol])

        new_branch = xp.branchobj(prob, isoriginal=False)   # Create new branch object to be returned
        new_branch.addbranches(2)                           # Number of branches to add
        new_branch.addbounds(0,["U"],[branchcol],[UB])      # Add upper bound to first branch
        new_branch.addbounds(1,["L"],[branchcol],[LB])      # Add lower bound to second branch

        return new_branch
    else:
        return None

# Create a new problem
p = xp.problem()

modelfile = "burglar.mps"
p.read(modelfile)

p.controls.mipdualreductions = 0  # Turn off dual presolve reductions for this example, otherwise the problem is reduced to an empty problem

print(f"Start solving problem {modelfile}.")

p.mipoptimize("l") # Use mipoptimize with the 'l' flag to stop after solving the root LP relaxation

p.controls.miplog = 3

# Change some controls to make sure we actually need to branch to solve the problem
p.controls.heuremphasis = 0
p.controls.cutstrategy = 0

# Get solution data (presolved problem) to pass to callback
colind = []
coltype = []
p.getmipentities(coltype,colind,None,None,None,None,None)
mtol = p.controls.miptol

sol = SolData(colind,coltype,mtol)

p.addcbchgbranchobject(varselectioncb, sol)

p.mipoptimize()

print("Solving complete.")