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

TUP_COND = 0
TUP_RATE = 1
TUP_ID   = 2
TUP_ARC  = 3
TUP_INIT = (False, 0.0, 0, 0)
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
        self.visited_matrix       = np.zeros((1,1))
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
        self.setup_visited_matrix()
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
                return [True, -top_matrix[arc][j], j, arc_list]
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
                print "SUCCESS get_next_node"
                return [True, -top_matrix[arc][j], j, arc_list]
        print "FAIL get_next_node"
        return TUP_INIT
    def get_next_nodes(self, node, top_matrix, block_list):
        row         = len(top_matrix)
        sink_conn   = 0
        source_node = 0
        next_list   = []
        node_id     = node[TUP_ID]
        print "get_next_nodes= ", node
        for j in xrange(row):
            if top_matrix[j][node_id] > 0:
                # This get_next_node will only generate the next node
                # on the specified arc
                source_node = self.get_next_node(j, top_matrix, block_list)
                print "source_node[i]= ", source_node
                arc_list    = self.get_node_arcs(source_node[TUP_ID], top_matrix, block_list)
                arc_len     = len(arc_list)
                print "arc list= ", arc_list
                for k in xrange(arc_len):
                    source_node[TUP_ARC] = arc_list[k]
                    next_list.append(source_node)
        #node_id     = node[TUP_ID]
        #node_arc    = node[TUP_ARC]
        #source_node = self.get_next_node(node_arc, top_matrix, block_list)      
        #next_list.append(source_node)
        #next_list = self.get_next_node(node_arc, top_matrix, block_list)      
        print "next_list= ", next_list
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
                print "prev nodes= ", source_node
                print "visited= ",
                print self.visited_matrix
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
         print "node_id= ", node_id, " node_arc= ", node_arc
         old_rate = top_matrix[node_arc][node_id]
         print "OLD RATE= ", old_rate
         self.visited_matrix[node_arc][node_id] = 1
         top_matrix[node_arc][node_id] = rate
         # setup the corresponding input arc for the next node
         ret_is = self.get_next_node(node_arc, top_matrix, block_list)
         print "Set new rate for Node= ", node, " arc= ", node_arc, " old rate= ", old_rate, " new_rate= ", rate
         print "ret_is= ", ret_is
         ret_len = len(ret_is)
         print "ret len= ", ret_len
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
        for i in xrange(list_len):
            node_rate = node_list[i][TUP_RATE]
            # If we never been to this node before
            if self.visited_matrix[i][node_list[i][TUP_ARC]] == 0:
                self.visited_matrix[i][node_list[i][TUP_ARC]] = 1
                cur_rate  = cur_rate * node_rate
                print "cur_rate= ", cur_rate
                print "node_list[i]= ", node_list[i]
                self.set_new_node_relative_rate(node_list[i], cur_rate, top_matrix, block_list)
                ret_is = self.is_sink(node_list[i][TUP_ID], top_matrix, block_list)
                if ret_is[TUP_COND]  == False:
                    node_list2= self.get_next_nodes(node_list[i], top_matrix, block_list)
                    list2_len = len(node_list2)
                    print "node_list21= ", node_list2
                    # run for a second time to get the outgoing rate of
                    # the next node and not the incoming one
                    print "node_list2= ", node_list2, " len= ", list2_len
                    for j in xrange(list2_len):
                        ret_is = self.is_sink(node_list2[j][TUP_ID], top_matrix, block_list)
                        if ret_is[TUP_COND]  == False:
                            print "node_list2= ", node_list2
                            node_list3= self.get_next_node(node_list2[0][TUP_ARC], top_matrix, block_list)
                            print "node_list3= ", node_list3
                            node_list2[0][TUP_RATE] = node_list3[TUP_RATE]
                            #if (node_list[i][TUP_ID] >= 12 and node_list[i][TUP_ID] <= 13):
                        #    print "node# is= ", node_list[i][TUP_ID]
                        self.set_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate, node_list[i])
                    else:
                        if self.DEBUG:
                            print "FOUND SINK"
            # If we visited this node before we need to ensure that
            # the expected relative rate from this iteration is the
            # same as the one we're finding.  If not then we need to
            # calculate a common multiple factor and trigger a revised
            # relative rate calculation going backwards through the
            # previously traversed paths
            '''
            else:
                node_rate = node_list[i][TUP_RATE]
                print "Previously visited node= ", node_list[i][TUP_ID] 
                print "prev_rate= ", node_rate, " cur_rate= ", cur_rate
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
                    print "cf1= ", cf_1, " cf2= ", cf_2
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
                            print "cf1 fix node= ", prev_nodes[i]
                            self.set_rev_rate_consistency_helper(prev_nodes[i], top_matrix,block_list, cf_1)
                    if cf_2 != 1:
                        print "cf2 fix node= ", prev_path
                        self.set_rev_rate_consistency_helper([prev_path], top_matrix,block_list, cf_2)
                '''
        #next_node = self.get_next_node(self, arc, top_matrix, block_list)
    # traverse in reverse mode to fix inconsistency
    def set_rev_rate_consistency_helper(self, node_list, top_matrix, block_list, cf):
        list_len  = len(node_list)
        ret_is    = TUP_INIT
        node_rate = 1.0
        print "list_len= ", list_len
        for i in xrange(list_len):
            node_rate = node_list[i][TUP_RATE]
            cur_rate  = cf * node_rate
            print "new cur rate= ", cur_rate
            self.set_new_node_relative_rate(node_list[i], cur_rate, top_matrix, block_list)
            # since traversing backwards make sure that node is not a
            # source node
            ret_is = self.is_source(node_list[i][TUP_ID], top_matrix, block_list)
            print "check if source node"
            if ret_is[TUP_COND]  == False:
                print "find prev for= ", node_list[i][TUP_ID]
                node_list2= self.get_prev_visited_nodes(node_list[i][TUP_ID], top_matrix, block_list)
                print "new list of prev visited= ", node_list2
                # run for a second time to get the outgoing rate of
                # the next node and not the incoming one
                ret_is = self.is_source(node_list2[0][TUP_ID], top_matrix, block_list)
                if ret_is[TUP_COND]  == False:
                    node_list3= self.get_prev_visited_nodes(node_list2[0][TUP_ID], top_matrix, block_list)
                    node_list2[0][TUP_RATE] = node_list3[0][TUP_RATE]
                    self.set_rev_rate_consistency_helper(node_list2, top_matrix, block_list, cur_rate)
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
