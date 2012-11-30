#!/usr/bin/env python

import sys, string, types, os
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
        
        self.param_loc = PARAM_ORIG
        self.block_loc = BLOCK_ORIG

    def __del__(self):
        self.outfile.close()
        
    def write_element(self, tag_str, name_str, class_str, value_str):

        node = self.doc.createElement(tag_str)

        node.setAttribute("name", name_str)        
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
        return loc_str

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

            else:
               exit("ERROR: Found in write_to_ptolemy method. Unknown Block Class\n")
                
        elif type_str is DIRECT:
            node1 = self.write_element(PROP, NAME_SDF, CLASS_SDF, "None")
            loc_str = self.ptolemy_location_update(DIRECT, offset)
            node2 = self.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)
            node1.appendChild(node2)
        else:
            exit("ERROR: Found in write_to_ptolemy method. Parameter passed is incompatible\n")

        return node1
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

    node1 = pgen.write_to_ptolemy_file(DIRECT, CLASS_SDF, NAME_SDF, "None", 0)
    pgen.top_element.appendChild(node1)

    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_MULTDIV, NAME_MULTDIV, "None", 0)
    pgen.top_element.appendChild(node1)

    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_DELAY, NAME_DELAY, "repeat(sampling_freq*symbol_time, 0)", 100)
    pgen.top_element.appendChild(node1)

    node1 = pgen.write_to_ptolemy_file(BLOCK, CLASS_FIR, NAME_LOWPASS, "rxrc1.dat", 0)
    pgen.top_element.appendChild(node1)
    
    pgen.write_to_xmlfile()
    pgen.print_xmlfile()
