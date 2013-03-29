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

from ptolemy_gen     import *
from gnuradio_gen    import *
from lp_gen          import *
from occam_parser    import *
from data_collection import *
from design_check    import *

ALLOC_DEF = 0
ALLOC_TOP = 1

if __name__ == "__main__":
    infile_name_list = ["csp-sdf-rx.occ", "csp-sdf-tx.occ", "csp-sdf-sim.occ"]
    # the input occam program which we will be processing
    infile_name = infile_name_list[2]
    # specifies processes of interest in the occam program
    fcn_list    = ["parameterGen", "main"]
    
    top_handler    = graph_handler(infile_name)
    design_handler = graph_check()
    data_handler   = data_collection()
    
    design_handler.DEBUG = False
    top_handler.set_fcn_interest(fcn_list)
    # peforms initial parameter parsing of the occam file
    top_handler.parse_input_file_param()
    top_handler.set_param_values()
    top_handler.parse_input_file_channels()
    top_handler.parse_proc_connection()
    top_handler.print_top_matrix()

    
    print "Genertaing Ptolemy simulation ..."
    top_handler.generate_code(PTOLEMY, infile_name)
    print "Generating GNU Radio project file ..."
    ##############################################
    ## DISABLED TO PREVENT GRC FILE REWRITE
    top_handler.generate_code(GNURADIO, infile_name)
    design_handler.setup_design_constraint("memory", [1024, 2048])
    design_handler.token_size = 1024    
    # Observe the first level system resource and consistency check on
    # the topology matrix and firing vector
    #design_handler.gnu_mem_alloc_policy = ALLOC_DEF
    #design_handler.gnu_mem_alloc_policy = ALLOC_TOP
    ##############################################
    #design_handler.first_stage_topology_test(top_handler, top_handler.top_matrix)
    #design_handler.second_stage_topology_test(top_handler, top_handler.top_matrix)




    data_handler.collect_data(top_handler, design_handler, infile_name)







    #par_node = design_handler.find_parent_node(14, design_handler.second_top_matrix, design_handler.second_blocks_list)
    #print "PAR NODE= ", par_node
    print "Final TOP MAtrix= "
    print design_handler.second_top_matrix
    #design_handler.set_gnuradio_top_matrix()
    #design_handler.set_gnuradio_firing_vector()
    design_handler.print_gnuradio_top_matrix()
    design_handler.print_gnuradio_firing_vector()

    ###########################################
    ## Prints final design resource utilization
    #design_handler.print_design_constraints();
    ###########################################
    
