#!/usr/bin/env python
import sys, string, types, os, copy
import getopt
import numpy as np
import scipy
import fractions
import subprocess

from ptolemy_gen  import *
from gnuradio_gen import *
from lp_gen       import *
from occam_parser import *
#IMPORTANT: This is the final gnuradio file that will be generated.
#It must be here so you can import and reload eventually after
#regenerating the code
#cdfrom OCCAM_generated import *

if __name__ == "__main__":
    infile_name_list = ["csp-sdf-rx.occ", "csp-sdf-tx.occ", "csp-sdf-sim.occ"]
    # the input occam program which we will be processing
    infile_name = infile_name_list[2]
    # specifies processes of interest in the occam program
    fcn_list    = ["parameterGen", "main"]
    
    top_handler    = graph_handler(infile_name)
    design_handler = graph_check()
    
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
    top_handler.generate_code(GNURADIO, infile_name)

    design_handler.setup_design_constraint("memory", [1024, 2048])
    design_handler.print_design_constraints();
    # Observe the first level system resource and consistency check on
    # the topology matrix and firing vector 
    design_handler.first_stage_topology_test(top_handler, top_handler.top_matrix)


    
