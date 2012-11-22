#!/usr/bin/env python

import sys, string, types, os
import getopt
import numpy as np

'''
Checks if the token specifies an OCCAM process
it basically checks if the token starts with
the word PROC
'''
def is_process(line):
    if "PROC" in line:
        if not_comment(line):
            return True
        else:
            return False
    else:
        return False
def is_process_end(line):
    if line == ":\n" and len(line) == 2:
        if not_comment(line):
            return True
        else:
            False
    else:
        return False
    
def is_process_body(line):
    if ("SEQ" in line or "PAR" in line):
        if not_comment(line):
            return True
        else:
            return False
    else:
        return False
def is_assignment(line):
    if ":=" in line:
        if not_comment(line):
            return True
        else:
            return False
    else:
        return False
def is_int_declaration(line):
    if "INT" in line:
        if not_comment(line):
            return True
        else:
            return False
    else:
        False
def is_channel_declaration(line):
    if (("CHAN" in line) and (not_comment(line))):
        return True
    else:
        return False
    
def not_comment(line):
    if "--" not in line:
        return True
    else:
        return False
# extracts the value of the int variable
def extract_val(line):
    tokens = line.split()
    token_val = 0
    len_toks = len(tokens)
    for i in range(len_toks):
        if (tokens[i] == ":="):
            token_val = tokens[i+1]
        
    return token_val
# extract the name of the integer variable
def extract_int_var(line):
    tokens = line.split()
    token_val = 0
    len_toks = len(tokens)
    for i in range(len_toks):
        if (tokens[i] == ":="):
            token_val = tokens[i-1]
        
    return token_val

#def parse_topology_1(infile)
def parse_input_file_param(seq_base, infile, outfile):
    assign_cond  = False
    param_dict   = {}

    line = infile.readline()
    while line:
        # check to see if the processes of interest are in the current
        # line

        if seq_base in line:
            print "seq = ", seq_base, "Aline = ", line
            # make sure that the token specifies a process
            if is_process(line):
                assign_cond  = False
                        
                while(assign_cond == False):
                    line = infile.readline()
                    print "ILINE= ", line
                    outfile.write(line)
                    # populate the list of radio parameters of
                    # interest by parsing the variables declared in
                    # the parameter definition process in the occam program
                    if is_process_end(line):
                        print "Quit1"
                        assign_cond = True
                        break
                    if not line:
                        print "Quit"    
                        assign_cond = True
                        break
                    if is_assignment(line):
                        token_name = extract_int_var(line)
                        token_val  = extract_val(line)
                        param_dict[token_name] = token_val
        if assign_cond == True:
            print "EXLine= ", line
            break
        line = infile.readline()
        print "BLine= ", line
    return {'param_dict':param_dict, 'infile':infile}
def parse_input_file_channels(fcn_interest, infile2, outfile):
    chan_dict = {}
    chan_cond = False

    line_loc = infile2.readline()
    print "lineO = ", line_loc
    while line_loc:
        if is_process_end(line_loc):
            line_loc = False
            break
        if not line_loc:
            assign_cond = False
            break
        if is_channel_declaration(line_loc):
            print "line_loc = ", line_loc
            #token_name = extract_int_var(line)
            #token_val  = extract_val(line)
            #param_dict[token_name] = token_val
        print "lineO = ", line_loc
        line_loc = infile2.readline()

        return {'chan_dict':chan_dict, 'infile2':infile2}        
    
if __name__ == "__main__":
    # specifies processes of interest in the occam program
    fcn_interest= ["parameterGen", "main"]

    assign_cond = False
    token_val = 0

    # output filestream used to save the parameter generator
    # body for further processing after we discover the requested
    # topology in the main loop body
    outfile = file('tmp_assignment_body.txt', 'w')
    outfile.flush()
    os.fsync(outfile)

    # the input occam program which we will be processing
    infile  = file('csp-sdf-tx.occ', 'r')

    # peforms initial parameter parsing of the occam file
    r = parse_input_file_param(fcn_interest[0], infile, outfile)
    param_dict = r["param_dict"]
    infile2     = r["infile"]
    print "param_dict is = ", param_dict
    r = parse_input_file_channels(fcn_interest, infile2, outfile)
    #chan_dict = r["chan_dict"]

    arr = np.zeros((10, 10))

    outfile.close()
    infile.close()
