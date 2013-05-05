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
import occam_parser as occam
import datetime

TUP_COND = 0
TUP_RATE = 1
TUP_ID   = 2
TUP_ARC  = 3
TUP_INIT = (False, 0.0, 0, 0)

ALLOC_DEF = 0
ALLOC_TOP = 1

INT       = 4
DOUBLE    = 4
SHORT     = 2
CHAR      = 1
IMAG      = 2*2 # short*2
MEM_GNU_DEF = 32*1024

MEM            = 'memory'
MEM_TOT        = 'memory_total'
CONSISTENT     = 'consistent'
LATENCY        = 'latency'
THRU           = 'throughput'
EXE            = 'execution_time'
EXE_VAR        = 'execution_time_var'
PRODUCED       = 'produced'
PRODUCED_VAR   = 'produced_var'
NOUTPUT        = 'noutput'
NOUTPUT_VAR    = 'noutput_var'
IBUFF_FULL     = 'input_buffer_fullness'
IBUFF_FULL_VAR = 'input_buffer_fullness_var'
OBUFF_FULL     = 'output_buffer_fullness'
OBUFF_FULL_VAR = 'output_buffer_fullness_var'
CONFIG_TIME    = 'configuration_time'
NOUTPUT_ENUM            = 0
NOUTPUT_VAR_ENUM        = 1
NPRODUCED_ENUM          = 2
NPRODUCED_VAR_ENUM      = 3
OUTPUT_BUFF_ENUM        = 4
OUTPUT_BUFF_VAR_ENUM    = 5
WORK_TIME_ENUM          = 6
WORK_TIME_VAR_ENUM      = 7

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
        self.run_time     = 1
        self.vect_factor  = 1
        self.token_size_orig = 1024
        self.first_is_consistent = False        
        self.first_sched         = []
        self.infile_name         = 'None'
        self.ofile_name          = 'None'
        self.second_top_matrix    = np.zeros((1,1))
        self.visited_matrix       = np.zeros((1,1))
        self.second_blocks_list   = []
        self.second_is_consistent = False
        self.second_sched         = []
        self.gnu_mem_alloc_policy = ALLOC_DEF
        # blocks to be excluded in latency calculation
        self.latency_ref          = {
            'csp-sdf-sim.occ' : ['noise_source0', 'multiply_const_vcc0'],
            'csp-sdf-rx.occ'  : [],
            'csp-sdf-tx.occ'  : []
            }
        # block to be used in calculating flowgraph throughput
        self.throughput_ref       = {
            'csp-sdf-sim.occ' : 'message_source1',
            'csp-sdf-rx.occ'  : 'multiply_const_vcc1',
            'csp-sdf-tx.occ'  : 'multiply_const_vcc1'
            }
        self.top_impl_info = {
                              # whether a graph is consistent or not
                              CONSISTENT     : False,
                              #Dictionary with each block output
                              #buffer memory usage
                              MEM            : {},
                              #total output buffer memory consumption
                              MEM_TOT        : 0,
                              EXE            : {},
                              EXE_VAR        : {},
                              PRODUCED       : {},
                              PRODUCED_VAR   : {},
                              NOUTPUT        : {},
                              NOUTPUT_VAR    : {},
                              IBUFF_FULL     : {},
                              IBUFF_FULL_VAR : {},
                              OBUFF_FULL     : {},
                              OBUFF_FULL_VAR : {},
                              LATENCY        : 0,
                              THRU           : 0,
                              CONFIG_TIME    : 0
                          }
        self.DEBUG = False
    def setup_gnuradio_handle(self):
            import OCCAM_generated
            reload(OCCAM_generated)
            from OCCAM_generated import OCCAM_generated
            # set the gnuradio top block handler to the one generated
            self.gnuradio_tb = OCCAM_generated()
    def print_top_impl_info_file(self):
        print "WRTITE TO FILE= ", self.ofile_name
        ofile_handler = open(self.ofile_name, 'w')
        data_str      = self.infile_name+"\n"
        ofile_handler.write(data_str)
        data_str      = str(datetime.datetime.now())+"\n"
        ofile_handler.write(data_str)
        data_str      = "token_size_orig = " + str(self.token_size_orig)+"\n"
        ofile_handler.write(data_str)
        data_str      = "vect_factor = " + str(self.vect_factor)+"\n"
        ofile_handler.write(data_str)
        data_str      = "run_time = " + str(self.run_time)+"\n"
        ofile_handler.write(data_str)
        data_str      = CONFIG_TIME + " = " + str(self.top_impl_info[CONFIG_TIME])+"\n"
        ofile_handler.write(data_str)
        data_str      = MEM_TOT + " = " + str(self.top_impl_info[MEM_TOT]) + "\n"
        ofile_handler.write(data_str)
        data_str      = LATENCY + " = " + str(self.top_impl_info[LATENCY]) + "\n"
        ofile_handler.write(data_str)
        data_str      = THRU + " = " + str(self.top_impl_info[THRU]) + "\n"
        ofile_handler.write(data_str)
        data_str      = "ALL" + " = "+ "\n"
        ofile_handler.write(data_str)
        for item in self.top_impl_info.keys():
            data_str = "\n"+item+"\n"
            ofile_handler.write(data_str)
            if item is not MEM_TOT and item is not CONSISTENT and item is not LATENCY and item is not THRU and item is not CONFIG_TIME:
                for block in self.top_impl_info[item]:
                    data_str = "\t " + block + " = " + str(self.top_impl_info[item][block])+"\n"
                    ofile_handler.write(data_str)
            else:
                data_str = "\t " + block + " = " + str(self.top_impl_info[item])+"\n"
                ofile_handler.write(data_str)
        ofile_handler.write(data_str)
       
        j=0 
        for block in self.second_blocks_list:
             data_str=block+" IO-SIG= "+str(self.gnuradio_tb.get_block_io(j))
             ofile_handler.write(data_str)
             j = j + 1
        data_str      = "Second Topology Matrix= \n" + str(self.second_top_matrix)
        ofile_handler.write(data_str)
        data_str      = "\nSecond Blocks List= \n" + str(self.second_blocks_list)
        ofile_handler.write(data_str)
        ofile_handler.close()
    def print_top_impl_info(self):
        for item in self.top_impl_info.keys():
            print "\n", item, "\n"
            if item is not MEM_TOT and item is not CONSISTENT and item is not LATENCY and item is not THRU:
                for block in self.top_impl_info[item]:
                    #print '{0:10} ==> {1:30d}'.format(name, phone)
                    print '\t', '{0:30} = {1:10}'.format(block, self.top_impl_info[item][block])
                    #print repr(" ").rjust(1), repr(block).rjust(2), repr("= ").rjust(9), repr(self.top_impl_info[item][block]).rjust(10)
            else:
                print '\t', '{0:30} = {1:10}'.format(item, self.top_impl_info[item])
    #Calculates the memory usage of each block and accumulate the
    #total memory usage for reference
    def is_uhd_channel(self, top_matrix, channel_id):
        num_blocks = len(top_matrix[0])
        for i in xrange(num_blocks):
            if np.abs(top_matrix[channel_id][i]) > 0.0:
                if 'uhd' in self.second_blocks_list[i]:
                    print "INSIDE UHD CHAN= ", self.second_blocks_list[i], " matrix[",channel_id,",",i,"]= ", top_matrix[channel_id][i]
                    return 1
        return 0
    def memory_usage(self, graph_handler, top_matrix):
        len_chans = len(top_matrix)
        self.top_impl_info[MEM_TOT] = 0
        # initialize the memory utilization for each block as 0
        for block in self.second_blocks_list:
            self.top_impl_info[MEM][block] = 0
            self.top_impl_info[EXE][block] = 0
        j = 0
        for block in self.second_blocks_list:
            mem_cur_chan = 0
            for i in xrange(len_chans):
                data_size       = self.gnuradio_tb.get_block_io(j)
                matrix_val      = top_matrix[i][j]                
                if self.gnu_mem_alloc_policy == ALLOC_DEF:
                    if matrix_val > 0:
                        # GNU Radio allocates the buffers to be 2*32KB 
                        mem_cur_chan    = MEM_GNU_DEF*2
                    else:
                        mem_cur_chan    = 0
                        matrix_val      = 0                        
                elif self.gnu_mem_alloc_policy == ALLOC_TOP:
                    if matrix_val > 0:
                        if self.is_uhd_channel(top_matrix, i):
                            print 'UHD CHAN= ', i
                            temp_mem = matrix_val*self.token_size*data_size
                            temp_mem = np.ceil(np.log(temp_mem)/np.log(2))
                            mem_cur_chan    = 2**temp_mem
                        else:
                            mem_cur_chan    = matrix_val*self.token_size*data_size
                    else:
                        mem_cur_chan    = 0
                        matrix_val      = 0
                self.top_impl_info[MEM][block] = self.top_impl_info[MEM][block]+mem_cur_chan
                self.top_impl_info[MEM_TOT]     = self.top_impl_info[MEM_TOT]+ mem_cur_chan
            j = j + 1
    def get_avg_exe_time(self, graph_handler):
        i=0
        self.memory_usage(graph_handler, self.second_top_matrix)
        for block in self.second_blocks_list:
            self.top_impl_info[EXE][block]            = self.gnuradio_tb.get_pc_performance_metric(WORK_TIME_ENUM, i)
            self.top_impl_info[EXE_VAR][block]        = self.gnuradio_tb.get_pc_performance_metric(WORK_TIME_VAR_ENUM, i)
            self.top_impl_info[PRODUCED][block]       = self.gnuradio_tb.get_pc_performance_metric(NPRODUCED_ENUM, i)
            self.top_impl_info[PRODUCED_VAR][block]   = self.gnuradio_tb.get_pc_performance_metric(NPRODUCED_VAR_ENUM, i)
            self.top_impl_info[NOUTPUT][block]        = self.gnuradio_tb.get_pc_performance_metric(NOUTPUT_ENUM, i)
            self.top_impl_info[NOUTPUT_VAR][block]    = self.gnuradio_tb.get_pc_performance_metric(NOUTPUT_VAR_ENUM, i)
            self.top_impl_info[OBUFF_FULL][block]     = self.gnuradio_tb.get_pc_performance_metric(OUTPUT_BUFF_ENUM, i)
            self.top_impl_info[OBUFF_FULL_VAR][block] = self.gnuradio_tb.get_pc_performance_metric(OUTPUT_BUFF_VAR_ENUM, i)
            i = i + 1
        # Calculate and print out Throughput and Latency
        self.calculate_latency()
        self.calculate_throughput()
    def calculate_latency(self):
        tot_latency = 0        
        for block in self.top_impl_info[EXE]:
            if self.is_block_in_list(block, self.latency_ref[self.infile_name]) == False:
                tot_latency = tot_latency + self.top_impl_info[EXE][block]
        self.top_impl_info[LATENCY] = tot_latency
    def calculate_throughput(self):
        block = self.throughput_ref[self.infile_name]
        thru  = self.top_impl_info[PRODUCED][block]/self.top_impl_info[EXE][block]
        self.top_impl_info[THRU] = thru
    def is_block_in_list(self, block, block_list):
        for block_it in block_list:
            if block in block_list:
                return True
        return False
    def setup_design_constraint(self, name_val, range_val):
        self.design_constraints[name_val] = range_val
    def print_design_constraints(self):
        print "Design Constraints= "
        print self.design_constraints
        self.print_top_impl_info()
    def first_stage_topology_test(self, graph_handler, top_matrix):
        # calculate the 1st level topology matrix and constraints
        [errorCond, self.first_sched] = self.calculate_schedule(top_matrix)
        self.setup_gnuradio_handle()
        self.first_is_consistent = self.is_consistent(top_matrix)
        #self.memory_usage(graph_handler, top_matrix)
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
    def second_stage_topology_test(self, graph_handler, top_matrix):
        #self.top_impl_info[CONFIG_TIME]
        start_time = 0.0
        elapse_time = 0.0
        start_time = time.time()
        self.gnuradio_tb.prealloc()
        elapse_time = time.time()-start_time
        self.second_top_matrix = self.get_gnuradio_top_matrix()
        #print "1st Second Top Matrix= \n", self.second_top_matrix
        self.setup_visited_matrix()
        self.second_blocks_list = self.get_blocks_list()
        #print "second blocks_list= "
        #print self.second_blocks_list
        source_list             = self.find_sources(self.second_top_matrix, self.second_blocks_list)
        #print "Source List= ", source_list
        self.set_rate_consistency(source_list, self.second_top_matrix, self.second_blocks_list)
        self.second_is_consistent = self.is_consistent(self.second_top_matrix)
        print "2nd Second Top Matrix= \n", self.second_top_matrix
        [errorCond, self.second_sched] = self.calculate_schedule(self.second_top_matrix)
        if self.DEBUG:
            print "GNURADIO top matrix= "
            print self.second_top_matrix
            print "GNURADIO blocks_list= "
            print self.second_blocks_list
            print "2nd Stage topology matrix consistency= ", self.second_is_consistent        
            print "Second Stage"
            if errorCond == OK:
                print "Found Schedule"
        if errorCond == RELAXED_NO_SOL:
            print "Relaxed LP has no solution"
        elif errorCond == INTEGER_NO_SOL:
            print "Integer problem has no soluion"
        #self.print_schedule(self.first_sched)
        ############################################################
        ## GET PERFORMANCE MEASUREMENTS
        self.set_gnuradio_top_matrix()
        self.set_gnuradio_firing_vector()
        start_time = time.time()
        #self.gnuradio_tb.alloc(self.cur_bufer_size, self.gnu_mem_alloc_policy)
        #print "Before ALLOC Token size= ", self.token_size
        #print "SECOND TOP= "
        #print self.second_top_matrix
        self.gnuradio_tb.alloc(self.token_size, self.gnu_mem_alloc_policy)
        elapse_time = elapse_time+time.time()-start_time
        if self.DEBUG:
            print "Before Go"
        self.gnuradio_tb.reset_pc_performance_metric()
        time.sleep(2)
        start_time = time.time()
        self.gnuradio_tb.go()
        elapse_time = elapse_time+time.time()-start_time
        if self.DEBUG:
            print "Before Sleep"
        time.sleep(self.run_time)
        self.gnuradio_tb.set_pc_performance_metric()
        time.sleep(2)
        if self.DEBUG:
            print "GOODBUY"
        start_time = time.time()
        self.gnuradio_tb.stop()
        self.gnuradio_tb.wait()
        elapse_time = elapse_time+time.time()-start_time
        self.top_impl_info[CONFIG_TIME]=elapse_time
        self.get_avg_exe_time(graph_handler)
        time.sleep(2)
    def print_schedule(self, sched):
        print sched
    def calculate_schedule(self, top_matrix):
        #[errorCond, self.first_sched] = setup_sched_lp(top_matrix)
        return setup_sched_lp(top_matrix)
        #return errorCond
    def is_consistent(self, top_matrix):
        # TODO: add consistency for BDF type blocks ... such as packet decoders
        self.rankVal = np.linalg.matrix_rank(top_matrix)
        num_actors   = len(top_matrix[0])
        if self.rankVal < num_actors:
            self.top_impl_info[CONSISTENT] = True
        else:
            self.top_impl_info[CONSISTENT] = False
    def find_sinks(self, top_matrix, block_list):
        row = len(top_matrix)
        col = len(top_matrix[0])
        sink_conn = 0
        sink_list = []
        ret_is      = TUP_INIT
        if self.DEBUG:
            print "Row= ", row, " Col= ", col
        for i in xrange(col):
            ret_is = self.is_sink(i, top_matrix, block_list)
            if ret_is[TUP_COND]:
                sink_list.append(ret_is)
        if self.DEBUG:
            print "Sink List= ", sink_list
        return sink_list
    def find_sources(self, top_matrix, block_list):
        row = len(top_matrix)
        col = len(top_matrix[0])
        source_conn = 0
        source_list = []
        ret_is      = TUP_INIT
        if self.DEBUG:
            print "Row= ", row, " Col= ", col
        for i in xrange(col):
            ret_is = self.is_source(i, top_matrix, block_list)
            if ret_is[TUP_COND]:
                source_list.append(ret_is)
        if self.DEBUG:
            print "Source List= ", source_list
        return source_list
    # Tuple (True/False, rate)
    def is_source(self, node, top_matrix, block_list):
        row       = len(top_matrix)
        sink_conn = 0
        rate      = 0.0
        arc_list  = -1
        for j in xrange(row):
            if top_matrix[j][node] > 0:
                rate = top_matrix[j][node]
                # a source can have multiple outputs
                #if sink_conn == 1:
                #    sink_conn = -1
                #    return TUP_INIT
                #else:
                sink_conn = sink_conn + 1
                arc_list = j
            elif top_matrix[j][node] < 0:
                sink_conn = -1
                return TUP_INIT
        if sink_conn == 1:
            return [True, rate, node, arc_list]
        else:
            return TUP_INIT
        # Tuple (True/False, rate)
    def is_sink(self, node, top_matrix, block_list):
        row       = len(top_matrix)
        sink_conn = 0
        rate      = 0.0
        arc_list  = -1
        for j in xrange(row):
            if top_matrix[j][node] < 0:
                #if sink_conn == 1:
                #    sink_conn = -1
                #    return TUP_INIT
                #else:
                # a sink can have multiple input lines
                sink_conn = sink_conn + 1
                rate = top_matrix[j][node]
                arc_list = j
            elif top_matrix[j][node] > 0:
                sink_conn = -1
                return TUP_INIT
        if sink_conn == 1:
            return [True, rate, node, arc_list]
        else:
            return TUP_INIT
    def get_prev_node(self, arc, top_matrix, block_list):
        col       = len(top_matrix[0])
        arc_list  = -1
        for j in xrange(col):
            if top_matrix[arc][j] > 0:
                arc_list = arc
                return [True, top_matrix[arc][j], j, arc_list]
        print "FAIL get_prev_node"
        return TUP_INIT
    def get_node_arcs(self, node_id, top_matrix, block_list):
        row         = len(top_matrix)
        arc_list    = []
        for j in xrange(row):
            if top_matrix[j][node_id] > 0:
                arc_list.append(j)
        return arc_list
    def get_next_node(self, arc, top_matrix, block_list):
        col       = len(top_matrix[0])
        arc_list = -1
        for j in xrange(col):
            if top_matrix[arc][j] < 0:
                arc_list = arc
                return [True, -top_matrix[arc][j], j, arc_list]
        print "FAIL get_next_node"
        return TUP_INIT
    def get_next_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        next_list   = []
        node_id     = node[TUP_ID]
        for j in xrange(row):
            if top_matrix[j][node_id] > 0:
                # This get_next_node will only generate the next node
                # on the specified arc
                source_node = self.get_next_node(j, top_matrix, block_list)
                arc_list    = self.get_node_arcs(source_node[TUP_ID], top_matrix, block_list)
                arc_len     = len(arc_list)
                for k in xrange(arc_len):
                    source_node[TUP_ARC] = arc_list[k]
                    next_list.append(source_node)
        return next_list
    def get_prev_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        prev_list   = []
        for j in xrange(row):
            if top_matrix[j][node] < 0:
                source_node = self.get_prev_node(j, top_matrix, block_list)
                prev_list.append(source_node)
        return prev_list
    def get_prev_visited_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        prev_list   = []
        for j in xrange(row):
            if top_matrix[j][node] < 0:                
                source_node = self.get_prev_node(j, top_matrix, block_list)
                if self.visited_matrix[j][node] == 1:
                    prev_list.append(source_node)
        return prev_list
    def find_parent_node(self, node, top_matrix, block_list):
        list_temp  = []
        list_temp2 = []
        ret_is     = TUP_INIT
        if (type(node) != type(list_temp)):
            node_len = 1
        else:
            node_len  = len(node)
        if node_len > 1:
            for i in xrange(node_len):
                list_temp.extend(self.find_parent_node(node[i], top_matrix, block_list))
        else:
            ret_is = self.is_source(node, top_matrix, block_list)
            if ret_is[TUP_COND]:
                return node
            else:
                prev_nodes = self.get_prev_nodes(node, top_matrix, block_list)
                list_temp.extend(self.find_parent_node(prev_nodes, top_matrix, block_list))
        return list_temp

    def set_new_node_relative_rate(self, node, rate, top_matrix, block_list):
        #row_len = len(top_matrix)
        #for i in xrange(row_len):
            #if top_matrix[i][node] > 0:
                # configure the rate of the output arc
         node_id  = node[TUP_ID]
         node_arc = node[TUP_ARC]
         old_rate = top_matrix[node_arc][node_id]
         self.visited_matrix[node_arc][node_id] = 1
         top_matrix[node_arc][node_id] = rate
         # setup the corresponding input arc for the next node
         ret_is = self.get_next_node(node_arc, top_matrix, block_list)
         ret_len = len(ret_is)
         for i in xrange(ret_len):
             top_matrix[node_arc][ret_is[TUP_ID]] = -rate
             self.visited_matrix[node_arc][ret_is[TUP_ID]] = 1
        #print "AFTER"
        #print top_matrix
    # gnuradio doesn't explicitly set the relative rates between all
    # the blocks.  Therefore, we must set the appropriate relative
    # rates by traversing backwards, from sinks to a terminating
    # source and update the SECOND stage topology matrix -> the one we
    # get back from gnuradio not the one we setup from the OCCAM
    # programs which are already setup properly
    def set_rate_consistency(self, node_list, top_matrix, block_list):
        cur_rate = 1.0
        #print "TOP MATRIX= "
        #print self.second_top_matrix
        self.set_rate_consistency_helper(node_list, top_matrix, block_list, cur_rate, TUP_INIT)
    def set_rate_consistency_helper(self, node_list, top_matrix, block_list, cur_rate, prev_path):
        # NOTES WHERE I LEFT:
        # 1- Set a separate matrix for the original rates from
        # gnuradio
        # 2- set a second matrix to indicate whether or not you've
        # visited an arc
        # 3- Remove the hardcoded stop at initial graph ... renable to 12->13
        # 4- set flag to indicate rate mismatch so you can iterate
        # through for a second time to fix the second 12->13 branch
        list_len  = len(node_list)
        ret_is    = TUP_INIT
        node_rate = 1.0
        #print "Node List= ", node_list
        for i in xrange(list_len):
            #print "node_list= ", node_list[i], " visited= ", self.visited_matrix[node_list[i][TUP_ARC]][node_list[i][TUP_ID]], " ARC= ", node_list[i][TUP_ARC]
            #print "Visited Matrix =\n", self.visited_matrix
            #print "Top Matrix =\n", self.second_top_matrix
            node_rate = node_list[i][TUP_RATE]
            # If we never been to this node before
            if self.visited_matrix[node_list[i][TUP_ARC]][node_list[i][TUP_ID]] == 0:
                # If no rate change or if we found an interpolation block
                #if node_rate >= 1:
                if cur_rate * node_rate >= 1:
                    self.visited_matrix[node_list[i][TUP_ARC]][node_list[i][TUP_ID]] = 1
                    cur_rate  = cur_rate * node_rate
                    #print "Cur Rate= ", cur_rate, " Node Rate= ", node_rate, #" Top MAtrix= \n", top_matrix                
                    self.set_new_node_relative_rate(node_list[i], cur_rate, top_matrix, block_list)
                    ret_is = self.is_sink(node_list[i][TUP_ID], top_matrix, block_list)
                    if ret_is[TUP_COND]  == False:
                        node_list2= self.get_next_nodes(node_list[i], top_matrix, block_list)
                        #print "Next Nodes= ", node_list2
                        list2_len = len(node_list2)
                        # run for a second time to get the outgoing rate of
                        # the next node and not the incoming one
                        for j in xrange(list2_len):
                            # print "Cur Top MAtrix= \n", top_matrix
                            ret_is = self.is_sink(node_list2[j][TUP_ID], top_matrix, block_list)
                            if ret_is[TUP_COND]  == False:
                                node_list3= self.get_next_node(node_list2[0][TUP_ARC], top_matrix, block_list)
                                node_list2[0][TUP_RATE] = node_list3[TUP_RATE]
                            self.set_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate, node_list[i])
                        else:
                            if self.DEBUG:
                                print "FOUND SINK"
                # If we found a decimation block then we don't want to
                # use fraction representation so go in reverse and
                # multiple by 1/decimation to make the final decimated
                # rate = 1
                else:
                    #print "Found decimation block = ", node_list[i][TUP_ID]
                    cf  = cur_rate * (1/node_rate)
                    temp_rate = 1.0
                    self.set_new_node_relative_rate(node_list[i], temp_rate, top_matrix, block_list)
                    prev_nodes= self.get_prev_visited_nodes(node_list[i][TUP_ID], top_matrix, block_list)
                    list_len2 = len(prev_nodes)
                    #print "Prev Nodes= ", prev_nodes, " list len2 = ", list_len2
                    # for i in xrange(list_len2):
                    self.set_rev_rate_consistency_helper(prev_nodes, top_matrix,block_list, cf)
            # If we visited this node before we need to ensure that
            # the expected relative rate from this iteration is the
            # same as the one we're finding.  If not then we need to
            # calculate a common multiple factor and trigger a revised
            # relative rate calculation going backwards through the
            # previously traversed paths
            
            else:
                node_rate = node_list[i][TUP_RATE]
                if node_rate == cur_rate:
                    if self.DEBUG:
                        print "Rate Match"
                else:
                    # calculate a common relative rate in case of a
                    # rate mismatch
                    temp_rate  = self.least_common_mult([cur_rate, node_rate])
                    # calculate the correction factor for already
                    # traversed nodes
                    cf_1 = temp_rate/node_list[i][TUP_RATE]
                    # Calculate the correction factor for the previous
                    # node which caused the rate mismatch
                    cf_2 = temp_rate/prev_path[TUP_RATE]
                    # set the new corrected relative rate to the matrix
                    self.set_new_node_relative_rate(node_list[i], temp_rate, top_matrix, block_list)
                    # now traverse the previosuly visited nodes to
                    # correct their relative rates by the necessary
                    # correction factor.  If correction factor = 1
                    # then there is no need to traverse the previous
                    # nodes since it means they already have the
                    # correct relative rates set already
                    if cf_1 != 1:
                        prev_nodes= self.get_prev_visited_nodes(node_list[i][TUP_ID], top_matrix, block_list)
                        list_len2 = len(prev_nodes)
                        for i in xrange(list_len2):
                            self.set_rev_rate_consistency_helper(prev_nodes[i], top_matrix,block_list, cf_1)
                    if cf_2 != 1:
                        #print self.second_top_matrix
                        self.set_rev_rate_consistency_helper([prev_path], top_matrix,block_list, cf_2)
        #print "Cur Top MAtrix= \n", top_matrix
        #next_node = self.get_next_node(self, arc, top_matrix, block_list)
    # traverse in reverse mode to fix inconsistency
    def set_rev_rate_consistency_helper(self, node_list, top_matrix, block_list, cf):
        #print "WHY ARE YOU REVERSING"
        list_len  = len(node_list)
        ret_is    = TUP_INIT
        node_rate = 1.0
        for i in xrange(list_len):
            #print "Node list= ", node_list, " list len= ", list_len
            #print "Node List i = ", node_list[i]
            node_rate = node_list[i][TUP_RATE]
            cur_rate  = cf * node_rate
            self.set_new_node_relative_rate(node_list[i], cur_rate, top_matrix, block_list)
            # since traversing backwards make sure that node is not a
            # source node
            ret_is = self.is_source(node_list[i][TUP_ID], top_matrix, block_list)
            if ret_is[TUP_COND]  == False:
                node_list2= self.get_prev_visited_nodes(node_list[i][TUP_ID], top_matrix, block_list)
                self.set_rev_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate)                
                # run for a second time to get the outgoing rate of
                # the next node and not the incoming one
                #ret_is = self.is_source(node_list2[0][TUP_ID], top_matrix, block_list)
                #if ret_is[TUP_COND]  == False:
                #    node_list3= self.get_prev_visited_nodes(node_list2[0][TUP_ID], top_matrix, block_list)
                #    node_list2[0][TUP_RATE] = node_list3[0][TUP_RATE]
                #    self.set_rev_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate)
                #else:
                #    self.set_rev_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate)
    def least_common_mult(self, num_list):
        return self.find_lcm([], num_list)
    def find_lcm(self, one, two):
        list_len = len(two)
        if list_len > 1:
            return self.find_lcm(two[0], two[1:])
        else:
            return ((one*two[0])/fractions.gcd(one, two[0]))
    #######################################################################
    #######################################################################
    # GNURADIO specific methods
    #######################################################################
    #######################################################################
    def print_gnuradio_top_matrix(self):
        self.gnuradio_tb.print_top_matrix()
    def print_gnuradio_firing_vector(self):
        self.gnuradio_tb.print_blocks_firing()
    def get_work_time(self):
            tinfo = self.gnuradio_tb.blocks_add_xx_0.pc_work_time()
            print "tinfo= ", tinfo
    def get_buffer_full(self):
            print "Buffer Full perc="
            print self.gnuradio_tb.blocks_add_xx_0.pc_output_buffers_full()
    def get_gnuradio_top_matrix(self):
            row = self.gnuradio_tb.top_get_number_of_edges()
            col = self.gnuradio_tb.top_get_number_of_blocks()
            matrix_loc = np.zeros((row, col))
            for i in range(row):
                    for j in range(col):
                            matrix_loc[i][j] = self.gnuradio_tb.top_matrix_top(i, j)
            return copy.deepcopy(matrix_loc)
    def set_gnuradio_firing_vector(self):
            col = self.gnuradio_tb.top_get_number_of_blocks()
            for i in range(col):
                val_temp = self.second_sched[i]
                self.gnuradio_tb.set_blocks_firing(i, int(val_temp))
    def set_gnuradio_top_matrix(self):
            row = self.gnuradio_tb.top_get_number_of_edges()
            col = self.gnuradio_tb.top_get_number_of_blocks()
            matrix_loc = np.zeros((row, col))
            for i in range(row):
                    for j in range(col):
                        self.gnuradio_tb.set_top_matrix(i, j, self.second_top_matrix[i][j])
            return copy.deepcopy(matrix_loc)
    def setup_visited_matrix(self):
            row = self.gnuradio_tb.top_get_number_of_edges()
            col = self.gnuradio_tb.top_get_number_of_blocks()
            self.visited_matrix = np.zeros((row, col))
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
