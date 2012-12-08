#!/usr/bin/env python

import sys, string, types, os
import getopt
import numpy as np

from ptolemy_gen import *
'''
Checks if the token specifies an OCCAM process
it basically checks if the token starts with
the word PROC
'''
OUT_CHAN = 0
IN_CHAN  = 1
IGNORE_PROC = ["parameterGen"]
INIT_PROC = "parameterGen"

class graph_handler:
    def __init__(self, infile_name):
        self.infile  = file(infile_name, 'r') 
        self.outfile = file('tmp_assignment_body.txt', 'w')
        self.chan_dict    = {}
        self.chan_list    = []
        self.proc_dict    = {}
        self.proc_list    = []        
        self.param_dict   = {}
        self.param_list   = []
        self.top_matrix   = np.zeros((1,1))
        
        self.fcn_interest = []
        self.init_chans   = []

        self.block_map_dict = ['rfOut':[CLASS_DISCARD],
                               'channelFilter': [CLASS_FIR],
                               'rfScale': [CLASS_SCALE],
                               'dataSrc':[CLASS_CONST],
                               'carrierScale':[CLASS_SCALE],
                               'carrier':[CLASS_SINE],
                               'dbpskTransmitter':[CLASS_DBPSK_TX],
                               ]
    def __del__(self):
        self.outfile.close()
        self.infile.close()
        
    def is_process(self, line):
        if "PROC" in line:
            if self.not_comment(line):
                return True
            else:
                return False
        else:
            return False
    def is_process_end(self, line):
        if line == ":\n" and len(line) == 2:
            if self.not_comment(line):
                return True
            else:
                False
        else:
            return False
    
    def is_process_body(self, line):
        if ("SEQ" in line or "PAR" in line):
            if self.not_comment(line):
                return True
            else:
                return False
        else:
            return False
    def is_assignment(self, line):
        if ":=" in line:
            if self.not_comment(line):
                return True
            else:
                return False
        else:
            return False
    def is_int_declaration(self, line):
        if "INT" in line:
            if self.not_comment(line):
                return True
            else:
                return False
        else:
            False
    def is_channel_declaration(self, line):
        if (("CHAN" in line) and (self.not_comment(line))):
            return True
        else:
            return False
    def is_debug(self, token):
        if (token[0] == "D"):
            return True
        else:
            return False
    def not_comment(self, line):
        if "--" not in line:
            return True
        else:
            return False
    def is_comment(self, line):
        if "--" not in line:
            return False
        else:
            return True        
        # extracts the value of the int variable
    def extract_val(self, line):
        tokens = line.split()
        token_val = 0
        len_toks = len(tokens)
        for i in range(len_toks):
            if (tokens[i] == ":="):
                token_val = tokens[i+1]
        return token_val
    # extract the name of the integer variable
    def extract_int_var(self, line):
        tokens = line.split()
        token_val = 0
        len_toks = len(tokens)
        for i in range(len_toks):
            if (tokens[i] == ":="):
                token_val = tokens[i-1]
        return token_val
    def extract_int_var2(self, line):
        tokens = line.split()
        token_val = ""
        len_toks = len(tokens)
        for i in range(len_toks):
            if (tokens[i] == "INT"):
                token_val = tokens[i+1]
                break
        return token_val
    def set_fcn_interest(self, fcn_pass):
        self.fcn_interest = fcn_pass
    def print_parameters(self):
        print "Parameter Dictionary"
        print self.param_dict
    def print_channels(self):
        print "Channel Dictionary"
        print self.chan_dict
    def print_proc_dict(self):
        print "Process Dictionary"
        print self.proc_dict
    def print_chan_list(self):
        print "Channel List"
        print self.chan_list
    def print_proc_list(self):
        print "Processes list"
        print self.proc_list
    def print_top_matrix(self):
        print "Topology Matrix"
        print self.top_matrix
    def parse_input_file_param(self):
        # output filestream used to save the parameter generator
        # body for further processing after we discover the requested
        # topology in the main loop body
        self.outfile.flush()
        os.fsync(self.outfile)

        assign_cond  = False

        line = self.infile.readline()
        while line:
            # check to see if the processes of interest are in the current
            # line
            if self.fcn_interest[0] in line:
                # make sure that the token specifies a process
                if self.is_process(line):
                    assign_cond  = False
                        
                    while(assign_cond == False):
                        line = self.infile.readline()
                        self.outfile.write(line)
                        # populate the list of radio parameters of
                        # interest by parsing the variables declared in
                        # the parameter definition process in the occam program
                        if self.is_process_end(line):
                            assign_cond = True
                            break
                        if not line:
                            assign_cond = True
                            break
                        if self.is_assignment(line):
                            token_name = self.extract_int_var(line)
                            token_val  = self.extract_val(line)
                            if ((token_name in self.param_dict) == False):
                                self.param_list.append(token_name)
                            self.param_dict[token_name] = token_val
            if assign_cond == True:
                break
            line = self.infile.readline()
        return True
    def parse_input_file_channels(self):
        chan_dict = {}
        chan_cond = False
        process_body = False

        line = self.infile.readline()
        while line:
            if self.is_process_end(line):
                line = False
                break
            elif not line:
                assign_cond = False
                break
            elif (process_body == True):
                # make sure it's not an empty line
                if len(line) > 1:
                    # make sure it's not a commented out line
                    if (self.is_comment(line) == False):
                        self.parse_channel_directions(line)
            elif (self.is_channel_declaration(line) and
                self.is_process(line) == False):
                token_name = self.extract_int_var2(line)
                if (self.is_debug(token_name) == False):
                    self.chan_dict[token_name] = ["", ""]
                    self.chan_list.append(token_name)                    

            elif self.is_process_body(line):
                process_body = True
                
            line = self.infile.readline()

        return True
        #return {'chan_dict':chan_dict, 'infile2':infile2}
    def clean_from_punc(self, tokens):
        len_tokens = len(tokens)
        for i in range(len_tokens):
            tokens[i] = tokens[i].replace(")", "")
            tokens[i] = tokens[i].replace("(", "")
            tokens[i] = tokens[i].replace(",", "")
        return tokens
    def channel_name(self, token):
        token = token.replace("?", "")
        token = token.replace("!", "")
        return token
    def channel_direction(self, token):
        if "!" in token:
            return "out"
        elif "?" in token:
            return "in"
        elif token[0] == "D":
            return "debug"
        else:
            return ""
    def is_ignore_proc(self, proc_name):
        len_list = len(IGNORE_PROC);
        for i in range(len_list):
            if proc_name == IGNORE_PROC[i]:
                return True
        return False
        
    def parse_channel_directions(self, line):
        tokens     = line.split()
        tokens     = self.clean_from_punc(tokens)
        len_tokens = len(tokens)
        chan_name  = ""
        chan_dir   = ""

        proc_name  = tokens[0]

        # the first token is the function name.  If this is a debug
        # function then ignore it
        if (self.is_debug(proc_name) or self.is_comment(line)):
            return True
        else:
            # Start at "1" since 0->Process Name
            for j in range(1, len_tokens):
                chan_name = self.channel_name(tokens[j])
                chan_dir  = self.channel_direction(tokens[j])
                if(self.is_debug(chan_name) == False):
                    if (self.is_ignore_proc(proc_name) == False):
                    #if True:
                        if chan_dir == "out":
                           # if ( ((proc_name in self.proc_list) == False)
                           #      and (self.is_ignore_proc(proc_name) == False)):
                           #     self.proc_list.append(proc_name)
                           #     self.proc_dict[proc_name] = len(self.proc_dict)
                            self.chan_dict[chan_name][OUT_CHAN] = proc_name
                            if proc_name == INIT_PROC:
                                self.init_chans = self.init_chans+[chan_name]
                        elif chan_dir == "in":
                            self.chan_dict[chan_name][IN_CHAN] = proc_name
                        elif chan_dir == "debug":
                            chan_dir = chan_dir
                        else:                        
                            return False
                        if chan_dir != "debug":
                            if ((proc_name in self.proc_list) ==
                                False):
                                if(self.is_ignore_proc(proc_name)==False):
                                    self.proc_list.append(proc_name)
                                    self.proc_dict[proc_name] = len(self.proc_dict)                                    
                        
            len_proc = len(self.proc_list)
            self.top_matrix = np.zeros((len_proc, len_proc))    
    def parse_proc_connection(self):
        len_chans = len(self.chan_list)
        for i in range(len_chans):
            
            chan_name = self.chan_list[i]
            
            proc_out  = self.chan_dict[chan_name][0]
            proc_in   = self.chan_dict[chan_name][1]

            if (proc_out != ""):
                proc_out_index  = self.proc_dict[proc_out]
                if (proc_in != ""):                
                    proc_in_index   = self.proc_dict[proc_in]
                self.top_matrix[proc_out_index][proc_in_index] = 1
        
if __name__ == "__main__":

    # the input occam program which we will be processing
    infile_name = 'csp-sdf-tx.occ'
    # specifies processes of interest in the occam program
    fcn_list    = ["parameterGen", "main"]
    
    top_handler = graph_handler(infile_name)
    top_handler.set_fcn_interest(fcn_list)


    # peforms initial parameter parsing of the occam file
    top_handler.parse_input_file_param()
    top_handler.print_parameters()
    top_handler.parse_input_file_channels()
    top_handler.print_channels()

    top_handler.parse_proc_connection()

    top_handler.print_proc_list()
    top_handler.print_chan_list()
    top_handler.print_proc_dict()
    top_handler.print_top_matrix()
    test_ptolemy()

    #outfile.close()
    #infile.close)(
