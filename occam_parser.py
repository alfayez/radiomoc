#!/usr/bin/env python

import sys, string, types, os, copy
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

# Code Generation Modes

PTOLEMY       = 0
GNURADIO      = 1
SDF3          = 2

INPORT_COUNT  = 1
OUTPORT_COUNT = 2 
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
        # The following parameters should be written as ints for
        # ptolemy
        self.int_param_enforce_dict  = {'symbolTime':0, 'samplingRate':0, 'seedValG':0}
        self.long_param_enforce_dict = {'seedValG':0}
        # PORT_COUNT = used to iterate through connecting ports for
        # blocks with multiple input or output ports
        self.block_map_dict = {'rfOut'            :[CLASS_USER_OUTPUT,  0, 0],
                               'channelFilter'    :[CLASS_FIR,      0, 0],
                               'channelFilter2'   :[CLASS_FIR,      0, 0],
                               'rfScale'          :[CLASS_SCALE,    0, 0],
                               'rfScale2'         :[CLASS_SCALE,    0, 0],
                               'dataSrc'          :[CLASS_CONST,    0, 0],
                               'carrierScale'     :[CLASS_SCALE,    0, 0],
                               'carrier'          :[CLASS_SINE,     0, 0],
                               'dbpskTransmitter' :[CLASS_DBPSK_TX, 0, 0],
                               'rfIn'             :[CLASS_CONST,    0, 0],
                               'dbpskReceiver'    :[CLASS_DBPSK_RX, 0, 0],
                               'dataOut'          :[CLASS_USER_OUTPUT,  0, 0],
                               'gauss'            :[CLASS_GAUSS,    0, 0],
                               'gaussScale'       :[CLASS_SCALE,    0, 0],
                               'add'              :[CLASS_ADDSUB,   0, 0]
                              }
        self.block_port_dict_input = {'rfOut'    :[".input"],
                               'channelFilter'   :[".input"],
                               'channelFilter2'  :[".input"],
                               'rfScale'         :[".input"],
                               'rfScale2'        :[".input"],
                               'dataSrc'         :[".input"],
                               'carrierScale'    :[".input"],
                               'carrier'         :[".input"],
                               'dbpskTransmitter':[".carrier", ".datain"],
                               'rfIn'            :[".input"],
                               'dbpskReceiver'   :[".rfsig"],
                               'dataOut'         :[".input"],
                               'gaussScale'      :[".input"],
                               'add'             :[".plus"]
                              }
        self.block_port_dict_output = {'rfOut'   :[".output"],
                               'channelFilter'   :[".output"],
                               'channelFilter2'  :[".output"],
                               'rfScale'         :[".output"],
                               'rfScale2'        :[".output"],
                               'dataSrc'         :[".output"],
                               'carrierScale'    :[".output"],
                               'carrier'         :[".output"],
                               'dbpskTransmitter':[".output"],
                               'rfIn'            :[".output"],
                               'dbpskReceiver'   :[".output"],
                               'dataOut'         :[".output"],
                               'gauss'           :[".output"],
                               'gaussScale'      :[".output"],
                               'add'             :[".output"]
                              }
        self.offset_dict = {'rfOut'            :[0],
                             'channelFilter'   :[0],
                             'channelFilter2'  :[0],
                             'rfScale'         :[0],
                             'rfScale2'        :[0],
                             'dataSrc'         :[-70],
                             'carrierScale'    :[50],
                             'carrier'         :[50],
                             'dbpskTransmitter':[0],
                             'rfIn'            :[0],
                             'dbpskReceiver'   :[0],
                             'dataOut'         :[0],
                             'gauss'           :[50],
                             'gaussScale'      :[50], 
                             'add'             :[0]
                           }
        self.value_dict = {'rfOut'           :["None"],
                           'channelFilter'   :["None"],
                           'channelFilter2'  :["None"],
                           'rfScale'         :["None"],
                           'rfScale2'        :["None"],                           
                           'dataSrc'         :["None"],
                           'carrierScale'    :["None"],
                           'carrier'         :["None"],
                           'dbpskTransmitter':["None"],
                           'rfIn'            :["None"],
                           'dbpskReceiver'   :["None"],
                           'dataOut'         :["None"],
                           'gauss'           :["None"],
                           'gaussScale'      :["None"],
                           'add'             :["None"]
                            }
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
    def extract_var(self, line):
        tokens = line.split()
        token_val = 0
        len_toks = len(tokens)
        for i in range(len_toks):
            if (tokens[i] == ":="):
                token_val = tokens[i-1]
        return token_val
    def extract_var2(self, line):
        tokens = line.split()
        token_val = ""
        len_toks = len(tokens)
        for i in range(len_toks):
            if ((tokens[i] == "INT") or ((tokens[i] == "REAL32"))):
                token_val = tokens[i+1]
                break
        return token_val
    def set_fcn_interest(self, fcn_pass):
        self.fcn_interest = fcn_pass
    def print_parameters(self):
        print "Parameter Dictionary"
        print self.param_dict
    def print_parameter_list(self):
        print "Parameter List"
        print self.param_list
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
                            token_name = self.extract_var(line)
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
                token_name = self.extract_var2(line)
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
    def get_filename(self, filename_with_ext):
        new_name = os.path.splitext(filename_with_ext)[0]
        return new_name
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
    def set_param_values(self):
        self.value_dict = {'rfOut'            :["None"],
                           'channelFilter'    :["rc"+self.param_dict["rcFiltCoeff"]+".dat"],
                           'channelFilter2'   :["rc"+self.param_dict["rcFiltCoeff"]+".dat"],
                           'rfScale'          :["rfGain"],
                           'dataSrc'          :["7"],
                           'carrierScale'     :["carrierGain"],
                           'carrier'          :["samplingRate", "carrierFreq", "carrierPhase"],
                           'dbpskTransmitter' :["samplingRate*symbolTime"],
                           'rfIn'             :["None"],
                           'dbpskReceiver'    :["samplingRate*symbolTime"],
                           'dataOut'          :["None"],
                           'gauss'            :["seedValG", "meanValG", "stdValG"],
                           'gaussScale'       :["gaussGain"],
                           'add'              :["None"],
                           'rfScale2'         :["rfGain2"]
                            }
    def get_port_count(self, block_name, direction):
        if direction == "input":
            return self.block_map_dict[block_name][INPORT_COUNT]
        elif direction == "output":
            return self.block_map_dict[block_name][OUTPORT_COUNT]
        else:
            print "ERROR in get_port_count, didn't select valid direction (input or output)"
            exit(1)
    def inc_port_count(self, block_name, direction):
        if direction == "input":
            cur = self.block_map_dict[block_name][INPORT_COUNT]
            self.block_map_dict[block_name][INPORT_COUNT] = cur+1
        elif direction == "output":
            cur = self.block_map_dict[block_name][OUTPORT_COUNT]
            self.block_map_dict[block_name][OUTPORT_COUNT] = cur+1
        else:
            print "ERROR in inc_port_direction, didn't select valid direction (input or output)"
    def reset_port_count(self):
        len_list = len(self.proc_list)
        for i in range(len_list):
            block_name = self.proc_list[i]
            self.block_map_dict[block_name][INPORT_COUNT]=0
            self.block_map_dict[block_name][OUTPORT_COUNT]=0
    def check_if_int_enforce(self, param_name, param_val):
        if param_name in self.int_param_enforce_dict:
            param_val = param_val.replace(".0", "")
        return param_val
    def check_if_long_enforce(self, param_name, param_val):
        if param_name in self.long_param_enforce_dict:
            param_val = param_val+"L"
        return param_val    

    def generate_code(self, mode):
        if   mode == PTOLEMY:
            print "PTOLEMY Mode"
            filename = self.get_filename(infile_name)
            model_name = filename
            filename = filename + ".xml"
            pgen = ptolemy_writer(filename, model_name)

            # Choose MoC
            node1 = pgen.write_to_ptolemy_file(DIRECT, CLASS_SDF, NAME_SDF, "None", 0)
            pgen.top_element.appendChild(node1)
                
            # Generate and Instantiate Parameters
            len_list = len(self.param_list)
            for i in range(len_list):
                param_name = self.param_list[i]
                param_val  = self.param_dict[param_name]
                param_val  = self.check_if_int_enforce(param_name, param_val)
                param_val  = self.check_if_long_enforce(param_name, param_val)
                node1 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, param_name, [param_val], 0)
                pgen.top_element.appendChild(node1)
            # Generate and Instantiate Blocks
            len_list = len(self.proc_list)
            for i in range(len_list):
                block_name   = self.proc_list[i]
                class_name   = self.block_map_dict[block_name][PTOLEMY]
                block_offset = self.offset_dict[block_name][PTOLEMY]
                block_value  = self.value_dict[block_name]
                node1 = pgen.write_to_ptolemy_file(BLOCK, class_name, block_name, block_value, block_offset)
                pgen.top_element.appendChild(node1)
            #Generate and Instantiate Connections
            len_list  = len(self.chan_list)
            out_index = 0
            in_index  = 0
            for i in range(len_list):
                chan_name      = self.chan_list[i]
                block_out_name = self.chan_dict[chan_name][OUT_CHAN]
                block_in_name  = self.chan_dict[chan_name][IN_CHAN]
                if ((len(block_in_name)>0) and (len(block_out_name)>0)):                    
                    out_index = self.get_port_count(block_out_name, "output")
                    in_index  = self.get_port_count(block_in_name, "input")

                    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, chan_name, "no", 0)
                    pgen.top_element.appendChild(chan1)

                    # this allows connections into blocks with
                    # multiple input ports or non-default port names.
                    # Each time a block name appears an index is
                    # iterated which allows us to access the name of
                    # the next physical port in the block
                    outport_name = block_out_name+self.block_port_dict_output[block_out_name][out_index]
                    inport_name  = block_in_name+self.block_port_dict_input[block_in_name][in_index]

                    [chana, chanb] = pgen.link_in_ptolemy_file(outport_name, inport_name, chan_name)
                    pgen.top_element.appendChild(chana)
                    pgen.top_element.appendChild(chanb)

                    # increment port count except if port count limit
                    # is reached but there are more connections then
                    # this port is a multiport allowing multiple connections
                    out_lim = len(self.block_port_dict_output[block_out_name])
                    in_lim  = len(self.block_port_dict_input[block_in_name])
                    if out_lim > (out_index+1):
                        self.inc_port_count(block_out_name, "output")
                    if in_lim > (in_index+1):
                        self.inc_port_count(block_in_name, "input")
            self.reset_port_count()
            pgen.write_to_xmlfile()

        elif mode == GNURADIO:
            print "GNURADIO Mode"
        elif mode == SDF3:
            print "SDF3 Mode"
        else:
            print "ERROR in generate_code.  You chose an unsupported code generation mode"
            exit(-1)
        
if __name__ == "__main__":
    infile_name_list = ["csp-sdf-rx.occ", "csp-sdf-tx.occ", "csp-sdf-sim.occ"]
    # the input occam program which we will be processing
    infile_name = infile_name_list[2]
    # specifies processes of interest in the occam program
    fcn_list    = ["parameterGen", "main"]
    
    top_handler = graph_handler(infile_name)
    top_handler.set_fcn_interest(fcn_list)


    # peforms initial parameter parsing of the occam file
    top_handler.parse_input_file_param()
    top_handler.print_parameters()
    top_handler.print_parameter_list()    
    top_handler.set_param_values()
    top_handler.parse_input_file_channels()
    top_handler.print_channels()

    top_handler.parse_proc_connection()

    top_handler.print_proc_list()
    top_handler.print_chan_list()
    top_handler.print_proc_dict()
    top_handler.print_top_matrix()
    test_ptolemy()
    top_handler.generate_code(PTOLEMY)

    #outfile.close()
    #infile.close)(
