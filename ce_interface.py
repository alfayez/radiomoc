#!/usr/bin/env python

import sys, string, types, os, copy, time
import getopt
import numpy as np
import scipy
import fractions
import subprocess

from ptolemy_gen  import *
from gnuradio_gen import *
from lp_gen       import *
from occam_parser import *
import occam_parser as occam

class ce_interface:
    def __init__(self):
        self.out_file_vect = []
        self.token_vect    = []
        self.alloc_vect    = []
        self.vect_vect     = []
        self.run_vect      = []
    def set_ranges(self, vect_range):
        self.vect_range
    
if __name__ == "__main__":
    print "Before system call"
    out_file_name = "temp.dat"
    in_file_name  = "csp-sdf-sim.occ"
    alloc_policy  = str(1)
    token_size    = str(4096)
    vect_fact     = str(1)
    run_time      = str(5)
    command_str = "./design_interface.py -t "+token_size+" -l "+vect_fact+" -a "+alloc_policy+ " -r "+run_time+" -o "+out_file_name+" -i "+in_file_name
    os.system(command_str)
    print "Done with CE INTERFACE"
