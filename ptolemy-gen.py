#!/usr/bin/env python

import sys, string, types, os, copy
import getopt
import numpy as np
#from xml.dom.minidom import parse, parseString, Document,
#getDOMImplementation
from xml.dom import EMPTY_NAMESPACE, XML_NAMESPACE
from ptolemy_param import *
import pxdom

XML_HEADER1 = "<?xml version=\"1.0\" standalone=\"no\"?>"
XML_HEADER2 = """<!DOCTYPE entity PUBLIC \"-//UC Berkeley//DTD MoML 1//EN\"
\"http://ptolemy.eecs.berkley.edu/xml/dtd/MoML_1.dtd\">
"""
PARAM_COLOR = [0.0, 0.0, 1.0, 1.0]
PARAM_ORIG  = [1,0]
PARAM_STEP  = 15
PARAM_OFFSET = 25

BLOCK_ORIG  = [0, 200]
BLOCK_STEP  = 200
BLOCK_OFFSET = 25

DIRECT_LOC = [200, 10]
ERROR_LOC = "{-1, -1}"

X_AXIS = 0
Y_AXIS = 1

PARAM  = 0
BLOCK  = 1
DIRECT = 2
CH = 3

SDF = 0
#XML_INIT = "entity "
class ptolemy_writer:
    def __init__(self, outfile_name, model_name):
        self.outfile = file(outfile_name, 'w')
        self.outfile.flush()
        self.model_name = model_name
        self.outfile_name = outfile_name

        self.impl = pxdom.getDOMImplementation('')

        self.doctype = self.impl.createDocumentType("entity", None, None)
        self.doc = self.impl.createDocument(EMPTY_NAMESPACE, 'entity',self.doctype)
        self.top_element = self.doc.documentElement

        init_node0 = self.write_element(PROP, NAME_WIN_PROP, CLASS_WIN_PROP, VAL_WIN_PROP)
        init_node1 = self.write_element(PROP, NAME_VERG_SIZE, CLASS_SIZE_ATTR, VAL_VERG_SIZE_ATTR)
        init_node2 = self.write_element(PROP, NAME_VERG_ZOOM, CLASS_EXP_PARAM, VAL_VERG_ZOOM)
        init_node3 = self.write_element(PROP, NAME_VERG_CENTER, CLASS_EXP_PARAM, VAL_VERG_CENTER)

        self.top_element.appendChild(init_node0)        
        self.top_element.appendChild(init_node1)
        self.top_element.appendChild(init_node2)
        self.top_element.appendChild(init_node3)        
        
        self.param_loc = copy.deepcopy(PARAM_ORIG)
        self.block_loc = copy.deepcopy(BLOCK_ORIG)

    def __del__(self):
        self.outfile.close()
        
    def write_element(self, tag_str, name_str, class_str, value_str):

        node = self.doc.createElement(tag_str)

        if (name_str != "None"):        
            node.setAttribute("name", name_str)
        if (class_str != "None"):        
            node.setAttribute("class", class_str)
        if (value_str != "None"):
            node.setAttribute("value", value_str)        

        return node

    def write_to_xmlfile(self):
        
        ser = self.impl.createLSSerializer()
        ser.domConfig.setParameter('format-pretty-print', True)
        ser.writeToURI(self.doc, 'tmp_xml_read.xml')
        
        infile_temp = file ('tmp_xml_read.xml', 'r')

        line = infile_temp.readline()
        self.outfile.write(XML_HEADER1)
        self.outfile.write("\n")
        self.outfile.write(XML_HEADER2)

        line = infile_temp.readline()
        mod_model_name = "<entity name=\""+self.model_name+"\" class=\"ptolemy.actor.TypedCompositeActor\">\n"
        self.outfile.write(mod_model_name)
        
        line = infile_temp.readline()
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

    def ptolemy_location_update(self, req_type, offset):

        if req_type is PARAM:
            self.param_loc[Y_AXIS] = self.param_loc[Y_AXIS] + PARAM_STEP
            x_axis_temp = self.param_loc[X_AXIS] + offset
            loc_str = "{" + str(x_axis_temp) + ", " + str(self.param_loc[Y_AXIS]) + "}"
        elif req_type is BLOCK:
            self.block_loc[X_AXIS] = self.block_loc[X_AXIS] + BLOCK_STEP
            y_axis_temp = self.block_loc[Y_AXIS] + offset
            loc_str = "{" + str(self.block_loc[X_AXIS]) + ", " + str(y_axis_temp) + "}"
        elif req_type is DIRECT:
            loc_str = "{" + str(DIRECT_LOC[X_AXIS]) + ", " + str(DIRECT_LOC[Y_AXIS]) + "}"            
        else:
            exit("ERROR: Found in ptolemy_location_update method. Parameter passed is incompatible\n")
        return copy.deepcopy(loc_str)
    def convert_loc_to_str(self, loc):
        loc_str = "{" + str(loc[X_AXIS]) + ", " + str(loc[Y_AXIS]) + "}"
        return copy.deepcopy(loc_str)
        
    # used to generate locations for virteces without updating the
    # global objection location parameters
    def current_location(self, type_str):
        if type_str == PARAM:
            return copy.deepcopy(self.param_loc)
        elif type_str == BLOCK:
            return copy.deepcopy(self.block_loc)
        else:
            exit("ERROR: Found in current_location method.  Invalid request\n")
    def set_location(self, type_str, loc):
        if type_str == PARAM:
            self.param_loc = copy.deepcopy(loc)
        elif type_str == BLOCK:
            self.block_loc = copy.deepcopy(loc)
        else:
            exit("ERROR: Found in current_location method.  Invalid request\n")
    def ptolemy_location_gen(self, offset):

        x_axis_temp = self.block_loc[X_AXIS] + BLOCK_STEP/2
        y_axis_temp = self.block_loc[Y_AXIS] + offset
        loc_str = "{" + str(x_axis_temp) + ", " + str(y_axis_temp) + "}"
       
        return copy.deepcopy(loc_str)

    # offset = offset in x-axis for parameters and y-axis for blocks.
    # Used to make things look better visually
    def write_to_ptolemy_file(self, type_str, class_str, name, value, offset):
        if type_str is PARAM:

            node1 = self.write_element(PROP, name, CLASS_PARAMETER, value)
            node1 = self.write_element(PROP, name, CLASS_PARAMETER, value)
            node2 = self.write_element(PROP, NAME_ICON, CLASS_ICON, "None")
            node3 = self.write_element(PROP, NAME_COLOR, CLASS_COLOR, VAL_COLOR_PARAMETER)

            loc_str = self.ptolemy_location_update(PARAM, offset)
            node4 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)

            node1.appendChild(node2)
            node2.appendChild(node3)
            node1.appendChild(node4)
            
        elif type_str is BLOCK:
            if class_str is CLASS_MULTDIV:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
            elif class_str is CLASS_SCALE:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, NAME_ICON, CLASS_ATTR_ICON, "None")
                node3 = self.write_element(PROP, NAME_ATTR, CLASS_STR_ATTR, "factor")
                node4 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node2.appendChild(node3)
                node1.appendChild(node4)
                
            elif class_str is CLASS_SINE:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "samplingFrequency", CLASS_PARAMETER, "sampling_freq")
                node3 = self.write_element(PROP, "frequency", CLASS_PORT_PARAM, "carrier_freq")
                node4 = self.write_element(PROP, "phase", CLASS_PORT_PARAM, "carrier_phase")
                node5 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                node1.appendChild(node4)
                node1.appendChild(node5)
            elif class_str is CLASS_DELAY:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "initialOutputs", CLASS_PARAMETER, value)
                node3 = self.write_element(PROP, NAME_ICON, CLASS_BICON, "None")
                node4 = self.write_element(PROP, NAME_ATTR, CLASS_STR_ATTR, "initialOutputs")
                node5 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                node3.appendChild(node4)
                node1.appendChild(node5)
            elif class_str is CLASS_FIR:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                infile_temp = open(value, 'r')
                taps_str = infile_temp.read()
                taps_str = "{"+taps_str+"}"
                node2 = self.write_element(PROP, NAME_TAPS, CLASS_PARAMETER, taps_str)
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                infile_temp.close()
            elif class_str is CLASS_REPEAT:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "numberOfTimes", CLASS_PARAMETER, "sampling_freq*symbol_time")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
            elif class_str is CLASS_CHOP:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "numberToRead", CLASS_PARAMETER, value)
                node3 = self.write_element(PROP, "numberToWrite", CLASS_PARAMETER, "1")
                node4 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                node1.appendChild(node4)
            elif class_str is CLASS_COMP:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "comparison", CLASS_STR_ATTR, "&gt;")
                node3 = self.write_element(PROP, "style", CLASS_CHOICE_STYLE, "None")
                node4 = self.write_element(PROP, "gt", CLASS_STR_ATTR, "&gt;")
                node5 = self.write_element(PROP, "ge", CLASS_STR_ATTR, "&gt;")
                node6 = self.write_element(PROP, "lt", CLASS_STR_ATTR, "&lt;")
                node7 = self.write_element(PROP, "le", CLASS_STR_ATTR, "&lt;=")
                node8 = self.write_element(PROP, "eq", CLASS_STR_ATTR, "==")
                node1.appendChild(node2)
                node2.appendChild(node3)
                node3.appendChild(node4)
                node3.appendChild(node5)
                node3.appendChild(node6)
                node3.appendChild(node7)
                node3.appendChild(node8)

                node2 = self.write_element(PROP, NAME_ICON, CLASS_ATTR_ICON, "None")
                node3 = self.write_element(PROP, NAME_ATTR, CLASS_STR_ATTR, "comparison")
                node1.appendChild(node2)
                node2.appendChild(node3)
                
                node2 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                
            elif class_str is CLASS_CONST:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, "value", CLASS_PARAMETER, value)
                node3 = self.write_element(PROP, NAME_ICON, CLASS_BICON, "None")
                node4 = self.write_element(PROP, NAME_ATTR, CLASS_STR_ATTR, "value")
                node5 = self.write_element(PROP, NAME_DISP_WIDTH, CLASS_PARAMETER, "60")
                node6 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                node3.appendChild(node4)
                node3.appendChild(node5)
                node1.appendChild(node6)

            elif class_str is CLASS_BOOL_ANY:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node1.appendChild(node2)
            elif class_str is CLASS_SEQ_PLOT:
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(ENT, name, class_str, "None")
                node2 = self.write_element(PROP, NAME_WIN_PROP, CLASS_WIN_PROP, "None")
                node3 = self.write_element(PROP, NAME_PLOT_SIZE, CLASS_SIZE_ATTR, "None")    
                node4 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
                node1.appendChild(node4)
                
            # User Defined Composite Blocks
            elif class_str is CLASS_DIFF_ENC:
                name_inport = "input"
                name_outport = "output"
                name_rel_inport = "inputCh"

                name_data_bitstream = "Data to Bitstream"
                name_rel_data_bitstream = "databitstreamCh"
                name_dbpsk_choice = "DBPSK Bitstream Logic Level"
                name_rel_dbpsk_choice = "dbpskchoiceCh"
                
                name_delay = "SampleDelay"
                name_rel_delay = "delayCh"

                name_bool_any = "Boolean To Anything"
                name_rel_bool_any = "booltoanythingCh"
                
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport, "no", 0)
                node0.appendChild(chan1)


                #####################################################################
                ## Data to Bitstream
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DATA_BITSTREAM, name_data_bitstream, "None", 0)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_inport, name_data_bitstream+".input", name_rel_inport)
                node0.appendChild(chana)
                node0.appendChild(chanb)


                
                #####################################################################
                ## DBPSK Choice
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DBPSK_CHOICE, name_dbpsk_choice, "None", 0)
                node0.appendChild(node1)


                #####################################################################
                ## DELAY
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_BOOL_ANY, name_bool_any, "None", 100)
                node0.appendChild(node1)

                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_bool_any, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_bool_any+".output", name_delay+".input", name_rel_bool_any)
                node0.appendChild(chana)
                node0.appendChild(chanb)
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DELAY, name_delay, "{false}", 100)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_delay, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_delay+".output", name_dbpsk_choice+".datain", name_rel_delay)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_data_bitstream, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_data_bitstream+".output", name_dbpsk_choice+".choice", name_rel_data_bitstream)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_dbpsk_choice, "yes", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_dbpsk_choice+".output", name_outport, name_rel_dbpsk_choice)
                node0.appendChild(chana)
                node0.appendChild(chanb)
                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_dbpsk_choice, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file("None", name_bool_any+".input", name_rel_dbpsk_choice)
                #node0.appendChild(chana)
                node0.appendChild(chanb)                

                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None", "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)

                self.set_location(BLOCK, orig_loc)

                return node0
            elif class_str is CLASS_DATA_BITSTREAM:
                name_inport = "input"
                name_outport = "output"
                
                name_rel_inport = "inputCh"
                
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport, "no", 0)
                node0.appendChild(chan1)

                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None", "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)

                self.set_location(BLOCK, orig_loc)

                return node0
            elif class_str is CLASS_DBPSK_CHOICE:
                name_inport1 = "datain"
                name_inport2 = "choice"
                name_outport = "output"
                
                name_rel_inport1 = "datainCh"
                name_rel_inport2 = "choiceCh"                
                
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport1, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport1, "no", 0)
                node0.appendChild(chan1)
                node1 = self.write_element(PORT, name_inport2, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport2, "no", 0)
                node0.appendChild(chan1)

                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None", "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)

                self.set_location(BLOCK, orig_loc)

                return node0                                           
            elif class_str is CLASS_DBPSK_MOD:
                name_inport1 = "modin"
                name_inport2 = "carrier"
                name_outport = "output"
                
                name_rel_inport1 = "modinCh"
                name_rel_inport2 = "carrierCh"                
                
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport1, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport1, "no", 0)
                node0.appendChild(chan1)
                node1 = self.write_element(PORT, name_inport2, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport2, "no", 0)
                node0.appendChild(chan1)

                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None", "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)

                self.set_location(BLOCK, orig_loc)

                return node0                
            elif class_str is CLASS_DBPSK_TX:
                name_inport1 = "carrier"
                name_inport2 = "datain"
                name_outport = "output"
                name_diff_enc = "Differential Encoder"
                name_repeat = "Repeat Block"
                name_dbpsk_mod = "DBPSK Modulator"
                
                name_rel_inport1 = "carrierCh"
                name_rel_inport2 = "datainCh"
                name_rel_diff_enc = "diffencCh"
                name_rel_repeat = "repeatCh"
                name_rel_dbpsk_mod = "dbpskModCh"
                
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport1, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport1, "no", 0)
                node0.appendChild(chan1)

                node1 = self.write_element(PORT, name_inport2, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)

                #####################################################################
                ## DIFFERENTIAL ENCODER
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DIFF_ENC, name_diff_enc, "None", 0)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport1, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_inport1, name_diff_enc+".input", name_rel_inport1)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                #####################################################################
                ## REPEAT 
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_REPEAT, name_repeat, "None", 0)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_diff_enc, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_diff_enc+".output", name_repeat+".input", name_rel_diff_enc)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                #####################################################################
                ## DBPSK Modulator
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DBPSK_MOD, name_dbpsk_mod, "None", 0)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_repeat, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_repeat+".output", name_dbpsk_mod+".modin", name_rel_repeat)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_dbpsk_mod, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_dbpsk_mod+".output", name_outport, name_rel_dbpsk_mod)
                node0.appendChild(chana)
                node0.appendChild(chanb)

                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport2, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_inport2, name_dbpsk_mod+".carrier", name_rel_inport2)
                node0.appendChild(chana)
                node0.appendChild(chanb)                                
                #####################################################################
                
                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None", "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)

                self.set_location(BLOCK, orig_loc)

                return node0                
            elif class_str is CLASS_DBPSK_RX:

                name_inport1 = "rfsig"
                name_inport2 = "rfsig"
                name_outport = "output"
                
                name_mult  = name+" Multiply Here"
                name_delay = name+" SDF Feedback Delay"
                name_fir   = name+" Low Pass Filter"
                name_chop  = name+" Downsample Unit"
                name_comp  = name+" Comparator Unit"
                name_const = name+" Thrshold Value"

                name_rel_inport = "inportChanO"
                name_rel_multdiv = "multdivChanO"
                name_rel_fir = "lpFirO"
                name_rel_const = "constChanO"
                name_rel_comp0 = "compChan0O"
                name_rel_comp1 = "compChan1O"                
                name_rel_chop = "chopChanO"                
                name_rel_delay = "delayChanO"
                name_rel_outport = "outportChanO"
    
                # save the current location in the flowgraph so we can
                # go back to it after we're done building the current
                # composite actor                
                orig_loc_str = self.ptolemy_location_update(BLOCK, offset)
                orig_loc = self.current_location(BLOCK)
                self.set_location(BLOCK, BLOCK_ORIG)
                
                ############################
                ### Instantiate Blocks   ###
                ############################

                # Instantiate the container composite actor
                node0 = self.write_element(ENT, name, CLASS_COMP_ACT, "None")
                # set location the composite actor
                node1 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, orig_loc_str)
                node0.appendChild(node1)

                #####################################################################
                ## INPUT Port
                #####################################################################
                # create ports for the composite actor
                node1 = self.write_element(PORT, name_inport1, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "input", "None", "None")
                node0.appendChild(node1)
                node1.appendChild(node2)

                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport, "yes", 0)
                node0.appendChild(chan1)

                #####################################################################
                ## DELAY
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_DELAY,
                name_delay, "repeat(sampling_freq*symbol_time, 0)",
                100)
                node0.appendChild(node1)
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_delay, "no", 0)
                node0.appendChild(chan1)
                #######################################################################

                #node1 = self.write_to_ptolemy_file(DIRECT, CLASS_SDF, NAME_SDF, "None", 0)
                #node0.appendChild(node1)

                #####################################################################
                ## MULT
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_MULTDIV, name_mult, "None", 0)
                node0.appendChild(node1)

                [chana, chanb] = self.link_in_ptolemy_file(name_delay+".output", name_mult+".multiply", name_rel_delay)
                node0.appendChild(chana)
                node0.appendChild(chanb)
                #####################################################################
                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_inport, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_inport1, name_mult+".multiply", name_rel_inport)
                node0.appendChild(chana)
                node0.appendChild(chanb)
                [chana, chanb] = self.link_in_ptolemy_file("None", name_delay+".input", name_rel_inport)
                node0.appendChild(chanb)                

                #####################################################################
                ## FIR Filter
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_FIR, name_fir, "rxrc1.dat", 0)
                node0.appendChild(node1)

                #####################################################################                
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_fir, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_mult+".output", name_fir+".input", name_rel_fir)
                node0.appendChild(chana)
                node0.appendChild(chanb)                

                #####################################################################
                ## CHOP
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_CHOP, name_chop, "sampling_freq*symbol_time", 0)
                node0.appendChild(node1)

                #####################################################################
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_chop, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_fir+".output", name_chop+".input", name_rel_chop)
                node0.appendChild(chana)
                node0.appendChild(chanb)                

                #####################################################################
                ## CONST
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_CONST, name_const, "0.2", 100)
                node0.appendChild(node1)

                #####################################################################
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_const, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_const+".output", name_comp+".right", name_rel_const)
                node0.appendChild(chana)
                node0.appendChild(chanb)                

                #####################################################################
                ## COMPARISON
                #####################################################################
                node1 = self.write_to_ptolemy_file(BLOCK, CLASS_COMP, name_comp, "None", 0)
                node0.appendChild(node1)
                #####################################################################
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_comp0, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_chop+".output", name_comp+".left", name_rel_comp0)
                node0.appendChild(chana)
                node0.appendChild(chanb)                


                
                #####################################################################
                ## OUTPUT Port
                #####################################################################
                # create ports for the composite actor

                loc_str = self.ptolemy_location_update(BLOCK, offset)
                node1 = self.write_element(PORT, name_outport, CLASS_NAMED_IO_PORT, "None")
                node2 = self.write_element(PROP, "output", "None",
                "None")
                node3 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)                
                node0.appendChild(node1)
                node1.appendChild(node2)
                node1.appendChild(node3)
                #####################################################################
                chan1 = self.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rel_outport, "no", 0)
                node0.appendChild(chan1)
                [chana, chanb] = self.link_in_ptolemy_file(name_comp+".output", name_outport, name_rel_outport)
                node0.appendChild(chana)
                node0.appendChild(chanb)                                

                self.set_location(BLOCK, orig_loc)

                return node0
                
            else:
               print "ERROR: Found in write_to_ptolemy_file method. Unknown Block Class = ", class_str
               exit(-1)
        
        elif type_str is CH:
            node1 = self.write_element(RELATION, name, class_str,"None")

            # "yes" means we need to add a virtex
            if (value == "yes"):
                loc_str = self.ptolemy_location_gen(0)
                node2 = self.write_element(PROP, "width", CLASS_PARAMETER,"-1")
                node3 = self.write_element(VERTEX, name, "None",loc_str)
                node1.appendChild(node2)
                node1.appendChild(node3)
            return node1
            
        elif type_str is DIRECT:
            node1 = self.write_element(PROP, NAME_SDF, CLASS_SDF, "None")
            loc_str = self.ptolemy_location_update(DIRECT, offset)
            node2 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
            node1.appendChild(node2)
            return node1
        elif type_str is PORT:
            node1 = self.write_element(PORT, name, class_str,
                                       "None")
            loc_str = self.ptolemy_location_update(BLOCK, offset)
            node2 = self.write_element(PROP, NAME_LOCATION,
                                       CLASS_LOCATION, loc_str)
            node3 = self.write_element(PROP, NAME_SHOW_NAME,
                                       CLASS_SING_PARAM, "true")
            node1.appendChild(node2)
            node1.appendChild(node3)
            return node1
        else:
            print "ERROR: Found in write_to_ptolemy method. Parameter passed is incompatible= ",  type_str
            exit(-1)

        return node1
    def link_in_ptolemy_file(self, out_unit, in_unit, name_relation):

        if out_unit != "None":
            node1 = self.doc.createElement(LINK)
            node1.setAttribute("port", out_unit)
            node1.setAttribute(RELATION, name_relation)
        else:
            node1 = "None"
            
        if in_unit != "None":
            node2 = self.doc.createElement(LINK)
            node2.setAttribute("port", in_unit)
            node2.setAttribute(RELATION, name_relation)
        else:
            node2 = "None"



        return [node1, node2]
        

