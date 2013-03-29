#!/usr/bin/env python
import sys, string, types, os, copy, time
import getopt
import numpy as np
import scipy
import fractions
import subprocess

from pylab        import *
from ptolemy_gen  import *
from gnuradio_gen import *
from lp_gen       import *
from design_check import *
import occam_parser as occam

class gnuradio_tb_handler:
    def __init__(self):
        self.gnuradio_tb         = {}
        import OCCAM_generated
        reload(OCCAM_generated)
        from OCCAM_generated import OCCAM_generated
        # set the gnuradio top block handler to the one generate
        self.gnuradio_tb = OCCAM_generated()
    def get_avg_exe_time(self, graph_handler, design_handler):
        i=0
        for block in design_handler.second_blocks_list:
            design_handler.top_impl_info[EXE][block]            = self.gnuradio_tb.get_performance_measure(i,EXE_TIME_ENUM)
            design_handler.top_impl_info[EXE_VAR][block]        = self.gnuradio_tb.get_performance_measure(i,EXE_TIME_VAR_ENUM)
            design_handler.top_impl_info[PRODUCED][block]       = self.gnuradio_tb.get_performance_measure(i,PRODUCED_ENUM)
            design_handler.top_impl_info[PRODUCED_VAR][block]   = self.gnuradio_tb.get_performance_measure(i,PRODUCED_VAR_ENUM)
            design_handler.top_impl_info[NOUTPUT][block]        = self.gnuradio_tb.get_performance_measure(i,NOUTPUT_ENUM)
            design_handler.top_impl_info[NOUTPUT_VAR][block]    = self.gnuradio_tb.get_performance_measure(i,NOUTPUT_VAR_ENUM)
            design_handler.top_impl_info[IBUFF_FULL][block]     = self.gnuradio_tb.get_performance_measure(i,IBUFF_FULL_ENUM)
            design_handler.top_impl_info[IBUFF_FULL_VAR][block] = self.gnuradio_tb.get_performance_measure(i,IBUFF_FULL_VAR_ENUM)
            design_handler.top_impl_info[OBUFF_FULL][block]     = self.gnuradio_tb.get_performance_measure(i,OBUFF_FULL_VAR_ENUM)
            design_handler.top_impl_info[OBUFF_FULL_VAR][block] = self.gnuradio_tb.get_performance_measure(i,OBUFF_FULL_VAR_ENUM)
            i = i + 1
        # Calculate and print out Throughput and Latency
        tot_latency = 0
        for block in design_handler.top_impl_info[EXE]:
            tot_latency = tot_latency + design_handler.top_impl_info[EXE][block]
            denom = design_handler.top_impl_info[EXE][block]
            if denom > 0:
                design_handler.top_impl_info[THRU][block] = design_handler.top_impl_info[PRODUCED][block]/denom
            else:
                design_handler.top_impl_info[THRU][block] = float("infinity")
        design_handler.top_impl_info[LATENCY] = tot_latency
    def memory_usage(self, graph_handler, design_handler, top_matrix):
        len_chans = len(top_matrix)
        design_handler.top_impl_info[MEM_TOT] = 0
        # initialize the memory utilization for each block as 0
        for block in design_handler.second_blocks_list:
            design_handler.top_impl_info[MEM][block] = 0
            design_handler.top_impl_info[EXE][block] = 0
        j = 0
        #print "second_blocks_list= ", self.second_blocks_list
        for block in design_handler.second_blocks_list:
            mem_cur_chan = 0
            for i in xrange(len_chans):
                #data_size       = graph_handler.gnuradio_block_io_rates[block][occam.IO_TYPE_SIZE]
                data_size       = design_handler.blocks_io[j]
                matrix_val      = top_matrix[i][j]                
                if design_handler.gnu_mem_alloc_policy == ALLOC_DEF:
                    if matrix_val > 0:
                        mem_cur_chan    = MEM_GNU_DEF
                    else:
                        mem_cur_chan    = 0
                        matrix_val      = 0                        
                elif design_handler.gnu_mem_alloc_policy == ALLOC_TOP:
                    if matrix_val > 0:
                        mem_cur_chan    = matrix_val*design_handler.token_size
                    else:
                        mem_cur_chan    = 0
                        matrix_val      = 0
                design_handler.top_impl_info[MEM][block] = design_handler.top_impl_info[MEM][block]+mem_cur_chan
                design_handler.top_impl_info[MEM_TOT]     = design_handler.top_impl_info[MEM_TOT]+ mem_cur_chan
            j = j + 1
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
    def set_gnuradio_firing_vector(self, design_handler):
            col = self.gnuradio_tb.top_get_number_of_blocks()
            for i in range(col):
                val_temp = design_handler.second_sched[i]
                self.gnuradio_tb.set_blocks_firing(i, int(val_temp))
    def set_gnuradio_top_matrix(self, design_handler):
            row = self.gnuradio_tb.top_get_number_of_edges()
            col = self.gnuradio_tb.top_get_number_of_blocks()
            #matrix_loc = np.zeros((row, col))
            for i in range(row):
                    for j in range(col):
                        self.gnuradio_tb.set_top_matrix(i, j, design_handler.second_top_matrix[i][j])
            #return copy.deepcopy(matrix_loc)
#    def setup_visited_matrix(self):
#            row = self.gnuradio_tb.top_get_number_of_edges()
#            col = self.gnuradio_tb.top_get_number_of_blocks()
#            self.visited_matrix = np.zeros((row, col))
    def get_blocks_list(self):
        block_loc = []
        col = self.gnuradio_tb.top_get_number_of_blocks()
        for i in range(col):
            block_name = self.gnuradio_tb.blocks_list_top(i)
            block_loc.append(block_name)
        return copy.deepcopy(block_loc)
    def get_blocks_io(self, design_handler):
        block_loc = []
        col = self.gnuradio_tb.top_get_number_of_blocks()
        i = 0
        for i in xrange(col):
            ret_val = design_handler.is_sink(i, design_handler.second_top_matrix, design_handler.second_blocks_list)
            if ret_val[TUP_COND]:
                block_io = 0
            else:
                block_io = self.gnuradio_tb.get_block_io(i, 0)
            block_loc.append(block_io)
        return copy.deepcopy(block_loc)        
    def get_number_of_blocks(self):
            print "gnuradio num blocks= "
            print self.gnuradio_tb.top_get_number_of_blocks()
    def get_number_of_edges(self):
            print "gnuradio num edges= "
            print self.gnuradio_tb.top_get_number_of_edges()
