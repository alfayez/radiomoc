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
    print "Date/Time= ", datetime.datetime.now()

    parser = OptionParser()
    parser.add_option("-t", "--token-size",   dest="token_size_pass",  help="Passes the desired token size")
    parser.add_option("-l", "--vect-fact",    dest="vect_factor_pass", help="The vectorization factor for the calculated schedule")
    parser.add_option("-a", "--alloc-policy", dest="alloc_policy_pass",help="0-> Default, 1->Topology matrix based")
    parser.add_option("-r", "--run-time",     dest="run_time_pass",    help="How many seconds to run the graph for")
    parser.add_option("-o", "--out-file",     dest="out_file_pass",    help="File to write performance data")
    parser.add_option("-i", "--in-file",      dest="in_file_pass",     help="File to read in")

    (options, args) = parser.parse_args()

    print "token_size_pass= ", options.token_size_pass, " vect_factor_pass= ", options.vect_factor_pass, "alloc_policy_pass= ", options.alloc_policy_pass, " run_time=", options.run_time_pass, " out-file= ", options.out_file_pass, " in-file= ", options.in_file_pass
    #exit(-1)
    #infile_name_list = ["csp-sdf-rx.occ", "csp-sdf-tx.occ", "csp-sdf-sim.occ"]
    # the input occam program which we will be processing
    infile_name = options.in_file_pass
    # specifies processes of interest in the occam program
    fcn_list    = ["parameterGen", "main"]
    
    top_handler    = graph_handler(infile_name)
    design_handler = graph_check()
    design_handler.infile_name = infile_name
    design_handler.ofile_name  = options.out_file_pass
    design_handler.DEBUG = False
    top_handler.set_fcn_interest(fcn_list)
    # peforms initial parameter parsing of the occam file
    top_handler.parse_input_file_param()
    top_handler.set_param_values()
    top_handler.parse_input_file_channels()
    top_handler.parse_proc_connection()
    #top_handler.print_top_matrix()

    
    print "Genertaing Ptolemy simulation ..."
    top_handler.generate_code(PTOLEMY, infile_name)
    print "Generating GNU Radio project file ..."
    ##########################################3
    ## DISABLED TO PREVENT GRC FILE REWRITE
    top_handler.generate_code(GNURADIO, infile_name)

    design_handler.setup_design_constraint("memory", [1024, 2048])
    ##########################################3
    
    # Observe the first level system resource and consistency check on
    # the topology matrix and firing vector
    design_handler.gnu_mem_alloc_policy = int(options.alloc_policy_pass)
    design_handler.token_size_orig      = int(options.token_size_pass)
    design_handler.vect_factor          = int(options.vect_factor_pass)
    design_handler.token_size           = int(options.token_size_pass)*int(options.vect_factor_pass)
    design_handler.run_time             = int(options.run_time_pass)
    design_handler.first_stage_topology_test(top_handler, top_handler.top_matrix)

    design_handler.second_stage_topology_test(top_handler, top_handler.top_matrix)
    # par_node = design_handler.find_parent_node(14, design_handler.second_top_matrix, design_handler.second_blocks_list)
    # print "PAR NODE= ", par_node
    #print "Final TOP MAtrix= "
    #print design_handler.second_top_matrix
    #design_handler.print_gnuradio_top_matrix()
    #design_handler.print_gnuradio_firing_vector()

    ###########################################
    ## Prints final design resource utilization
    #design_handler.print_design_constraints();
    design_handler.print_top_impl_info_file()
    #print design_handler.second_blocks_list
    ###########################################
    