if __name__ == "__main__":
    filename   = "xml-tmp.xml"
    model_name = "xml-tmp"

    pgen = ptolemy_writer(filename, model_name)
    pgen.write_element("property", "_createBy", "ptolemy.kernel.attributes.VersionAttribute", "8.0.1_20101021")

    node1 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, "period_time", "4000", 0)
    node2 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, "carrier_freq", "4.0", 0)
    node3 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, "carrier_phase", "0", 0)
    node4 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, "sampling_freq", "400", 0)
    node5 = pgen.write_to_ptolemy_file(PARAM, CLASS_PARAMETER, "symbol_time", "2", 0)
    pgen.top_element.appendChild(node1)
    pgen.top_element.appendChild(node2)
    pgen.top_element.appendChild(node3)
    pgen.top_element.appendChild(node4)
    pgen.top_element.appendChild(node5)


    name_carrier_scale = "Carrier Scale" 
    name_carrier = "Tx Carrier"
    name_rcv = "My DBPSK Receiver"
    name_seq_plot = "Data In Monitor"
    name_pulse_filt = "Pulse Shaping Filter"
    name_data_in = "Data In"
    name_tx = "My DBPSK Transmitter"

    name_carrier_rel = "carrierCon0"
    name_rcv_rel = "recvconn"
    name_pulse_filt_rel = "pulseFiltO"
    name_carrier_scale_rel = "carrscaleO"
    name_data_in_rel = "datainO"
    name_tx_rel = "dbpskTxCh"

    node1 = pgen.write_to_ptolemy_file(DIRECT, CLASS_SDF, NAME_SDF, "None", 0)
    pgen.top_element.appendChild(node1)

    #####################################################################
    ## Carrier
    #####################################################################
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_SINE, name_carrier, "None", 0)
    pgen.top_element.appendChild(node1)

    #####################################################################
    ## Data 
    #####################################################################
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_CONST, name_data_in, "0.2", 100)
    pgen.top_element.appendChild(node1)
    #####################################################################
    ## Scale
    #####################################################################
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_SCALE, name_carrier_scale, "None", 0)
    pgen.top_element.appendChild(node1)
    
    #####################################################################
    ## DBPSK Tx
    #####################################################################
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_DBPSK_TX, name_tx, "None", 0)
    pgen.top_element.appendChild(node1)

    #####################################################################
    ## Pulse Shaping Filter
    #####################################################################
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_FIR, name_pulse_filt, "rxrc1.dat", 0)
    pgen.top_element.appendChild(node1)

    #####################################################################                
    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_pulse_filt_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    
    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_DBPSK_RX, name_rcv, "None", 0)
    pgen.top_element.appendChild(node1)    

    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_SEQ_PLOT, name_seq_plot, "None", 0)
    pgen.top_element.appendChild(node1)    

    ############################################
    ## Block Connections

    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_carrier_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_carrier+".output", name_carrier_scale+".input", name_carrier_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)

    ############################
    # TX connections
    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_carrier_scale_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_carrier_scale+".output", name_tx+".carrier", name_carrier_scale_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)
    
    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_data_in_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_data_in+".output", name_tx+".datain", name_data_in_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)

    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_tx_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_tx+".output", name_pulse_filt+".input", name_tx_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)                    
    ############################
    
    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_pulse_filt_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_pulse_filt+".output", name_rcv+".rfsig", name_pulse_filt_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)                

    
    chan1 = pgen.write_to_ptolemy_file(CH, CLASS_NAMED_IO_RELATION, name_rcv_rel, "no", 0)
    pgen.top_element.appendChild(chan1)
    [chana, chanb] = pgen.link_in_ptolemy_file(name_rcv+".output", name_seq_plot+".input", name_rcv_rel)
    pgen.top_element.appendChild(chana)
    pgen.top_element.appendChild(chanb)                

    pgen.write_to_xmlfile()
    #pgen.print_xmlfile()
