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
from occam_parser import *

import occam_parser as occam

class ce_interface:
    def __init__(self):
        self.out_file_vect = []
        self.token_vect    = []
        self.alloc_vect    = []
        self.vect_vect     = []
        self.run_vect      = []
        
        self.mem_vect_top      = []
        self.lat_vect_top      = []
        self.thru_vect_top     = []
        self.mem_vect_def      = []
        self.lat_vect_def      = []
        self.thru_vect_def     = []
        
        self.i_cur         = 0 

    def visualize_performance_results(self):
        len_vect      = len(self.thru_vect_top)
        vect_vect_loc = []
        for i in xrange(len_vect-1):
            self.lat_vect_def.extend([self.lat_vect_def[i]])
            self.mem_vect_def.extend([self.mem_vect_def[i]])
            self.thru_vect_def.extend([self.thru_vect_def[i]])
            vect_vect_loc.extend([self.vect_vect[i+1]])

        vect_vect_loc.extend([self.vect_vect[len_vect]])

        # save data to special folder
        '''
        folder_name = str(datetime.datetime.now())
        if os.path.exsists(folder_name):
            # in the off chance another directory was created at the
            # same exact moment
            folder_name = folder_name+folder_name
        os.path.mkdir(folder_name)

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
        data_str      = MEM_TOT + " = " + str(self.top_impl_info[MEM_TOT]) + "\n"
        ofile_handler.write(data_str)
        data_str      = LATENCY + " = " + str(self.top_impl_info[LATENCY]) + "\n"
        ofile_handler.write(data_str)
        data_str      = THRU + " = " + str(self.top_impl_info[THRU]) + "\n"
        ofile_handler.write(data_str)
        ofile_handler.close()
        '''
        #############################################################################
        # Latency Plot
        #############################################################################
        
        figure(0)
        plot(vect_vect_loc, self.lat_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.lat_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.lat_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.lat_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Latency (sec)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.lat_vect_top))
        max_def = ceil(max(self.lat_vect_def))
        max_both = max(max_top, max_def)
        ylim(0.0, max_both)        
        savefig("latency.png", dpi=300)
        
        #############################################################################
        # Memory Plot
        #############################################################################
        figure(1)
        print "vect_vect= ", vect_vect_loc
        print "mem_vect_def= ", self.mem_vect_def
        print "mem_vect_top= ", self.mem_vect_top
        plot(vect_vect_loc, self.mem_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.mem_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.mem_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.mem_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Memory (bytes)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.mem_vect_top))
        max_def = ceil(max(self.mem_vect_def))
        max_both = max(max_top, max_def)*1.4
        min_top = ceil(min(self.mem_vect_top))
        min_def = ceil(min(self.mem_vect_def))
        min_both = min(min_top, min_def)
        ylim(0, max_both)
        savefig("memory.png", dpi=300)
        #############################################################################
        # Throughput Plot
        #############################################################################
        figure(2)
        plot(vect_vect_loc, self.thru_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.thru_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.thru_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.thru_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Throughput (bytes/sec)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.thru_vect_top))
        max_def = ceil(max(self.thru_vect_def))
        max_both = max(max_top, max_def)
        max_both = max_both*1.3
        min_top = ceil(max(self.thru_vect_top))
        min_def = ceil(max(self.thru_vect_def))
        min_both = min(min_top, min_def)
        min_both = min_both/1.3
        ylim(min_both, max_both)
        savefig("throughput.png", dpi=300)
        show()        
    def set_ranges(self, vect_range):
        self.vect_range
    def add_data_point(self, file_name, mem_vect_local, lat_vect_local, thru_vect_local):
        sanity_check  = 0
        ifile_handler = open(file_name, 'r')
        line          = ifile_handler.readline()
        tokens        = line.split()
        while line:
            if "memory_total" in line:
                sanity_check = sanity_check + 1
                mem_vect_local.extend([float(tokens[2])])
            elif "latency" in line:
                sanity_check = sanity_check + 1
                lat_vect_local.extend([float(tokens[2])])
            elif "throughput" in line:
                sanity_check = sanity_check + 1
                thru_vect_local.extend([float(tokens[2])])
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
    vectorization_times = 5
    run_time_duration   = 60
    token_size_size     = 2048

    ce_handler    = ce_interface()

    ce_handler.vect_vect     = range(vectorization_times)
    len_range                = len(ce_handler.vect_vect)
    for i in xrange(len_range):
        ce_handler.out_file_vect.extend(["temp"+str(i)+".dat"])
        if i is 0:
            ce_handler.alloc_vect.extend([0])
        else:
            ce_handler.alloc_vect.extend([1])

    token_size    = str(token_size_size)
    in_file_name  = "csp-sdf-sim.occ"
    run_time      = str(run_time_duration)
    for i in xrange(len_range):
        out_file_name = ce_handler.out_file_vect[i]
        vect_fact = str(ce_handler.vect_vect[i])
        alloc_policy = str(ce_handler.alloc_vect[i])
        
        command_str = "./design_interface.py -t "+token_size+" -l "+vect_fact+" -a "+alloc_policy+ " -r "+run_time+" -o "+out_file_name+" -i "+in_file_name
        #os.system(command_str)

        if i is 0:
            ce_handler.add_data_point(out_file_name, ce_handler.mem_vect_def, ce_handler.lat_vect_def, ce_handler.thru_vect_def)
        else:
            ce_handler.add_data_point(out_file_name, ce_handler.mem_vect_top, ce_handler.lat_vect_top, ce_handler.thru_vect_top)

    ce_handler.visualize_performance_results()
    
    print "Done with CE INTERFACE"
