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
PARAM_ORIG  = [1,1]
PARAM_STEP  = 5

BLOCK_ORIG  = [10, 1]
BLOCK_STEP  = 15 

X_AXIS = 0
Y_AXIS = 1

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

        #self.top_element.appendChild(maincard)
        return node

    def write_to_xmlfile(self):
        
        ser = self.impl.createLSSerializer()
        ser.domConfig.setParameter('format-pretty-print', True)
        ser.writeToURI(self.doc, 'tmp_xml_read.xml')
        
        #outfile_temp = file('tmp_xml_read.xml', 'w')
        #outfile_temp.write(self.doc.toprettyxml())
        #outfile_temp.close()

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

    def write_parameter(self, name, value):
        node1 = pgen.write_element(PROP, "period_time", CLASS_PARAMETER, "400")
        node2 = pgen.write_element(PROP, NAME_ICON, CLASS_ICON, NONE)
        node3 = pgen.write_element(PROP, NAME_COLOR, CLASS_COLOR, VAL_COLOR_PARAMETER)

        self.param_loc[Y_AXIS] = self.param_loc[Y_AXIS] + PARAM_STEP
        loc_str = "{" + str(self.param_loc[X_AXIS]) + ", " + str(self.param_loc[Y_AXIS]) + "}"
        node4 = pgen.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, loc_str)

        node1.appendChild(node2)
        node2.appendChild(node3)
        node1.appendChild(node4)

        return node1
if __name__ == "__main__":
    filename   = "xml-tmp.xml"
    model_name = "xml-tmp"

    pgen = ptolemy_writer(filename, model_name)
    pgen.write_element("property", "_createBy", "ptolemy.kernel.attributes.VersionAttribute", "8.0.1_20101021")

    node = pgen.write_parameter("period_time", "400")

    pgen.top_element.appendChild(node)

    pgen.write_to_xmlfile()
    pgen.print_xmlfile()
