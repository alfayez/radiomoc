#!/usr/bin/env python
import numpy
import scipy
from scipy import linalg, matrix

import glpk

tol = 1
lp = glpk.LPX()
lp.name = "test.lp"

lp.obj.maximize = False

lp.rows.add(3)
for r in lp.rows:
    r.name = "d"+str(r)
    r.bounds = 0, 0

lp.cols.add(3)
i=1
for c in lp.cols:
    print "i= ", i
    c.name   = "x"+str(i)
    if i == 1: 
        c.bounds = 1, None
    else:
        c.bounds = 1, None
    c.kind   = int
    i        = i+1

lp.obj[0] = 1
lp.obj[1] = 1
lp.obj[2] = 1
lp.matrix = [1, -1, 0,
             0, 2, -1,
             2, 0, -1]


print "obj fcn= ", lp.obj
print "lp matrix= ",
print lp.rows[0].matrix
print "lp matrix= ",
print lp.rows[1].matrix
print "lp matrix= ",
print lp.rows[2].matrix

#the relaxed integer solution
retval = lp.simplex()
assert retval == None
print "obj val= ", lp.obj.value
for c in lp.cols:
    print c.name, "= ", c.primal

for c in lp.cols:
    c.kind   = int

retval = lp.integer()
print "obj val= ", lp.obj.value
for c in lp.cols:
    print c.name, "= ", c.value



