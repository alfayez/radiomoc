#!/usr/bin/env python
import numpy as np
import glpk
import copy

OK             = 0
RELAXED_NO_SOL = 1
INTEGER_NO_SOL = 2
def setup_sched_lp(mat):
    firing_lb = 1
    mat_temp  = []
    obj_temp  = []
    sched_loc = []    
    row = len(mat)
    col = len(mat[0])
    lp  = glpk.LPX()

    # the objective function is all ones because we're interested in
    # getting the minimum firing schedule so we want to minimize the
    # total number of actor firings
    #obj_temp = np.ones(col, dtype=np.float)
    obj_temp = np.ones(col, dtype=np.int)
    mat_temp = np.zeros(row*col)
    
    # LP configuration
    lp.name         = "autogen.lp"
    lp.obj.maximize = False       # We want to minimize the number of
                                  # firings so we can get the minimal
                                  # schedule
    glpk.env.term_on = False      # stops misc GLPK output
    lp.rows.add(row)
    lp.cols.add(col)
    for i in range(col):
        lp.obj[i]        = 1.0   # set up the objective function of
                                 # the LP

    # UB and LB must be zeros to get the null space of the topology matrix
    for r in lp.rows:
        r.bounds = 0.0,0.0
    for c in lp.cols:
        # lower bound >= 1 to ensure that we don't get the trivial
        # solution of all zeros
        c.bounds = firing_lb, None
    k=0
    for i in mat:
        for j in i:
            mat_temp[k] = j
            k           = k + 1
    lp.matrix = mat_temp

    # solved the relaxed form of the LP
    retval = lp.simplex()
    assert retval == None
    if lp.status != 'opt':
        return [RELAXED_NO_SOL, copy.deepcopy(sched_loc)]

    #################################################
    #################################################
    ## IMPORTANT RETURN INFO
    stat = lp.status
    print "obj val= ", lp.obj.value

    # setup the LP as a MIP
    for c in lp.cols:
        c.kind = int
    retval = lp.integer()
    assert retval == None
    if lp.status != 'opt':
        return [INTEGER_NO_SOL, copy.deepcopy(sched_loc)]
    
    sched_loc = np.zeros((len(lp.cols), 1))
    i = 0
    for c in lp.cols:
        sched_loc[i][0] = c.primal
        i = i + 1
    return [OK, copy.deepcopy(sched_loc)]
    #################################################
    #################################################
