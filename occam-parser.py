#!/usr/bin/env python

import sys, string, types, os
import getopt
import numpy as np

'''
Checks if the token specifies an OCCAM process
it basically checks if the token starts with
the word PROC
'''
class graph_handler:
    def __init__(self, infile_name):
        self.infile  = file(infile_name, 'r') 
        self.outfile = file('tmp_assignment_body.txt', 'w')
        self.chan_dict  = {}
        self.param_dict = {}
        self.fcn_interest = []
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
        print self.param_dict
    def print_channels(self):
        print self.chan_dict        
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
                            self.param_dict[token_name] = token_val
            if assign_cond == True:
                break
            line = self.infile.readline()
        return True
    def parse_input_file_channels(self):
        chan_dict = {}
        chan_cond = False

        line = self.infile.readline()
        while line:
            if self.is_process_end(line):
                line = False
                break
            if not line:
                assign_cond = False
                break
            if (self.is_channel_declaration(line) and
                self.is_process(line) == False):
                token_name = self.extract_int_var2(line)
                if (self.is_debug(token_name) == False):
                    self.chan_dict[token_name] = ["", ""]
            line = self.infile.readline()
        return True
        #return {'chan_dict':chan_dict, 'infile2':infile2}
    
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

    arr = np.zeros((10, 10))

    #outfile.close()
    #infile.close)(
