#!/usr/bin/env python

#########################################################
# Main Program running the design environment
#########################################################

import sys, string, types, os, copy
import getopt
import numpy as np
import scipy
import fractions
import subprocess
import datetime

from optparse     import OptionParser
from ptolemy_gen  import *
from gnuradio_gen import *
from lp_gen       import *
from occam_parser import *

ALLOC_DEF = 0
ALLOC_TOP = 1

if __name__ == "__main__":
    infile_name_list = ["csp-sdf-rx.occ", "csp-sdf-tx.occ", "csp-sdf-sim.occ"]
    # the input occam program which we will be processing
    infile_name = infile_name_list[1]
    # specifies processes of interest in the occam program
    #fcn_list    = ["parameterGen", "main"]
    
    top_handler    = graph_handler(infile_name)
    design_handler = graph_check()
    # peforms initial parameter parsing of the occam file
    #top_handler.parse_input_file_param()
    #top_handler.set_param_values()
    #top_handler.parse_input_file_channels()
    #top_handler.parse_proc_connection()
    #top_handler.print_top_matrix()

    top_matrix2 = [[1,-1,0],[0,1,-1],[2,0,-1]]

    print "IS CONSISTENT= ", design_handler.is_consistent(top_matrix2)
    print top_matrix2
    [errorCond, second_sched] = design_handler.calculate_schedule(top_matrix2)
    if errorCond == OK:
        print "Found Schedule"
    if errorCond == RELAXED_NO_SOL:
        print "Relaxed LP has no solution"
    elif errorCond == INTEGER_NO_SOL:
        print "Integer problem has no soluion"
    print "repetition vector= "
    print second_sched
