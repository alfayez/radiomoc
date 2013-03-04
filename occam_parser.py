#!/usr/bin/env python

import sys, string, types, os, copy
import getopt
import numpy as np
import scipy
import fractions

from ptolemy_gen  import *
from gnuradio_gen import *
from lp_gen       import *
'''
Checks if the token specifies an OCCAM process
it basically checks if the token starts with
the word PROC
'''
# Indices for block_map_dict
OUT_CHAN = 0
IN_CHAN  = 1

# Indices for proc_dict
PROC_LIST_IND    = 0
PROC_RATE_IN     = 1
PROC_RATE_OUT    = 2

IGNORE_PROC = ["parameterGen"]
IGNORE_CHAN = ["setupC", "setupC2", "setupC3"]
INIT_PROC = "parameterGen"

# Code Generation Modes

PTOLEMY       = 0
GNURADIO      = 1
SDF3          = 2

INPORT_COUNT  = 2
OUTPORT_COUNT = 3 
class graph_handler:
    def __init__(self, infile_name):
        self.default_buffer_size = 32*1024
        self.cur_bufer_size      = 32*1024
        self.infile  = file(infile_name, 'r') 
        self.outfile = file('tmp_assignment_body.txt', 'w')
        self.chan_dict      = {}
        self.chan_dict_temp = {}        
        self.chan_list      = []
        self.proc_dict      = {}
        self.proc_list      = []        
        self.param_dict     = {}
        self.param_list     = []
        self.rate_list      = [] # list of rates in current flowgraph
        self.top_matrix     = np.zeros((1,1))
        self.sched          = 0
        self.fcn_interest = []
        self.init_chans   = []
        self.rankVal      = 0
        # The following parameters should be written as ints for
        # ptolemy
        self.int_param_enforce_dict  = {'symbolTime':0, 'samplingRate':0, 'seedValG':0, 'samplingRate':0, 'samplingRate2':0}
        self.long_param_enforce_dict = {'seedValG':0}
        ###################################################
        ## Provides the class names for the blocks in    ##
        ## Ptolemy and GNU Radio                         ##
        ###################################################        
        # PORT_COUNT = used to iterate through connecting ports for
        # blocks with multiple input or output ports
        self.block_map_dict = {'rfOut'            :[CLASS_USER_OUTPUT, CLASS_USRP_SINK_GNU, 0, 0],
                               'channelFilter'    :[CLASS_USER_FIR,    CLASS_MULT_CONST_GNU, 0, 0],
                               'channelFilter2'   :[CLASS_USER_FIR,    CLASS_MULT_CONST_GNU, 0, 0],
                               'basebandScale'    :[CLASS_SCALE,       CLASS_MULT_CONST_GNU, 0, 0],
                               'basebandScale2'   :[CLASS_SCALE,       CLASS_MULT_CONST_GNU, 0, 0],
                               'dataSrc'          :[CLASS_CONST,       CLASS_FILE_SRC_GNU, 0, 0],
                               'carrierScale'     :[CLASS_SCALE,       CLASS_MULT_CONST_GNU, 0, 0],
                               'carrier'          :[CLASS_SINE,        CLASS_SIG_GNU, 0, 0],
                               'dbpskMod'         :[CLASS_DBPSK_TX,    CLASS_DBPSK_TX_GNU, 0, 0],
                               'dbpskEnc'         :[CLASS_DBPSK_ENC,   CLASS_DBPSK_ENC_GNU, 0, 0],
                               'rfIn'             :[CLASS_CONST,       CLASS_USRP_SRC_GNU, 0, 0],
                               'dbpskDemod'       :[CLASS_DBPSK_RX,    CLASS_DBPSK_RX_GNU, 0, 0],
                               'dbpskDec'         :[CLASS_DBPSK_DEC,   CLASS_DBPSK_DEC_GNU, 0, 0],
                               'dataOut'          :[CLASS_USER_OUTPUT, CLASS_FILE_SINK_GNU, 0, 0],
                               'gauss'            :[CLASS_GAUSS,       CLASS_NOISE_GNU, 0, 0],
                               'gaussScale'       :[CLASS_SCALE,       CLASS_MULT_CONST_GNU, 0, 0],
                               'add'              :[CLASS_ADDSUB,      CLASS_ADD_GNU, 0, 0]
                              }
        ###################################################
        ## Provides port names for the respective blocks ##
        ###################################################        
        self.block_port_dict_input = {'rfOut'    :[".input"],
                               'channelFilter'   :[".input"],
                               'channelFilter2'  :[".input"],
                               'basebandScale'   :[".input"],
                               'basebandScale2'  :[".input"],
                               'dataSrc'         :[".input"],
                               'carrierScale'    :[".input"],
                               'carrier'         :[".input"],
                               'dbpskMod'        :[".datain"],
                               'dbpskEnc'        :[".input"],                                      
                               'rfIn'            :[".input"],
                               'dbpskDemod'      :[".rfsig"],
                               'dbpskDec'        :[".input"],
                               'dataOut'         :[".input"],
                               'gaussScale'      :[".input"],
                               'add'             :[".plus"]
                              }
        self.block_port_dict_input_gnu = {'rfOut'    :["0"],
                               'channelFilter'   :["0"],
                               'channelFilter2'  :["0"],
                               'basebandScale'   :["0"],
                               'basebandScale2'  :["0"],
                               'dataSrc'         :["0"],
                               'carrierScale'    :["0"],
                               'carrier'         :["0"],
                               'dbpskMod'        :["0"],
                               'dbpskEnc'        :["0"],                                      
                               'rfIn'            :["0"],
                               'dbpskDemod'      :["0"],
                               'dbpskDec'        :["0"],
                               'dataOut'         :["0"],
                               'gaussScale'      :["0"],
                               'add'             :["0", "1"]
                              }        
        self.block_port_dict_output = {'rfOut'   :[".output"],
                               'channelFilter'   :[".output"],
                               'channelFilter2'  :[".output"],
                               'basebandScale'   :[".output"],
                               'basebandScale2'  :[".output"],
                               'dataSrc'         :[".output"],
                               'carrierScale'    :[".output"],
                               'carrier'         :[".output"],
                               'dbpskMod'        :[".output"],
                               'dbpskEnc'        :[".output"],
                               'rfIn'            :[".output"],
                               'dbpskDemod'      :[".output"],
                               'dbpskDec'        :[".output"],
                               'dataOut'         :[".output"],
                               'gauss'           :[".output"],
                               'gaussScale'      :[".output"],
                               'add'             :[".output"]
                              }
        self.block_port_dict_output_gnu = {'rfOut'   :["0"],
                               'channelFilter'   :["0"],
                               'channelFilter2'  :["0"],
                               'basebandScale'   :["0"],
                               'basebandScale2'  :["0"],
                               'dataSrc'         :["0"],
                               'carrierScale'    :["0"],
                               'carrier'         :["0"],
                               'dbpskMod'        :["0"],
                               'dbpskEnc'        :["0"],
                               'rfIn'            :["0"],
                               'dbpskDemod'      :["0"],
                               'dbpskDec'        :["0"],
                               'dataOut'         :["0"],
                               'gauss'           :["0"],
                               'gaussScale'      :["0"],
                               'add'             :["0"]
                              }
        ###################################################
        ## Provides offset in the x,y plane for blocks   ##
        ###################################################        
        self.offset_dict = {'rfOut'            :[0,  0],
                             'channelFilter'   :[0,  0],
                             'channelFilter2'  :[0,  0],
                             'basebandScale'   :[0,  0],
                             'basebandScale2'  :[0,  0],
                             'dataSrc'         :[0,  0],
                             'carrierScale'    :[50, 0],
                             'carrier'         :[50, 0],
                             'dbpskMod'        :[0,  0],
                             'dbpskEnc'        :[0,  0],
                             'rfIn'            :[0,  0],
                             'dbpskDemod'      :[0,  0],
                             'dbpskDec'        :[0,  0],
                             'dataOut'         :[0,  0],
                             'gauss'           :[50, 50],
                             'gaussScale'      :[50, 50], 
                             'add'             :[0,  0]
                           }
        #######################################################
        ## Provides the initial value of blocks in ptolemy   ##
        ## and gnuradio                                      ##
        ## NOTE: these are setup later in the code according ##
        ## to the metadata associated with the blocks        ##
        #######################################################
        self.value_dict = {'rfOut'           :["None"],
                           'channelFilter'   :["None"],
                           'channelFilter2'  :["None"],
                           'basebandScale'   :["None"],
                           'basebandScale2'  :["None"],                           
                           'dataSrc'         :["None"],
                           'carrierScale'    :["None"],
                           'carrier'         :["None"],
                           'dbpskMod'        :["None"],
                           'dbpskEnc'        :["None"],                           
                           'rfIn'            :["None"],
                           'dbpskDemod'      :["None"],
                           'dbpskDec'        :["None"],                           
                           'dataOut'         :["None"],
                           'gauss'           :["None"],
                           'gaussScale'      :["None"],
                           'add'             :["None"]
                            }
        self.value_dict_gnu = {'rfOut'       :["None"],
                           'channelFilter'   :["None"],
                           'channelFilter2'  :["None"],
                           'basebandScale'   :["None"],
                           'basebandScale2'  :["None"],                           
                           'dataSrc'         :["None"],
                           'carrierScale'    :["None"],
                           'carrier'         :["None"],
                           'dbpskMod'        :["None"],
                           'dbpskEnc'        :["None"],                               
                           'rfIn'            :["None"],
                           'dbpskDemod'      :["None"],
                           'dbpskDec'        :["None"],                               
                           'dataOut'         :["None"],
                           'gauss'           :["None"],
                           'gaussScale'      :["None"],
                           'add'             :["None"]
                            }
        self.block_io_rates = {
                             'rfOut'           :["samplingRate2", "samplingRate2"],
                             'channelFilter'   :["samplingRate",  "samplingRate2"],
                             'channelFilter2'  :["samplingRate2", "samplingRate" ],
                             'basebandScale'   :["samplingRate2", "samplingRate2"],
                             'basebandScale2'  :["samplingRate2", "samplingRate2"],
                             'dataSrc'         :["samplingRate",  "samplingRate" ],
                             'carrierScale'    :["samplingRate2", "samplingRate2"],
                             'carrier'         :["samplingRate2", "samplingRate2"],
                             'dbpskMod'        :["samplingRate",  "samplingRate" ],
                             'dbpskEnc'        :["samplingRate",  "samplingRate" ],
                             'rfIn'            :["samplingRate2", "samplingRate2"],
                             'dbpskDemod'      :["samplingRate",  "samplingRate" ],
                             'dbpskDec'        :["samplingRate",  "samplingRate" ],
                             'dataOut'         :["samplingRate",  "samplingRate" ],
                             'gauss'           :["samplingRate2", "samplingRate2"],
                             'gaussScale'      :["samplingRate2", "samplingRate2"], 
                             'add'             :["samplingRate2", "samplingRate2"]
                           }
        self.top_impl_info = {'consistent'      : False,
                              
                          }
    def __del__(self):
        self.outfile.close()
        self.infile.close()
    def set_param_values(self):
        self.value_dict = {'rfOut'            :["None"],
                           'channelFilter'    :["rc"+self.param_dict["rcFiltCoeff"]+".dat", "samplingRate2/samplingRate", "1"],
                           'channelFilter2'   :["rc"+self.param_dict["rcFiltCoeff"]+".dat", "1", "samplingRate2/samplingRate"],
                           'basebandScale'    :["rfGain"],
                           'dataSrc'          :["7"],
                           'carrierScale'     :["carrierGain"],
                           'carrier'          :["samplingRate", "carrierFreq", "carrierPhase"],
                           'dbpskMod'         :["samplingRate*symbolTime"],
                           'dbpskEnc'         :["1"],
                           'rfIn'             :["None"],
                           'dbpskDemod'       :["recvThresh"],
                           'dbpskDec'         :["1"],                           
                           'dataOut'          :["None"],
                           'gauss'            :["seedValG", "meanValG", "stdValG"],
                           'gaussScale'       :["gaussGain"],
                           'add'              :["None"],
                           'basebandScale2'   :["rfGain2"]
                            }
        self.value_dict_gnu = {'rfOut'        :["samplingRate2", "carrierFreq", "rfGain"],
                           'channelFilter'    :["complex", "1.0"],
                           'channelFilter2'   :["complex", "1.0"],
                           'basebandScale'    :["complex", "bbGain"],
                           'dataSrc'          :["music-tx"+self.param_dict["dataName"]+".dat", "float", "False"],
                           'carrierScale'     :["float", "carrierGain"],
                           'carrier'          :["samplingRate", CLASS_SINE_GNU, "500.0", "carrierGain"],
                           'dbpskEnc'         :["float", "samplingRate2/samplingRate", "1"],
                           'dbpskMod'         :["dbpsk", "samplingRate2/samplingRate", "0.35","yes", "False", "False"],
                           'rfIn'             :["samplingRate2", "carrierFreq", "rfGain2"],
                           'dbpskDemod'       :["dbpsk","samplingRate2/samplingRate","0.35","6.28/100.0", "6.28/100.0", "6.28/100.0", "True", "False", "False", "False"],
                           'dbpskDec'         :["float", "-1"],
                           'dataOut'          :["music-rx"+self.param_dict["dataName"]+".dat", "float", "False"],
                           'gauss'            :["complex", CLASS_GAUSS_GNU, "0.3", "0"],
                           'gaussScale'       :["complex", "gaussGain"],
                           'add'              :["complex", "2"],
                           'basebandScale2'   :["complex", "bbGain2"]
                            }
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
    def print_top_impl_info(self):
        for item in self.top_impl_info.keys():
            print item, "= ", self.top_impl_info[item]
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
    def print_schedule(self):
        print "Firing Schedule"
        print self.sched
    def calculate_schedule(self):
        [errorCond, self.sched] = setup_sched_lp(self.top_matrix)
        return errorCond
    def is_consistent(self):
        self.rankVal = np.linalg.matrix_rank(self.top_matrix)
        num_actors   = len(self.top_matrix[0])
        if self.rankVal < num_actors:
            self.top_impl_info["consistent"] = True
        else:
            self.top_impl_info["consistent"] = False
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
                    self.chan_dict_temp[token_name] = ["", ""]

            elif self.is_process_body(line):
                process_body = True
                
            line = self.infile.readline()

        return True
    def finalize_top_matrix_chan_dict(self):
        chan_dict = {}
        for key, value in self.chan_dict_temp.items():
            if value[0] != "" and value[1] != "":
                if self.is_ignore_chan(key) == False:
                    self.chan_dict[key] = self.chan_dict_temp[key]
                    self.chan_list.append(key)
        len_proc = len(self.proc_list)
        len_chan = len(self.chan_list)
        self.top_matrix = np.zeros((len_chan, len_proc))
        
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
    def is_ignore_chan(self, proc_name):
        len_list = len(IGNORE_CHAN);
        for i in range(len_list):
            if proc_name == IGNORE_CHAN[i]:
                return True
        return False
    def append_rate(self, rate_pass):
        if rate_pass not in self.rate_list:
            self.rate_list.append(rate_pass)
            
    def parse_channel_directions(self, line):
        tokens     = line.split()
        tokens     = self.clean_from_punc(tokens)
        len_tokens = len(tokens)
        chan_name  = ""
        chan_dir   = ""
        rate_in    = 0
        rate_out   = 0
        
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
                            self.chan_dict_temp[chan_name][OUT_CHAN] = proc_name
                            if proc_name == INIT_PROC:
                                self.init_chans = self.init_chans+[chan_name]
                        elif chan_dir == "in":
                            self.chan_dict_temp[chan_name][IN_CHAN] = proc_name
                        elif chan_dir == "debug":
                            chan_dir = chan_dir
                        else:                        
                            return False
                        if chan_dir != "debug":
                            if ((proc_name in self.proc_list) ==
                                False):
                                if(self.is_ignore_proc(proc_name)==False):
                                    self.proc_list.append(proc_name)
                                    self.proc_dict[proc_name] = [0,0,0]
                                    self.proc_dict[proc_name][PROC_LIST_IND] = len(self.proc_dict)-1
                                    #Get the parameter name indicating
                                    #the I/O data rate then get the
                                    #physical value from the parameter dictionary
                                    rate_in  = self.param_dict[self.block_io_rates[proc_name][0]]
                                    rate_out = self.param_dict[self.block_io_rates[proc_name][1]]
                                    self.proc_dict[proc_name][PROC_RATE_IN]  = int(float(rate_in))
                                    self.proc_dict[proc_name][PROC_RATE_OUT] = int(float(rate_out))
                                    self.append_rate(int(float(rate_in)))
                                    self.append_rate(int(float(rate_out)))
    def parse_proc_connection(self):
        self.finalize_top_matrix_chan_dict()
        len_chans = len(self.chan_list)
        proc_gcd = self.proc_rate_gcd()

        for i in range(len_chans):
            
            chan_name = self.chan_list[i]
            
            proc_out  = self.chan_dict[chan_name][0]
            proc_in   = self.chan_dict[chan_name][1]
            if proc_out != "":
                proc_out_index  = self.proc_dict[proc_out][PROC_LIST_IND]
                if (proc_in != ""):                
                    proc_in_index   = self.proc_dict[proc_in][PROC_LIST_IND]
                self.top_matrix[i][proc_out_index] = self.proc_dict[proc_out][PROC_RATE_OUT]/proc_gcd
                self.top_matrix[i][proc_in_index]  = -self.proc_dict[proc_in][PROC_RATE_IN]/proc_gcd
            else:
                print "ERROR: in parse_proc_connection, found an empty output process"
                exit(1)                

    # function finds the gcd of the I/O sampling rates of the various
    # blocks recursively
    def proc_rate_gcd(self):
        return self.find_gcd([], self.rate_list)
    def find_gcd(self, one, two):
        list_len = len(two)
        if list_len > 1:
            return self.find_gcd(two[0], two[1:])
        else:
            return fractions.gcd(one, two[0])
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
    def write_to_file(self, pgen, type_str, class_str, name, value, offset, mode):
        if mode is PTOLEMY:
            return pgen.write_to_ptolemy_file(type_str, class_str, name, value, offset)
        elif mode is GNURADIO:
            return pgen.write_to_gnuradio_file(type_str, class_str, name, value, offset)
    def link_in_file(self, pgen, out_unit, in_unit, name_relation, mode):
        if mode is PTOLEMY:
            return pgen.link_in_ptolemy_file(out_unit, in_unit, name_relation)
        elif mode is GNURADIO:
            return pgen.link_in_gnuradio_file(out_unit, in_unit, name_relation)
    def generate_code(self, mode):
        
        filename = self.get_filename(infile_name)
        model_name = filename

        if mode is PTOLEMY:
            filename = filename + ".xml"
            pgen = ptolemy_writer(filename, model_name)
        elif mode is GNURADIO:
            filename = filename + ".grc"
            pgen = gnuradio_writer(filename, model_name)
        else:
            print "ERROR in generate_code: UNKNOW code generation mode= ", mode


        # Choose MoC
        if mode is PTOLEMY:
            node1 = self.write_to_file(pgen, DIRECT, CLASS_SDF, NAME_SDF, "None", 0, mode)
            pgen.top_element.appendChild(node1)

        # Generate and Instantiate Parameters
        len_list = len(self.param_list)
        for i in range(len_list):
            param_name = self.param_list[i]
            param_val  = self.param_dict[param_name]
            param_val  = self.check_if_int_enforce(param_name, param_val)
            param_val  = self.check_if_long_enforce(param_name, param_val)
            
            if mode is PTOLEMY:
                node1      = self.write_to_file(pgen, PARAM, CLASS_PARAMETER, param_name, [param_val], 0, mode)
            elif mode is GNURADIO:
                node1      = self.write_to_file(pgen, PARAM_GNU, CLASS_VARIABLE, param_name, [param_val], 0, mode)

            pgen.top_element.appendChild(node1)

        # Generate and Instantiate Blocks
        len_list = len(self.proc_list)
        for i in range(len_list):
            block_name   = self.proc_list[i]
            class_name   = self.block_map_dict[block_name][mode]
            block_offset = self.offset_dict[block_name][mode]
            if mode == PTOLEMY:
                block_value  = self.value_dict[block_name]
                node1 = self.write_to_file(pgen, BLOCK, class_name, block_name, block_value, block_offset, mode)
            elif mode == GNURADIO:              
                block_value  = self.value_dict_gnu[block_name]
                node1 = self.write_to_file(pgen, BLOCK_GNU, class_name, block_name, block_value, block_offset, mode)
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
                Out_index = self.get_port_count(block_out_name, "output")
                in_index  = self.get_port_count(block_in_name, "input")
                if mode == PTOLEMY:
                    chan1 = self.write_to_file(pgen, CH, CLASS_NAMED_IO_RELATION, chan_name, "no", 0, mode)
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
                elif mode == GNURADIO:
                    chana = pgen.link_in_gnuradio_file(block_out_name, Out_index, block_in_name, in_index)
                    pgen.top_element.appendChild(chana)
                    out_lim = len(self.block_port_dict_output_gnu[block_out_name])
                    in_lim  = len(self.block_port_dict_input_gnu[block_in_name])
                    
                if out_lim > (out_index+1):
                    self.inc_port_count(block_out_name, "output")
                if in_lim > (in_index+1):
                    self.inc_port_count(block_in_name, "input")
        self.reset_port_count()
        pgen.write_to_xmlfile()
        return True

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
    top_handler.set_param_values()
    top_handler.parse_input_file_channels()

    top_handler.parse_proc_connection()

    top_handler.print_top_matrix()

    
    print "Genertaing Ptolemy simulation ..."
    top_handler.generate_code(PTOLEMY)
    print "Generating GNU Radio project file ..."
    top_handler.generate_code(GNURADIO)
    errorCond = top_handler.calculate_schedule()
    top_handler.print_schedule()
    top_handler.is_consistent()

    top_handler.print_top_impl_info()
