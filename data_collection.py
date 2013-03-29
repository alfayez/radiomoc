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
from gnuradio_flowgraph import *
ALLOC_DEF = 0
ALLOC_TOP = 1

class data_collection:
    def __init__(self):
        self.mem_vect       = []
        self.alloc_vect     = []
        self.throughput_def = -1
        self.latency_def    = -1
        self.mem_def        = -1
        self.throughput_top = []
        self.latency_top    = []
        self.mem_top        = []        
    def collect_data(self, top_handler, design_handler, infile_name):
        start_vect = 0
        end_vect   = 10
        run_len    = 0

        self.mem_vect = range(start_vect, end_vect)
        run_len       = len(self.mem_vect)
        self.alloc_vect = [ALLOC_DEF]
        self.alloc_vect.extend([ALLOC_TOP]*(run_len-1))
        print "Total Iterations= ", run_len
        print "mem_vect= ", self.mem_vect, " alloc_vect= ", self.alloc_vect
        for i in xrange(run_len):
            gnuradio_handler = gnuradio_tb_handler()
            if i == run_len-1:
                break
            print "Iteration= ", i, " mem_vect= ", self.mem_vect[i], " alloc= ", self.alloc_vect[i]
            design_handler.gnu_mem_alloc_policy = self.alloc_vect[i]
            design_handler.token_size           = self.mem_vect[i]*design_handler.token_size_orig
            design_handler.first_stage_topology_test (top_handler, top_handler.top_matrix)
            design_handler.second_stage_topology_test(top_handler, top_handler.top_matrix, gnuradio_handler)
            sink_block_list = ['file_sink']
            sink_block      = design_handler.find_block_name(sink_block_list, design_handler.second_blocks_list)
            print "sink_block= ", sink_block
            if design_handler.gnu_mem_alloc_policy == ALLOC_DEF:
                self.throughput_def = design_handler.top_impl_info[THRU][sink_block]
                self.latency_def    = design_handler.top_impl_info[LATENCY]
                self.mem_def        = design_handler.top_impl_info[MEM_TOT]
            else:
                self.throughput_top.append(design_handler.top_impl_info[THRU][sink_block])
                self.latency_top.append(design_handler.top_impl_info[LATENCY])
                self.mem_top.append(design_handler.top_impl_info[MEM_TOT])

            #top_handler.generate_code(GNURADIO, infile_name)
            #design_handler = graph_check()
            #design_handler.setup_design_constraint("memory", [1024, 2048])
            #design_handler.token_size = 1024    
            # Observe the first level system resource and consistency check on
            # the topology matrix and firing vector
            # design_handler.gnu_mem_alloc_policy = ALLOC_DEF
            #design_handler.gnu_mem_alloc_policy = ALLOC_TOP
            print "before delete gnuradio handler"
            del gnuradio_handler
            print "after delete gnuradio handler"    

        print "thru def   = ", self.throughput_def
        print "latency def= ", self.latency_def
        print "mem def    = ", self.mem_def
        
        print "thru top   = ", self.throughput_top
        print "latency top= ", self.latency_top
        print "mem top    = ", self.mem_top    
