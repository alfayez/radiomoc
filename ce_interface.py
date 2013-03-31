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
        self.token_vect    = [4096]
        self.alloc_vect    = [1]
        self.vect_vect     = [1]
        self.run_vect      = [5]
        self.mem_vect      = [0]
        self.lat_vect      = [0]
        self.thru_vect     = [0]
        
        self.i_cur         = 0 
    def set_ranges(self, vect_range):
        self.vect_range
    def add_data_point(self, file_name):
        sanity_check  = 0
        print "ifile_name= ", file_name
        ifile_handler = open(file_name, 'r')
        line          = ifile_handler.readline()
        tokens        = line.split()
        while line:
            if "memory_total" in line:
                sanity_check = sanity_check + 1
                self.mem_vect[self.i_cur] = float(tokens[2])
            elif "latency" in line:
                sanity_check = sanity_check + 1
                self.lat_vect[self.i_cur] = float(tokens[2])
            elif "throughput" in line:
                sanity_check = sanity_check + 1
                self.thru_vect[self.i_cur] = float(tokens[2])
            line   = ifile_handler.readline()
            tokens = line.split()
        ifile_handler.close()
        if sanity_check == 3:
            self.i_cur = self.i_cur + 1
            return True
        else:
            print "ERROR in add_data_point, file= ", filename, " is malformed, sanity check= ", sanity_check
            return False
    
if __name__ == "__main__":
    print "Before system call"

    ce_handler    = ce_interface()
    out_file_name = "temp.dat"
    in_file_name  = "csp-sdf-sim.occ"
    alloc_policy  = str(1)
    token_size    = str(4096)
    vect_fact     = str(1)
    run_time      = str(5)
    command_str = "./design_interface.py -t "+token_size+" -l "+vect_fact+" -a "+alloc_policy+ " -r "+run_time+" -o "+out_file_name+" -i "+in_file_name
    os.system(command_str)
    ce_handler.add_data_point(out_file_name)
    print "lat_vect= ",  ce_handler.lat_vect
    print "mem_vect= ",  ce_handler.mem_vect
    print "thru_vect= ", ce_handler.thru_vect
    
    print "Done with CE INTERFACE"
