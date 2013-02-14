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

        init_node0 = self.write_to_gnuradio_file(BLOCK_GNU, CLASS_OPTIONS, NONE, ["4096, 4096"], "None")
        self.top_element.appendChild(init_node0)        
        
        self.param_loc = copy.deepcopy(PARAM_ORIG)
        self.block_loc = copy.deepcopy(BLOCK_ORIG)

    def __del__(self):
        self.outfile.close()
        
    def write_element(self, tag_str, name_str, class_str, value_str):
        node  = self.doc.createElement(tag_str)
        if name_str != NONE:
            node2 = self.doc.createTextNode(name_str)
            node.appendChild(node2)
        #if (name_str != "None"):        
        #    node.setAttribute("name", name_str)
        #if (class_str != "None"):        
        #    node.setAttribute("class", class_str)
        #if (value_str != "None"):
        #    node.setAttribute("value", value_str)        

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
            print "gnuradio loc_str= ", loc_str
        elif req_type is BLOCK_GNU:
            self.block_loc[X_AXIS] = self.block_loc[X_AXIS] + BLOCK_STEP
            y_axis_temp = self.block_loc[Y_AXIS] + offset
            loc_str = "(" + str(self.block_loc[X_AXIS]) + ", " + str(y_axis_temp) + ")"
        elif req_type is DIRECT_GNU:
            loc_str = "(" + str(DIRECT_LOC[X_AXIS]) + ", " + str(DIRECT_LOC[Y_AXIS]) + ")"
        else:
            exit("ERROR: Found in ptolemy_location_update method. Parameter passed is incompatible\n")
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
    def ptolemy_location_gen(self, offset):

        x_axis_temp = self.block_loc[X_AXIS] + BLOCK_STEP/2
        y_axis_temp = self.block_loc[Y_AXIS] + offset
        loc_str = "{" + str(x_axis_temp) + ", " + str(y_axis_temp) + "}"
       
        return copy.deepcopy(loc_str)
    #def write_element(self, tag_str, name_str, class_str, value_str):
    def write_to_gnuradio_file(self, type_str, class_str, name, value, offset):
        if type_str is PARAM_GNU:
                node1 = self.write_element(BLOCK_GNU, NONE, NONE, NONE)
                node2 = self.write_element(KEY_GNU,   class_str, NONE, NONE)
                node1.appendChild(node2)

                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "id", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, name, NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "_enabled", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "true", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "value", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, value[0], NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)

                loc_str = self.gnuradio_location_update(PARAM_GNU, 0)
                
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "_coordinate", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, loc_str, NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)                
        elif type_str is BLOCK_GNU:
            if class_str is CLASS_OPTIONS:
                node1 = self.write_element(BLOCK_GNU, NONE, NONE, NONE)
                node2 = self.write_element(KEY_GNU,   class_str, NONE, NONE)
                node1.appendChild(node2)

                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "id", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "top_block", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "_enabled", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "True", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "title", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "author", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "description", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)                
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "window_size", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, value[0], NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "generate_options", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "wx_gui", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "category", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "Custom", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "run_options", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "prompt", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "run", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "True", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "max_nouts", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "0", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "realtime_scheduling", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "_coordinate", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "(10, 10)", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)
                node2 = self.write_element(PARAM_GNU, NONE, NONE, NONE)                
                node3 = self.write_element(KEY_GNU,   "_rotation", NONE, NONE)
                node4 = self.write_element(VALUE_GNU, "0", NONE, NONE)                
                node1.appendChild(node2)
                node2.appendChild(node3)
                node2.appendChild(node4)                
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
    def link_in_gnuradio_file(self, out_unit, in_unit, name_relation):
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

def test_gnuradio():
    print "Hello!"
    filename   = "xml-tmp.grc"
    model_name = "xml-tmp"
    pgen = gnuradio_writer(filename, model_name)

    pgen.write_to_xmlfile()

