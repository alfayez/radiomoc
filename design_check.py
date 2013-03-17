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

        self.first_is_consistent = False        
        self.first_sched         = []
        
        self.second_top_matrix    = np.zeros((1,1))
        self.second_blocks_list   = []
        self.second_is_consistent = False
        self.second_sched         = []
        
        self.top_impl_info = {# whether a graph is consistent or not
                              'consistent'      : False,
                              #Dictionary with each block output
                              #buffer memory usage
                              'memory'          : {},
                              #total output buffer memory consumption
                              'memory_total'    : 0,
                              
                          }
        self.DEBUG = False
    def setup_gnuradio_handle(self):
            import OCCAM_generated
            reload(OCCAM_generated)
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
        self.first_is_consistent = self.is_consistent(top_matrix)
        self.memory_usage(graph_handler, top_matrix)
        if self.DEBUG:
            print "First Stage"
            if errorCond == OK:
                print "Found Schedule"
            elif errorCond == RELAXED_NO_SOL:
                print "Relaxed LP has no solution"
            elif errorCond == INTEGER_NO_SOL:
                print "Integer problem has no soluion"        
            print "First Schedule= "
            self.print_schedule(self.first_sched)
            print "1st Stage topology matrix consistency= ", self.first_is_consistent
            self.print_top_impl_info()
    def second_stage_topology_test(self, graph_handler, top_matrix):
        self.gnuradio_tb.prealloc()
        self.second_top_matrix = self.get_top_matrix()
        self.second_blocks_list = self.get_blocks_list()
        self.second_is_consistent = self.is_consistent(self.second_top_matrix)
        errorCond = self.calculate_schedule(self.second_top_matrix)
        if self.DEBUG:
            print "GNURADIO top matrix= "
            print self.second_top_matrix
            print "GNURADIO blocks_list= "
            print self.second_blocks_list
            print "2nd Stage topology matrix consistency= ", self.second_is_consistent        
            print "Second Stage"
            if errorCond == OK:
                print "Found Schedule"
            elif errorCond == RELAXED_NO_SOL:
                print "Relaxed LP has no solution"
            elif errorCond == INTEGER_NO_SOL:
                print "Integer problem has no soluion"
        self.print_schedule(self.first_sched)
        self.gnuradio_tb.alloc(self.cur_bufer_size)
        if self.DEBUG:
            print "Before Go"
        self.gnuradio_tb.go()
        if self.DEBUG:
            print "Before Sleep"
        time.sleep(2)
        if self.DEBUG:
            print "GOODBUY"
        self.gnuradio_tb.stop()
    def print_schedule(self, sched):
        print sched
    def calculate_schedule(self, top_matrix):
        [errorCond, self.first_sched] = setup_sched_lp(top_matrix)
        return errorCond
    def is_consistent(self, top_matrix):
        # TODO: add consistency for BDF type blocks ... such as packet decoders
        self.rankVal = np.linalg.matrix_rank(top_matrix)
        num_actors   = len(top_matrix[0])
        if self.rankVal < num_actors:
            self.top_impl_info["consistent"] = True
        else:
            self.top_impl_info["consistent"] = False
    def find_sinks(self, top_matrix, block_list):
        row = len(top_matrix)
        col = len(top_matrix[0])
        sink_conn = 0
        sink_list = []
        if self.DEBUG:
            print "Row= ", row, " Col= ", col
        for i in xrange(col):
            if self.is_sink(i, top_matrix, block_list):
                sink_list.append(i)
        if self.DEBUG:
            print "Sink List= ", sink_list
        return sink_list
    def find_sources(self, top_matrix, block_list):
        row = len(top_matrix)
        col = len(top_matrix[0])
        source_conn = 0
        source_list = []
        if self.DEBUG:
            print "Row= ", row, " Col= ", col
        for i in xrange(col):
            if self.is_source(i, top_matrix, block_list):
                source_list.append(i)
        if self.DEBUG:
            print "Source List= ", source_list
        return source_list
    def is_source(self, node, top_matrix, block_list):
        row       = len(top_matrix)
        sink_conn = 0
        for j in xrange(row):
            if top_matrix[j][node] > 0:
                if sink_conn == 1:
                    sink_conn = -1
                    return False
                else:
                    sink_conn = sink_conn + 1
            elif top_matrix[j][node] < 0:
                sink_conn = -1
                return False
        if sink_conn == 1:
            return True
        else:
            return False
    def is_sink(self, node, top_matrix, block_list):
        row       = len(top_matrix)
        sink_conn = 0
        for j in xrange(row):
            if top_matrix[j][node] < 0:
                if sink_conn == 1:
                    sink_conn = -1
                    return False
                else:
                    sink_conn = sink_conn + 1
            elif top_matrix[j][node] > 0:
                sink_conn = -1
                return False
        if sink_conn == 1:
            return True
        else:
            return False
    def get_prev_node(self, arc, top_matrix, block_list):
        col       = len(top_matrix[0])
        for j in xrange(col):
            if top_matrix[arc][j] > 0:
                return j
    def get_next_node(self, arc, top_matrix, block_list):
        col       = len(top_matrix[0])
        for j in xrange(col):
            if top_matrix[arc][j] < 0:
                return j
    def get_prev_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        prev_list   = []
        for j in xrange(row):
            if top_matrix[j][node] < 0:
                source_node = self.get_prev_node(j, top_matrix, block_list)
                prev_list.append(source_node)
    def get_next_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        next_list   = []
        for j in xrange(row):
            if top_matrix[j][node] > 0:
                source_node = self.get_next_node(j, top_matrix, block_list)
                next_list.append(source_node)
        return next_list
    # gnuradio doesn't explicitly set the relative rates between all
    # the blocks.  Therefore, we must set the appropriate relative
    # rates by traversing backwards, from sinks to a terminating
    # source and update the SECOND stage topology matrix -> the one we
    # get back from gnuradio not the one we setup from the OCCAM
    # programs which are already setup properly
    def set_rate_consistency(self, node_list, top_matrix, block_list):
        self.set_rate_consistency_helper(node_list, top_matrix, block_list)
    def set_rate_consistency_helper(self, node_list, top_matrix, block_list):
        list_len = len(node_list)
        if self.DEBUG:
            print "Next= ", node_list
        for i in xrange(list_len):
            if self.is_sink(node_list[i], top_matrix, block_list) == False:
                node_list2= self.get_next_nodes(node_list[i], top_matrix, block_list)
                self.set_rate_consistency_helper(node_list2, top_matrix, block_list)
            else:
                if self.DEBUG:
                    print "FOUND SINK"
                
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
            matrix_loc = np.zeros((row, col))
            for i in range(row):
                    for j in range(col):
                            matrix_loc[i][j] = self.gnuradio_tb.top_matrix_top(i, j)
            return copy.deepcopy(matrix_loc)
    def get_blocks_list(self):
        block_loc = []
        col = self.gnuradio_tb.top_get_number_of_blocks()
        for i in range(col):
            block_name = self.gnuradio_tb.blocks_list_top(i)
            block_loc.append(block_name)
        return copy.deepcopy(block_loc)

    def get_number_of_blocks(self):
            print "gnuradio num blocks= "
            print self.gnuradio_tb.top_get_number_of_blocks()
    def get_number_of_edges(self):
            print "gnuradio num edges= "
            print self.gnuradio_tb.top_get_number_of_edges()
