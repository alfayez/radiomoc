#!/usr/bin/env python

#########################################################
# This file is responsible for running all the necessary
# design and topology matrix checks
#########################################################

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
import occam_parser as o

#IMPORTANT: This is the final gnuradio file that will be generated.
#It must be here so you can import and reload eventually after
#regenerating the code
#cdfrom OCCAM_generated import *

class graph_check:
    def __init__(self):
        # gnuradio Top Block Handler
        self.gnuradio_tb         = {}
        # Dictionary holding the users desired design constraints
        self.design_constraints  = {}        
        self.default_buffer_size = 32*1024
        self.cur_bufer_size      = 32*1024
        self.token_size   = 1024
        self.second_top_matrix = np.zeros((1,1))

        self.top_impl_info = {# whether a graph is consistent or not
                              'consistent'      : False,
                              #Dictionary with each block output
                              #buffer memory usage
                              'memory'          : {},
                              #total output buffer memory consumption
                              'memory_total'    : 0,
                              
                          }
    def setup_gnuradio_handle(self):
            from OCCAM_generated import OCCAM_generated
            # set the gnuradio top block handler to the one generated
            self.gnuradio_tb = OCCAM_generated()            
    def print_top_impl_info(self):
        for item in self.top_impl_info.keys():
            print item, "= ", self.top_impl_info[item]    
    #Calculates the memory usage of each block and accumulate the
    #total memory usage for reference
    def memory_usage(self, graph_handler, top_matrix):
        len_chans = len(graph_handler.chan_list)
        self.top_impl_info["memory_total"] = 0
        # initialize the memory utilization for each block as 0
        for i in range(len_chans):
            chan_name      = graph_handler.chan_list[i]            
            proc_out       = graph_handler.chan_dict[chan_name][0]
            proc_out_index = graph_handler.proc_dict[proc_out][o.PROC_LIST_IND]
            self.top_impl_info["memory"][proc_out] = 0
        mem_cur_chan = 0
        for i in range(len_chans):
            chan_name = graph_handler.chan_list[i]    
            proc_out  = graph_handler.chan_dict[chan_name][0]
            proc_out_index  = graph_handler.proc_dict[proc_out][o.PROC_LIST_IND]
            mem_cur_chan    = top_matrix[i][proc_out_index]*self.token_size
            self.top_impl_info["memory"][proc_out] = self.top_impl_info["memory"][proc_out]+mem_cur_chan
            self.top_impl_info["memory_total"]     = self.top_impl_info["memory_total"]+ mem_cur_chan
    def setup_design_constraint(self, name_val, range_val):
        self.design_constraints[name_val] = range_val
    def print_design_constraints(self):
        print "Design Constraints= "
        print self.design_constraints
    def first_stage_topology_test(self, graph_handler, top_matrix):
        # calculate the 1st level topology matrix and constraints
        errorCond = self.calculate_schedule(top_matrix)
        self.setup_gnuradio_handle()
        self.print_schedule()
        self.is_consistent(top_matrix)
        self.memory_usage(graph_handler, top_matrix)
        self.print_top_impl_info()
    def second_stage_topology_test(self, graph_handler, top_matrix):
        self.gnuradio_tb.prealloc()
	print "GNURADIO top matrix= "
	self.second_top_matrix = self.get_top_matrix()
        print self.second_top_matrix
	print "GNURADIO blocks_list= "
	print self.get_blocks_list()
        self.gnuradio_tb.alloc(self.cur_bufer_size)
        self.gnuradio_tb.go()
        time.sleep(2)        
        print "GOODBUY"
        self.gnuradio_tb.stop()
    def print_schedule(self):
        print "Firing Schedule"
        print self.sched
    def calculate_schedule(self, top_matrix):
        [errorCond, self.sched] = setup_sched_lp(top_matrix)
        return errorCond
    def is_consistent(self, top_matrix):
        # TODO: add consistency for BDF type blocks ... such as packet decoders
        self.rankVal = np.linalg.matrix_rank(top_matrix)
        num_actors   = len(top_matrix[0])
        if self.rankVal < num_actors:
            self.top_impl_info["consistent"] = True
        else:
            self.top_impl_info["consistent"] = False

    #######################################################################
    #######################################################################
    # GNURADIO specific methods
    #######################################################################
    #######################################################################
    def get_work_time(self):
            tinfo = self.gnuradio_tb.blocks_add_xx_0.pc_work_time()
            print "tinfo= ", tinfo
    def get_buffer_full(self):
            print "Buffer Full perc="
            print self.gnuradio_tb.blocks_add_xx_0.pc_output_buffers_full()
    def get_top_matrix(self):
            row = self.gnuradio_tb.top_get_number_of_edges()
            col = self.gnuradio_tb.top_get_number_of_blocks()
            #print self.top_matrix_top(index1, index2)
            matrix_loc = np.zeros((row, col))
            for i in range(row):
                    for j in range(col):
                            matrix_loc[i][j] = self.gnuradio_tb.top_matrix_top(i, j)
            print "gnuradio topology matrix= "
            print matrix_loc
            return copy.deepcopy(matrix_loc)
    def get_blocks_list(self):
            print "gnuradio blocks list= "
            #print self.gnuradio_tb.blocks_list_top(index)
            block_loc = {}
            col = self.gnuradio_tb.top_get_number_of_blocks()
            for i in range(col):
                    block_name = self.gnuradio_tb.blocks_list_top(i)
                    block_loc[block_name] = ""
            return copy.deepcopy(block_loc)

    def get_number_of_blocks(self):
            print "gnuradio num blocks= "
            print self.gnuradio_tb.top_get_number_of_blocks()
    def get_number_of_edges(self):
            print "gnuradio num edges= "
            print self.gnuradio_tb.top_get_number_of_edges()
