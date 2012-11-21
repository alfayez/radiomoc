#!/usr/bin/env python

import sys, string, types
import getopt
import numpy as np

'''
Checks if the token specifies an OCCAM process
it basically checks if the token starts with
the word PROC
'''
def is_process(line):
    if "PROC" in line:
        return True
    else:
        return False

def is_assignment(line):
    if ":=" in line:
        return True
    else:
        return False
'''
 creates a dictionary from the sequence variables of interest
 as specified by the param_in sequence list
'''
def make_dict_from_seq(param_in):
    seq_len   = len(param_in)

    if (seq_len == 0):
        temp_dict = dict()
        return temp_dict

    temp_arr  = np.zeros(seq_len)
    temp_dict = dict(zip(param_in, temp_arr))
    return temp_dict

def param_first_occur(param_in, line):
    occur = "None"
    cond  = False

    len_param = len(param_in)
    for i in range(len_param):
        if param_in[i] in line:
            cond = True
            return{'cond':cond, 'occur':param_in[i]}
    return {'cond':cond, 'occur':occur}

def extract_val(line):
    tokens = line.split()
    token_val = 0
    len_toks = len(tokens)
    for i in range(len_toks):
        if (tokens[i] == ":="):
            token_val = tokens[i+1]
        
    return token_val

def parse_input_file(param_in, param_dict_orig, infile):
    param_dict = param_dict_orig


    line = infile.readline()
    while line:

        # check to see if the processes of interest are in the current
        # line
        
        if seq_base[0] in line:

            # make sure that the token specifies a process
            if is_process(line):
                assign_cond = False
                while(assign_cond == False):
                    line = infile.readline()
                    if not line:
                        assign_cond = False
                        break
                    r = param_first_occur(param_in, line)
                    if(r['cond']):
                        if is_assignment(line):
                            token_val = extract_val(line)
                            param_dict[r["occur"]] = token_val
        line = infile.readline()


    return {'param_dict:'=param_dict, 'infile:', infile}

#def get_val(param, infile):
#    cond = False
#    val  = 0
#    
#    for line in infile:
#        if 
#
#    return {'cond': cond, 'val':val}

if __name__ == "__main__":
    # specifies processes of interest in the occam program
    seq_base= ["parameterGen"]

    # specifies the parameters of interest defined in the occam
    # program in the "paramGen" init function
    param_in= ["symbolTime", "samplingRate", "carrierFreq",
               "rcFiltCoeff", "carrierGain", "rfGain"]

    assign_cond = False
    token_val = 0

    # opens filestreams
    outfile = file('tmp.txt', 'w')
    infile  = file('csp-sdf-tx.occ', 'r')


    # create dictionary from sequence entries
    param_dict = make_dict_from_seq(param_in)

    r = parse_input_file(param_in, param_dict, infile)
    param_dict = r["param_dict"]

    print "param_dict is = ", param_dict
    outfile.write('This is a test output to a file ... yepee!')
    arr = np.zeros((10, 10))

    outfile.close()
    infile.close()
