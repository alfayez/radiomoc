#!/usr/bin/env python

import sys, string, types, os, copy, time
import getopt
import numpy as np
import scipy
import fractions
import subprocess
import matplotlib.pyplot as plt

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
        self.config_vect_top   = []
        
        self.mem_vect_def      = []
        self.lat_vect_def      = []
        self.thru_vect_def     = []
        self.config_vect_def   = []
        
        self.infile_name       = ""
        
        self.i_cur         = 0 

    def visualize_performance_results(self, num_for_average):
        len_vect      = len(self.thru_vect_top)
        vect_vect_loc = []
        for i in xrange(len_vect-1):
            self.lat_vect_def.extend([self.lat_vect_def[0]])
            self.mem_vect_def.extend([self.mem_vect_def[0]])
            self.thru_vect_def.extend([self.thru_vect_def[0]])
            self.config_vect_def.extend([self.config_vect_def[0]])
            vect_vect_loc.extend([self.vect_vect[i+1]])

        vect_vect_loc.extend([self.vect_vect[len_vect]])

        # save data to special folder
        #save_file   = "data.dat"
        dir_name    = '/home/alfayez/workspace/dissertation_data/'
        folder_name = self.infile_name+"-"+str(datetime.date.today())+str(time.time())
        final_folder_name = dir_name+folder_name+"/"
        if os.path.exists(dir_name+folder_name):
            # in the off chance another directory was created at the
            # same exact moment
            folder_name = folder_name+folder_name
        os.makedirs(dir_name+folder_name)
        # make copies of raw data files for future use
        for fname in self.out_file_vect:
            for i in xrange(num_for_average):
                os.system("cp"+" "+fname+"-"+str(i)+".dat"+" "+final_folder_name)
            os.system("cp"+" "+self.infile_name+" "+final_folder_name)
            
        #############################################################################
        # Latency Plot
        #############################################################################
        
        figure(0)
        plot(vect_vect_loc, self.lat_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.lat_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.lat_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.lat_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Latency (ms)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = max(self.lat_vect_top)
        max_def = max(self.lat_vect_def)
        max_both = max(max_top, max_def)
        max_both = max_both*1.3
        ylim(0.0, max_both)
        #plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        pic_name = "latency.png"
        savefig(pic_name, dpi=300)
        os.system("mv"+" "+pic_name+" "+final_folder_name)
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
        ylabel('Memory (KB)')
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
        pic_name = "memory.png"
        savefig(pic_name, dpi=300)
        os.system("mv"+" "+pic_name+" "+final_folder_name)        
        #############################################################################
        # Throughput Plot
        #############################################################################
        figure(2)
        plot(vect_vect_loc, self.thru_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.thru_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.thru_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.thru_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Throughput (KB/sec)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.thru_vect_top))
        max_def = ceil(max(self.thru_vect_def))
        max_both = max(max_top, max_def)
        max_both = max_both*1.5
        min_top = ceil(max(self.thru_vect_top))
        min_def = ceil(max(self.thru_vect_def))
        min_both = min(min_top, min_def)
        min_both = min_both/1.3
        ylim(0.0, max_both)
        pic_name = "throughput.png"
        savefig(pic_name, dpi=300)
        os.system("mv"+" "+pic_name+" "+final_folder_name)
        #############################################################################
        # Reconfiguration Time Plot
        #############################################################################
        figure(3)
        plot(vect_vect_loc, self.config_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.config_vect_def, linewidth=2.0, color='blue')
        plot(vect_vect_loc, self.config_vect_top, linewidth=2.0, color='green', label='Topology Allocation')
        scatter(vect_vect_loc, self.config_vect_top, linewidth=2.0, color='green')
        xlabel('Vectorization Factor')
        ylabel('Reconfiguration Time (ms)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1], len_vect, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = max(self.config_vect_top)
        max_def = max(self.config_vect_def)
        max_both = max(max_top, max_def)
        max_both = max_both*1.3
        min_top = max(self.config_vect_top)
        min_def = max(self.config_vect_def)
        min_both = min(min_top, min_def)
        min_both = min_both/1.3
        print "max_both= ", max_both
        print "self.config_vect_top= ", self.config_vect_top
        print "self.config_vect_def= ", self.config_vect_def
        ylim(0, max_both)
        #plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        pic_name = "reconfiguration.png"
        savefig(pic_name, dpi=300)
        os.system("mv"+" "+pic_name+" "+final_folder_name)

        show()        
    def set_ranges(self, vect_range):
        self.vect_range
    def add_data_point(self, file_name, mem_vect_local,lat_vect_local, thru_vect_local, config_vect_local, run_num, run_len):
        sanity_check  = 0
        ifile_handler = open(file_name, 'r')
        line          = ifile_handler.readline()
        tokens        = line.split()
        value         = -1
        last_ind      = -1 
        while line:
            last_ind = len(mem_vect_local)-1            
            if "memory_total" in line:
                sanity_check = sanity_check + 1
                # divide by 1024 to make into KB
                #print "tokens[2]= ", tokens[2]
                if(run_num is 0):
                    value = float(tokens[2])/1024
                    value = value/run_len
                    mem_vect_local.extend([value])
                else:
                    value    = float(tokens[2])/1024
                    value = value/run_len                    
                    mem_vect_local[last_ind] = mem_vect_local[last_ind]+value
            elif "latency" in line:
                sanity_check = sanity_check + 1
                if(run_num is 0):
                    value = float(tokens[2])*1000 # make ms instead of second
                    value = value/run_len
                    lat_vect_local.extend([value])
                else:
                    value = float(tokens[2])*1000
                    value = value/run_len
                    lat_vect_local[last_ind] = lat_vect_local[last_ind] + value
            elif "throughput" in line:
                # divide by 1024 to make into KB/s
                sanity_check = sanity_check + 1
                if(run_num is 0):
                    value = float(tokens[2])/1024
                    value = value/run_len                    
                    thru_vect_local.extend([value])
                else:
                    value = float(tokens[2])/1024
                    value = value/run_len
                    thru_vect_local[last_ind] = thru_vect_local[last_ind] + value                    
            elif "configuration_time" in line:
                sanity_check = sanity_check + 1
                if(run_num is 0):
                    value = float(tokens[2])*1000
                    value = value/run_len                    
                    config_vect_local.extend([value])
                else:
                    value = float(tokens[2])*1000
                    value = value/run_len
                    config_vect_local[last_ind] = config_vect_local[last_ind] + value                    
            if sanity_check == 4:
                break
            line   = ifile_handler.readline()
            tokens = line.split()
        ifile_handler.close()
        if sanity_check == 4:
            self.i_cur = self.i_cur + 1
            return True
        else:
            print "ERROR in add_data_point, file= ", filename, " is malformed, sanity check= ", sanity_check
            return False
    
if __name__ == "__main__":
    print "Before system call"
    num_for_average     = 10
    start_vect          = 0
    vectorization_times = 16 
    run_time_duration   = 60*5
    #run_time_duration   = 10 
    token_size_size     = 256 
    token_mode          = "linear"
    ce_handler    = ce_interface()

    ce_handler.vect_vect     = range(start_vect, vectorization_times)
    len_range                = len(ce_handler.vect_vect)
    for i in range(start_vect, vectorization_times):
        ce_handler.out_file_vect.extend(["temp"+str(i)])
        if i is 0:
            ce_handler.alloc_vect.extend([0])
        else:
            ce_handler.alloc_vect.extend([1])
    #print "outfile_vect = ", ce_handler.out_file_vect
    token_size    = token_size_size
    in_file_name  = "csp-sdf-sim.occ"
    #in_file_name  = "csp-sdf-tx.occ"
    #in_file_name  = "csp-sdf-rx.occ"    
    run_time      = str(run_time_duration)
    for i in range(vectorization_times-start_vect):
        for j in range(num_for_average):
            i_vect = i + start_vect
            ce_handler.infile_name = in_file_name
            out_file_name    = ce_handler.out_file_vect[i]+"-"+str(j)+".dat"
            vect_fact        = ce_handler.vect_vect[i]
            alloc_policy     = str(ce_handler.alloc_vect[i])
            print "Average Iteration= ", j        
            #command_str = "python design_interface.py -t "+token_size+" -l "+vect_fact+" -a "+alloc_policy+ " -r "+run_time+" -o "+out_file_name+" -i "+in_file_name
            command_str2 = ['python', 'design_interface.py', '-t', str(token_size), '-l', str(vect_fact), '-a', str(alloc_policy), '-r', str(run_time), '-o', out_file_name, '-i', in_file_name, '-m', token_mode]
            
            #result = os.system(command_str)
            #print "command= ", command_str2

            proc = subprocess.Popen(command_str2, shell=False)
            result = proc.wait()


            #out, err = proc.communicate()
            #print "Out= ", out, " ERROR= ", err
            
            if i is 0:
                ce_handler.add_data_point(out_file_name, ce_handler.mem_vect_def, ce_handler.lat_vect_def,
                                          ce_handler.thru_vect_def, ce_handler.config_vect_def, j, num_for_average)
            else:
                ce_handler.add_data_point(out_file_name, ce_handler.mem_vect_top, ce_handler.lat_vect_top,
                                          ce_handler.thru_vect_top, ce_handler.config_vect_top, j, num_for_average)

    ce_handler.visualize_performance_results(num_for_average)
    
    print "Done with CE INTERFACE"
