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
        self.token_graph   = []

        self.mem_vect_top      = []
        self.lat_vect_top      = []
        self.thru_vect_top     = []
        self.config_vect_top   = []
        self.mem_vect_top2      = np.zeros((1,1))
        self.lat_vect_top2      = np.zeros((1,1))
        self.thru_vect_top2     = np.zeros((1,1))
        self.config_vect_top2   = np.zeros((1,1))
        self.mem_vect_top2_var      = np.zeros((1,1))
        self.lat_vect_top2_var      = np.zeros((1,1))
        self.thru_vect_top2_var     = np.zeros((1,1))
        self.config_vect_top2_var   = np.zeros((1,1))

        self.top_sub_plot      = 1
        
        self.mem_vect_def      = []
        self.lat_vect_def      = []
        self.thru_vect_def     = []
        self.config_vect_def   = []
        
        self.mem_vect_def2      = np.zeros((1,1))
        self.lat_vect_def2      = np.zeros((1,1))
        self.thru_vect_def2     = np.zeros((1,1))
        self.config_vect_def2   = np.zeros((1,1))
        self.mem_vect_def2_var      = np.zeros((1,1))
        self.lat_vect_def2_var      = np.zeros((1,1))
        self.thru_vect_def2_var     = np.zeros((1,1))
        self.config_vect_def2_var   = np.zeros((1,1))
        
        self.infile_name       = ""
        
        self.i_cur         = 0 

    def calc_var_help(self, var_vect, mean_val):
        var_val = 0
        #print "VAR= ", var_vect        
        avg_len  = len(var_vect)
        #print "AVG LEN= ", avg_len
        #print "var_val0= ", var_val
        for j in range(avg_len):
            #print "j= ", j
            #print "var_val1= ", var_vect
            #print "mean_val= ", mean_val
            #print "var_vect[j]= ", var_vect[j]
            var_val = var_val + pow((mean_val - var_vect[j]),2)/avg_len
        #print "var_val2= ", var_val
        var_val = sqrt(var_val)
        #print "var_val3= ", var_val
        return var_val
    def calc_var(self):
        vect_len = len(self.thru_vect_top[0])
        #print "VECT LEN= ", vect_len
        #raw_input("HERE")
        for i in range(vect_len+1):
            #print "I= ", i            
            if i == 0:
                self.lat_vect_def2_var[i]    = self.calc_var_help(self.lat_vect_def2, self.lat_vect_def[i])
                self.thru_vect_def2_var[i]   = self.calc_var_help(self.thru_vect_def2, self.thru_vect_def[i])
                self.config_vect_def2_var[i] = self.calc_var_help(self.config_vect_def2, self.config_vect_def[i])
                #print "DEF in var= ", self.config_vect_def2, " mean= ", self.config_vect_def[i]
                #print "DEF self.config_vect_def2_var[i]= ", self.config_vect_def2_var[i]
                #name = raw_input('Something')
                #for j in xrange(vect_len-1):
                #    print "j= ", self.lat_vect_def2_var
                #    self.lat_vect_def2_var[j+1]    = self.lat_vect_def2_var[0]
                #    self.thru_vect_def2_var[j+1]   = self.thru_vect_def2_var[0]
                #    self.config_vect_def2_var[j+1] = self.config_vect_def2_var[0]
            else:
                #print "TOP2_var = ", len(self.lat_vect_top2_var)
                #print "LAT2 = ", self.lat_vect_top2
                #print "LAT = ", self.lat_vect_top[0]
                self.lat_vect_top2_var[i-1]    = self.calc_var_help(self.lat_vect_top2[i-1], self.lat_vect_top[0][i-1])
                self.thru_vect_top2_var[i-1]   = self.calc_var_help(self.thru_vect_top2[i-1],self.thru_vect_top[0][i-1])
                self.config_vect_top2_var[i-1] = self.calc_var_help(self.config_vect_top2[i-1], self.config_vect_top[0][i-1])
                #print "in var= ", self.config_vect_top2[i-1], " mean= ", self.config_vect_top[0][i-1]
                #print "self.config_vect_top2_var[i-1]= ", self.config_vect_top2_var[i-1]
                #name = raw_input('Something')
        #print "config_VAR= ", self.config_vect_def2_var
        #print "config_VAR_top= ", self.config_vect_top2_var
        #print "thru_VAR= ", self.thru_vect_def2_var
        #print "thru_VAR_top= ", self.thru_vect_top2_var
        #print "lat_VAR= ", self.lat_vect_def2_var
        #print "lat_VAR_top= ", self.lat_vect_top2_var
        #name = raw_input('Something')
    def visualize_performance_results(self, num_for_average):
        color_loc        = ['green', 'black', 'red', 'yellow']
        #index_temp    = 0
        len_vect      = len(self.thru_vect_top[0])
        vect_vect_loc = []
        print "BEGIN= ", "lat vect= ", self.lat_vect_def
        for i in xrange(len_vect-1):
            self.lat_vect_def.extend([self.lat_vect_def[0]])
            print "lat vect= ", self.lat_vect_def
            self.mem_vect_def.extend([self.mem_vect_def[0]])
            self.thru_vect_def.extend([self.thru_vect_def[0]])
            self.config_vect_def.extend([self.config_vect_def[0]])
            vect_vect_loc.extend([self.vect_vect[i+1]])

        vect_vect_loc.extend([self.vect_vect[len_vect]])
        self.calc_var()
        # save data to special folder
        #save_file   = "data.dat"
        #dir_name    = '/home/alfayez/workspace/dissertation_data/'
        #folder_name = self.infile_name+"-"+str(datetime.date.today())+str(time.time())
        #final_folder_name = dir_name+folder_name+"/"
        #if os.path.exists(dir_name+folder_name):
            # in the off chance another directory was created at the
            # same exact moment
        #    folder_name = folder_name+folder_name
        #os.makedirs(dir_name+folder_name)
        # make copies of raw data files for future use
        #for fname in self.out_file_vect:
        #    for i in xrange(num_for_average):
        #        os.system("cp"+" "+fname+"-"+str(i)+".dat"+" "+final_folder_name)
        #    os.system("cp"+" "+self.infile_name+" "+final_folder_name)
            
        #############################################################################
        # Latency Plot
        #############################################################################
        xzero = zeros(len(vect_vect_loc))        
        figure(0)
        plot(vect_vect_loc, self.lat_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        #scatter(vect_vect_loc, self.lat_vect_def, linewidth=2.0,
        #color='blue')
        print "VAR= ", self.lat_vect_def2_var
        errorbar(vect_vect_loc, self.lat_vect_def,yerr=self.lat_vect_def2_var, xerr=xzero,
                 linewidth=1.5, color='blue',fmt='o')
        for i in xrange(ce_handler.top_sub_plot):
            plot(vect_vect_loc, self.lat_vect_top[i], linewidth=2.0,
            color=color_loc[i], label='Topology Matrix Allocation')
            #scatter(vect_vect_loc, self.lat_vect_top[i], linewidth=2.0, color=color_loc[i])
            errorbar(vect_vect_loc, self.lat_vect_top[i],
                     yerr=self.lat_vect_top2_var, xerr=xzero,fmt='o',
                     linewidth=1.5, color=color_loc[i])
            
            
        xlabel('Buffer Scaling Factor')
        ylabel('Latency (ms)')
        legend(loc= 'upper left')
        # set X-ticks
        
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1]+1, len_vect+1, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = max(self.lat_vect_top[0])
        max_def = max(self.lat_vect_def)
        max_both = max(max_top, max_def)
        max_both = max_both*1.5
        ylim(0.0, max_both)
        #plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        pic_name = "latency.png"
        savefig(pic_name, dpi=300)
        #os.system("mv"+" "+pic_name+" "+final_folder_name)
        #############################################################################
        # Memory Plot
        #############################################################################
        figure(1)
        print "vect_vect= ", vect_vect_loc
        #print "mem_vect_def= ", self.mem_vect_def
        #print "mem_vect_top= ", self.mem_vect_top
        print "mem_vect_def= ", self.lat_vect_def
        print "mem_vect_top= ", self.lat_vect_top
        plot(vect_vect_loc, self.mem_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        scatter(vect_vect_loc, self.mem_vect_def, linewidth=2.0, color='blue')

        for i in xrange(ce_handler.top_sub_plot):
            plot(vect_vect_loc, self.mem_vect_top[i], linewidth=2.0,
            #color=color_loc[i], label='Buffer Scaling Base= '+str(self.token_graph[i]))
            color=color_loc[i], label='Topology Matrix Allocation')
            scatter(vect_vect_loc, self.mem_vect_top[i], linewidth=2.0, color=color_loc[i])

        xlabel('Buffer Scaling Factor')
        ylabel('Memory (KB)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1]+1, len_vect+1, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.mem_vect_top[0]))
        max_def = ceil(max(self.mem_vect_def))
        max_both = max(max_top, max_def)*1.4
        min_top = ceil(min(self.mem_vect_top[0]))
        min_def = ceil(min(self.mem_vect_def))
        min_both = min(min_top, min_def)
        ylim(0, max_both)
        pic_name = "memory.png"
        savefig(pic_name, dpi=300)
        #os.system("mv"+" "+pic_name+" "+final_folder_name)        
        #############################################################################
        # Throughput Plot
        #############################################################################
        figure(2)
        plot(vect_vect_loc, self.thru_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        #scatter(vect_vect_loc, self.thru_vect_def, linewidth=2.0,
        #color='blue')

        errorbar(vect_vect_loc, self.thru_vect_def, linewidth=1.5,
        color='blue', yerr=self.thru_vect_def2_var, xerr=xzero, fmt='o')

        for i in xrange(ce_handler.top_sub_plot):
            plot(vect_vect_loc, self.thru_vect_top[i], linewidth=2.0,
            #color=color_loc[i], label='Buffer Scaling Base= '+str(self.token_graph[i])
            color=color_loc[i], label='Topology Matrix Allocation')
            #scatter(vect_vect_loc, self.thru_vect_top[i], linewidth=2.0, color=color_loc[i])
            errorbar(vect_vect_loc, self.thru_vect_top[i],
            linewidth=1.5, color=color_loc[i],
                     fmt='o', yerr=self.thru_vect_top2_var, xerr=xzero)

        xlabel('Buffer Scaling Factor')
        ylabel('Throughput (samples/sec)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1]+1, len_vect+1, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = ceil(max(self.thru_vect_top[0]))
        max_def = ceil(max(self.thru_vect_def))
        max_both = max(max_top, max_def)
        max_both = max_both*1.5
        min_top = ceil(max(self.thru_vect_top[0]))
        min_def = ceil(max(self.thru_vect_def))
        min_both = min(min_top, min_def)
        min_both = min_both/1.3
        ylim(0.0, max_both)
        pic_name = "throughput.png"
        savefig(pic_name, dpi=300)
        #os.system("mv"+" "+pic_name+" "+final_folder_name)
        #############################################################################
        # Reconfiguration Time Plot
        #############################################################################
        figure(3)
        plot(vect_vect_loc, self.config_vect_def, linewidth=2.0, color='blue', label='Default Allocation')
        #scatter(vect_vect_loc, self.config_vect_def, linewidth=2.0, color='blue')

        errorbar(vect_vect_loc, self.config_vect_def, linewidth=1.5,
        color='blue', yerr=self.config_vect_def2_var, xerr=xzero, fmt='o')
        
        for i in xrange(ce_handler.top_sub_plot):
            plot(vect_vect_loc, self.config_vect_top[i],
            #linewidth=2.0, color=color_loc[i], label='Buffer Scaling Base= '+str(self.token_graph[i]))
            linewidth=2.0, color=color_loc[i], label='Topology Matrix Allocation')
            #scatter(vect_vect_loc, self.config_vect_top[i], linewidth=2.0, color=color_loc[i])
            errorbar(vect_vect_loc, self.config_vect_top[i], linewidth=1.5, color=color_loc[i],
            yerr=self.config_vect_top2_var, xerr=xzero, fmt='o')

        xlabel('Buffer Scaling Factor')
        ylabel('Reconfiguration Time (ms)')
        legend(loc= 'upper left')
        # set X-ticks
        set_xticks = np.linspace(vect_vect_loc[0], vect_vect_loc[len_vect-1]+1, len_vect+1, endpoint=True)
        xticks(set_xticks)
        # set y limit
        max_top = max(self.config_vect_top[0])
        max_def = max(self.config_vect_def)
        max_both = max(max_top, max_def)
        max_both = max_both*3.3
        min_top = max(self.config_vect_top[0])
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
        #os.system("mv"+" "+pic_name+" "+final_folder_name)

        show()
        print "lat top= ", self.lat_vect_top2_var
        print "thru top= ", self.thru_vect_top2_var
        print "config top= ", self.config_vect_top2_var
        
    def set_ranges(self, vect_range):
        self.vect_range
    def add_data_point(self, file_name, mem_vect_local,lat_vect_local, thru_vect_local, config_vect_local, run_num, run_len, i, j, override):
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
                value_save = float(tokens[2])*1000
                if i == 0:
                    self.lat_vect_def2[j] = copy.deepcopy(value_save)
                else:
                    self.lat_vect_top2[i-1][j] = copy.deepcopy(value_save)
            elif "throughput" in line:
                # divide by 1024 to make into KB/s
                sanity_check = sanity_check + 1
                if(run_num is 0):
                    #value = float(tokens[2])/1024
                    value = float(tokens[2])
                    value = value/run_len                    
                    thru_vect_local.extend([value])
                else:
                    #value = float(tokens[2])/1024
                    value = float(tokens[2])
                    value = value/run_len
                    thru_vect_local[last_ind] = thru_vect_local[last_ind] + value                    
                value_save = float(tokens[2])
                if i == 0:
                    self.thru_vect_def2[j] = copy.deepcopy(value_save)
                else:
                    self.thru_vect_top2[i-1][j] = copy.deepcopy(value_save)
            elif "configuration_time" in line:
                sanity_check = sanity_check + 1
                if(run_num is 0):
                    value = float(tokens[2])*1000
                    value = value/run_len
                    #print "line= ", line
                    #print "value= ", value
                    #raw_input ('Press Enter to continue: ')
                    config_vect_local.extend([value])
                else:
                    value = float(tokens[2])*1000
                    value = value/run_len
                    config_vect_local[last_ind] = config_vect_local[last_ind] + value                    
                value_save = float(tokens[2])*1000
                if i == 0:
                    self.config_vect_def2[j] = copy.deepcopy(value_save)
                else:
                    self.config_vect_top2[i-1][j] = copy.deepcopy(value_save)
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
    base_dir_name       = "SAVE-dissertation-data/desktop/"
 
    num_for_average     = 10
    start_vect          = 0 
    vectorization_times = 15
    token_size_size     = 1
    top_index           = 0

    ce_handler               = ce_interface()    

    # TX
    folder_names       = ["csp-sdf-tx.occ-2013-05-051367732455.05-TOKEN-EXP/"]
    #folder_names        = ["csp-sdf-tx.occ-2013-04-151366039201.6-TOKEN-256/", "csp-sdf-tx.occ-2013-04-TOKEN-128/"]

    # SIM
    #folder_names         = ["csp-sdf-sim.occ-2013-05-061367826430.19-TOKEN-EXP/"]
    #folder_names        = ["csp-sdf-sim.occ-2013-04-181366304302.77-TOKEN-256/", "csp-sdf-sim.occ-2013-04-171366213851.23-TOKEN-128/"]

    # RX
    #folder_names         = ["csp-sdf-rx.occ-2013-05-061367893844.16-TOKEN-EXP/"]
    # folder_names        = ["csp-sdf-rx.occ-2013-04-231366737255.4-TOKEN-512-CORRECT-ONE/", "csp-sdf-rx.occ-2013-04-201366484002.41-TOKEN-128-NOT-256/"]

    # RX
    #ce_handler.token_graph    = [512, 128]
    # TX and SIM
    ce_handler.token_graph    = [1, 128]

    ce_handler.top_sub_plot  = len(folder_names)
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

    ce_handler.mem_vect_top    = [[],[],[],[]]
    ce_handler.lat_vect_top    = [[],[],[],[]]
    ce_handler.thru_vect_top   = [[],[],[],[]]
    ce_handler.config_vect_top = [[],[],[],[]]

    ce_handler.mem_vect_def2      = np.zeros(num_for_average)
    ce_handler.lat_vect_def2      = np.zeros(num_for_average)
    ce_handler.thru_vect_def2     = np.zeros(num_for_average)
    ce_handler.config_vect_def2   = np.zeros(num_for_average)

    ce_handler.mem_vect_def2_var      = np.zeros(vectorization_times-start_vect-1)
    ce_handler.lat_vect_def2_var      = np.zeros(vectorization_times-start_vect-1)
    ce_handler.thru_vect_def2_var     = np.zeros(vectorization_times-start_vect-1)
    ce_handler.config_vect_def2_var   = np.zeros(vectorization_times-start_vect-1)

    ce_handler.mem_vect_top2      = np.zeros((vectorization_times-start_vect-1,num_for_average))
    ce_handler.lat_vect_top2      = np.zeros((vectorization_times-start_vect-1,num_for_average))
    ce_handler.thru_vect_top2     = np.zeros((vectorization_times-start_vect-1,num_for_average))
    ce_handler.config_vect_top2   = np.zeros((vectorization_times-start_vect-1,num_for_average))

    ce_handler.mem_vect_top2_var      = np.zeros(vectorization_times-start_vect-1)
    ce_handler.lat_vect_top2_var      = np.zeros(vectorization_times-start_vect-1)
    ce_handler.thru_vect_top2_var     = np.zeros(vectorization_times-start_vect-1)
    ce_handler.config_vect_top2_var   = np.zeros(vectorization_times-start_vect-1)

    for k in range(ce_handler.top_sub_plot):
        ce_handler.mem_vect_def   =[]
        ce_handler.lat_vect_def   =[]
        ce_handler.thru_vect_def  =[]
        ce_handler.config_vect_def=[]
        #ce_handler.mem_vect_top.append([])
        #ce_handler.lat_vect_top.append([])
        #ce_handler.thru_vect_top.append([])
        #ce_handler.config_vect_top.append([])
        for i in range(vectorization_times-start_vect):
            for j in range(num_for_average):
                i_vect = i + start_vect

                dir_name         = base_dir_name + folder_names[k]
                out_file_name    = dir_name+ce_handler.out_file_vect[i]+"-"+str(j)+".dat"
                vect_fact        = ce_handler.vect_vect[i]
                alloc_policy     = str(ce_handler.alloc_vect[i])
                #print "Average Iteration= ", j, " k= ", k

            
                if i is 0:
                    ce_handler.add_data_point(out_file_name,
                                              ce_handler.mem_vect_def,
                                              ce_handler.lat_vect_def,
                                              ce_handler.thru_vect_def,
                                              ce_handler.config_vect_def,
                                              j,
                                              num_for_average,
                                              i,
                                              j,
                                              True)
                else:
                    ce_handler.add_data_point(out_file_name,
                                              ce_handler.mem_vect_top[k],
                                              ce_handler.lat_vect_top[k],
                                              ce_handler.thru_vect_top[k],
                                              ce_handler.config_vect_top[k],
                                              j,
                                              num_for_average,
                                              i,
                                              j,
                                              False)
        print "vect LAT def = ", ce_handler.lat_vect_def
    #print "Mem top= ", ce_handler.mem_vect_top
    #print "Element[0,3]= ", ce_handler.mem_vect_top[0][3]
    #print "Element[1,3]= ", ce_handler.mem_vect_top[1][3]
    #print "len row = ", len(ce_handler.mem_vect_top)
    #print "len col = ", len(ce_handler.mem_vect_top[0])
    #print "len ele = ", len(ce_handler.mem_vect_top[0][0])
    #ce_handler.lat_vect_top    = [[],[]]
    #ce_handler.thru_vect_top   = [[],[]]
    #ce_handler.config_vect_top = [[],[]]    

    ce_handler.visualize_performance_results(num_for_average)
    
    print "Done with CE INTERFACE"
