#!/usr/bin/env python

import sys, string, types, os, copy
import getopt
import numpy as np
#from xml.dom.minidom import parse, parseString, Document,
#getDOMImplementation
from xml.dom import EMPTY_NAMESPACE, XML_NAMESPACE
from gnuradio_param import *
import pxdom

class gnuradio_writer:
    def __init__(self, outfile_name, model_name):
        self.outfile = file(outfile_name, 'w')
        self.outfile.flush()
        self.model_name = model_name
        self.outfile_name = outfile_name

        self.impl = pxdom.getDOMImplementation('')

        self.doctype = self.impl.createDocumentType(FLOW_GNU, None, None)
        self.doc = self.impl.createDocument(EMPTY_NAMESPACE, FLOW_GNU,self.doctype)
        self.top_element = self.doc.documentElement

        init_node0 = self.write_to_gnuradio_file(BLOCK_GNU, CLASS_OPTIONS, "OCCAM_generated", ["4096, 4096"], NONE)
        self.top_element.appendChild(init_node0)        
        
        self.param_loc = copy.deepcopy(PARAM_ORIG)
        self.block_loc = copy.deepcopy(BLOCK_ORIG)

    def __del__(self):
        self.outfile.close()
        
    def write_element(self, tag_str, key_str, value_str):
        if tag_str != PARAM_GNU:
            node  = self.doc.createElement(tag_str)
            if key_str != NONE:
                node2 = self.doc.createTextNode(key_str)
                node.appendChild(node2)
        else:
            node  = self.doc.createElement(tag_str)
            if key_str != NONE:
                node1 = self.doc.createElement("key")
                node2 = self.doc.createTextNode(key_str)
                node.appendChild(node1)
                node1.appendChild(node2)
            if value_str != NONE:
                node1 = self.doc.createElement("value")
                node2 = self.doc.createTextNode(value_str)
                node.appendChild(node1)
                node1.appendChild(node2)
        return node
    def write_to_xmlfile(self):
        ser = self.impl.createLSSerializer()
        ser.domConfig.setParameter('format-pretty-print', True)
        ser.writeToURI(self.doc, 'tmp_xml_read.xml')
        
        infile_temp = file ('tmp_xml_read.xml', 'r')
        line = infile_temp.readline()
        i = 0
        while line:
            self.outfile.write(line)
            line = infile_temp.readline()
            # Fix pxdom & XML escaping issue
            line = line.replace("&amp;", "&")            
            i = i + 1
        
        #outfile_temp.close()
        infile_temp.close()

    def print_xmlfile(self):
        
        #print self.doc.saveXML()

        self.outfile.close()
        infile_temp = file(self.outfile_name, 'r')

        print "XML File="
        line = infile_temp.readline()
        while line:
            sys.stdout.write(line)
            line = infile_temp.readline()
        infile_temp.close()
        print "\n"

    def gnuradio_location_update(self, req_type, offset):

        if req_type is PARAM_GNU:
            self.param_loc[Y_AXIS] = self.param_loc[Y_AXIS] + PARAM_STEP
            x_axis_temp = self.param_loc[X_AXIS] + offset
            loc_str = "(" + str(x_axis_temp) + ", " + str(self.param_loc[Y_AXIS]) + ")"
        elif req_type is BLOCK_GNU:
            self.block_loc[X_AXIS] = self.block_loc[X_AXIS] + BLOCK_STEP
            y_axis_temp = self.block_loc[Y_AXIS] + offset
            loc_str = "(" + str(self.block_loc[X_AXIS]) + ", " + str(y_axis_temp) + ")"
        elif req_type is DIRECT_GNU:
            loc_str = "(" + str(DIRECT_LOC[X_AXIS]) + ", " + str(DIRECT_LOC[Y_AXIS]) + ")"
        else:
            exit("ERROR: Found in gnuradio_location_update method. Parameter passed is incompatible\n")
        return copy.deepcopy(loc_str)
    def convert_loc_to_str(self, loc):
        loc_str = "{" + str(loc[X_AXIS]) + ", " + str(loc[Y_AXIS]) + "}"
        return copy.deepcopy(loc_str)        
    # used to generate locations for virteces without updating the
    # global objection location parameters
    def current_location(self, type_str):
        if type_str == PARAM_GNU:
            return copy.deepcopy(self.param_loc)
        elif type_str == BLOCK_GNU:
            return copy.deepcopy(self.block_loc)
        else:
            exit("ERROR: Found in current_location method.  Invalid request\n")
    def set_location(self, type_str, loc):
        if type_str == PARAM_GNU:
            self.param_loc = copy.deepcopy(loc)
        elif type_str == BLOCK_GNU:
            self.block_loc = copy.deepcopy(loc)
        else:
            exit("ERROR: Found in current_location method.  Invalid request\n")
    def gnuradio_location_gen(self, offset):

        x_axis_temp = self.block_loc[X_AXIS] + BLOCK_STEP/2
        y_axis_temp = self.block_loc[Y_AXIS] + offset
        loc_str = "{" + str(x_axis_temp) + ", " + str(y_axis_temp) + "}"
       
        return copy.deepcopy(loc_str)
    #def write_element(self, tag_str, name_str, class_str, value_str):
    def write_to_gnuradio_file(self, type_str, class_str, name, value, offset):
        # each block start with a BLOCK tag and a keytag indicating
        # the type of block it is
        # The Block to be implemented
        node1 = self.write_element(BLOCK_GNU, NONE, NONE)
        # the type of the block
        node2 = self.write_element(KEY_GNU,   class_str, NONE)
        node1.appendChild(node2)
        #if class_str != CLASS_OPTIONS:
        # the name of the block
        node2 = self.write_element(PARAM_GNU, "id", name)
        node1.appendChild(node2)
        # enable block
        node2 = self.write_element(PARAM_GNU, "enabled", "True")
        node1.appendChild(node2)
        if type_str is PARAM_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(PARAM_GNU, offset)
                node2 = self.write_element(PARAM_GNU, "value", value[0])                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "_coordinate", loc_str)                
                node1.appendChild(node2)
        elif type_str is BLOCK_GNU:
            if class_str is CLASS_OPTIONS:
                node2 = self.write_element(PARAM_GNU, "title", "")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "author","Almohanad Fayez")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "description", "")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "window_size", value[0])                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "generate_options", "wx_gui")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "category", "Custom")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "run_options", "prompt")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "run", "True")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "max_nouts", "0")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "realtime_scheduling", "")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "_coordinate", "(10, 10)")                
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "_rotation", "0")                
                node1.appendChild(node2)
            elif class_str is CLASS_INTERP_FIR_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)
                # 1- name of file with taps
                # 2- type of filter "ccc", "ccf", ... etc
                # 3- interpolation factor
                infile_temp = open(value[0], 'r')
                taps_str = infile_temp.read()
                node2 = self.write_element(PARAM_GNU, "type", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "interp", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "taps", taps_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)                
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)                
                infile_temp.close()                
            elif class_str is CLASS_FIR_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- name of file with taps
                # 2- type of filter "ccc", "ccf", ... etc
                # 3- decimation factor
                infile_temp = open(value[0], 'r')
                taps_str = infile_temp.read()
                node2 = self.write_element(PARAM_GNU, "type", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "decim", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "taps", taps_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)                
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)                
                infile_temp.close()
            elif class_str is CLASS_MULT_CONST_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- type (e.g. complex)
                # 2- const value
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "const", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "vlen", "1")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_DBPSK_TX_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- type (e.g. dbpsk)
                # 2- samples per symbol
                # 3- excess bw
                # 4- gray coded? yes, no
                # 5- verbose True or False
                # 6- log, True or False
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "samples_per_symbol", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "excess_bw", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "gray_coded", value[3])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "verbose", value[4])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "log", value[5])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_DBPSK_ENC_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- type (e.g. float)
                # 2- samples per symbol
                # 3- bits per symbol (e.g. 1 for dbpsk)
                # - access_code
                # - pad for usrp (True)
                # - payload length (0 = auto)
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "samples_per_symbol", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "bits_per_symbol", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "access_code", "")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "pad_for_usrp", "True")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "payload_length", "0")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_DBPSK_DEC_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)
                # 1- type (float)
                #  - access code (fixed "")
                # 2- threshold (-1 auto ?)
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "access_code", "")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "threshold", value[1])
                node1.appendChild(node2)                                
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)                                

            elif class_str is CLASS_DBPSK_RX_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- type (e.g. dbpsk)
                # 2- samples per symbol
                # 3- excess bw
                # 4- freq_bw
                # 5- phase bw
                # 6- timing bw
                # 7- gray coded
                # 8- verbose
                # 9- log
                # 10- sync_out, False for differential
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "samples_per_symbol", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "excess_bw", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "freq_bw", value[3])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "phase_bw", value[4])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "timing_bw", value[5])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "gray_coded", value[6])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "verbose", value[7])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "log", value[8])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "sync_out", value[9])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_SCOPE_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1-  (0)type (e.g. float, complex)
                # 2-  (1)title
                # 3-  (2)samp_rate
                # 4-  (-)v_scale (0-fixed)
                # 5-  (-)v_offset (0-fixed)
                # 6-  (3)t_scale  (e.g. 1/freq)
                # 7-  (-)ac_couple (False)
                # 8-  (-)xy_mode (False)
                # 9-  (4)num_inputs (e.g. 1)
                # 10- (-)win_size (e.g. "")
                # 11- (-)grid_pos ""
                # 12- (-)trig_mode (fixed gr.gr_TRIG_MODE_AUTO)
                # 13- (5)y_axis_labl
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "title", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "samp_rate", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "v_scale", "0")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "v_offset", "0")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "t_scale", value[3])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "ac_couple", "False")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "num_inputs", value[4])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "win_size", "")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "grid_pos", "")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "trig_mode", "gr.gr_TRIG_MODE_AUTO")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "y_axis_label", value[5])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)                
            elif class_str is CLASS_ADD_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- type (e.g. complex)
                # 2- number of inputs
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "type", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_NOISE_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- Type (e.g. complex)
                # 2- Noise Type
                # 3- Amplitude
                # 4- Seed
                node2 = self.write_element(PARAM_GNU, "type", value[0])
                node1.appendChild(node2)                                
                node2 = self.write_element(PARAM_GNU, "noise_type", value[1])
                node1.appendChild(node2)                                
                node2 = self.write_element(PARAM_GNU, "amp", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "seed", value[3])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, COORDINATE, loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, ROTATION, "0")
                node1.appendChild(node2)
            elif class_str is CLASS_SIG_GNU:
                # set location for block
                loc_str = self.gnuradio_location_update(BLOCK_GNU, offset)                
                # 1- sampling_freq
                # 2- waveform
                # 3- frequency
                # 4- amplitude
                node2 = self.write_element(PARAM_GNU, "type", "float")                
                node1.appendChild(node2)                
                node2 = self.write_element(PARAM_GNU, "samp_rate", value[0])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "waveform", value[1])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "freq", value[2])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "amp", value[3])
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "offset", "0")
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "_coordinate", loc_str)
                node1.appendChild(node2)
                node2 = self.write_element(PARAM_GNU, "_rotation", "0")
                node1.appendChild(node2)                
            else:
                print "ERROR: Found in write_to_gnuradio BLOCK method. Parameter passed is incompatible= ",  class_str
        #elif type_str is CH_GNU:
        #    print "channel"            
        #elif type_str is DIRECT_GNU:
        #    print "director"            
        #elif type_str is PORT_GNU:
        #    print "port"            
        else:
            print "ERROR: Found in write_to_gnuradio method. Parameter passed is incompatible= ",  type_str
            exit(-1)            
        return node1
    def link_in_gnuradio_file(self, block_out, out_index, block_in, in_index):
        node1 = self.doc.createElement("connection")

        if block_out != "None":
            node2 = self.doc.createElement("source_block_id")
            node3 = self.doc.createTextNode(block_out)
            node1.appendChild(node2)
            node2.appendChild(node3)
        if block_in != "None":
            node2 = self.doc.createElement("sink_block_id")
            node3 = self.doc.createTextNode(block_in)
            node1.appendChild(node2)
            node2.appendChild(node3)
        if block_out != "None":
            node2 = self.doc.createElement("source_key")
            node3 = self.doc.createTextNode(str(out_index))
            node1.appendChild(node2)
            node2.appendChild(node3)
        if block_in != "None":
            node2 = self.doc.createElement("sink_key")
            node3 = self.doc.createTextNode(str(in_index))
            node1.appendChild(node2)
            node2.appendChild(node3)

        return node1

def test_gnuradio():
    print "Hello!"
    filename   = "xml-tmp.grc"
    model_name = "xml-tmp"
    pgen = gnuradio_writer(filename, model_name)

    pgen.write_to_xmlfile()
