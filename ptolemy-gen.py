#!/usr/bin/env python

import sys, string, types, os
import getopt
import numpy as np
from xml.dom.minidom import parse, parseString, Document, getDOMImplementation
from ptolemy_param import *

XML_HEADER1 = "<?xml version=\"1.0\" standalone=\"no\"?>"
XML_HEADER2 = """<!DOCTYPE entity PUBLIC \"-//UC Berkeley//DTD MoML 1//EN\"
\"http://ptolemy.eecs.berkley.edu/xml/dtd/MoML_1.dtd\">
"""
PARAM_COLOR = [0.0, 0.0, 1.0, 1.0]
VERG_ORIG   = [1,1]

#XML_INIT = "entity "
class ptolemy_writer:
    def __init__(self, outfile_name, model_name):
        self.outfile = file(outfile_name, 'w')
        self.outfile.flush()
        self.model_name = model_name
        self.outfile_name = outfile_name

        self.impl = getDOMImplementation('')
        self.doc = self.impl.createDocument(None, 'entity', None)
        self.top_element = self.doc.documentElement
        

    def __del__(self):
        self.outfile.close()
        
    def write_element(self, tag_str, name_str, class_str, value_str):
        #wml = self.doc.createElement('card')
        #self.top_element.appendChild(wml)

        node = self.doc.createElement(tag_str)

        node.setAttribute("name", name_str)        
        node.setAttribute("class", class_str)
        if (value_str != "None"):
            node.setAttribute("value", value_str)        

        #self.top_element.appendChild(maincard)
        return node

    def write_to_xmlfile(self):
        outfile_temp = file('tmp_xml_read.xml', 'w')
        outfile_temp.write(self.doc.toprettyxml())
        outfile_temp.close()

        infile_temp = file ('tmp_xml_read.xml', 'r')

        line = infile_temp.readline()
        self.outfile.write(XML_HEADER1)
        self.outfile.write("\n")
        self.outfile.write(XML_HEADER2)

        line = infile_temp.readline()
        mod_model_name = "<entity name=\""+self.model_name+"\" class=\"ptolemy.actor.TypedCompositeActor\">\n"
        self.outfile.write(mod_model_name)
        
        line = infile_temp.readline()
        while line:
            self.outfile.write(line)
            line = infile_temp.readline()
        
        outfile_temp.close()
        infile_temp.close()
        
    def print_xmlfile(self):
        self.outfile.close()
        infile_temp = file(self.outfile_name, 'r')

        print "XML File="
        line = infile_temp.readline()
        while line:
            sys.stdout.write(line)
            line = infile_temp.readline()
        infile_temp.close()
        
if __name__ == "__main__":
    filename   = "xml-tmp.xml"
    model_name = "xml-tmp"

    pgen = ptolemy_writer(filename, model_name)
    #pgen.write_element("property", "_createBy", "ptolemy.kernel.attributes.VersionAttribute", "8.0.1_20101021")
    node1 = pgen.write_element(PROP, "period_time", CLASS_PARAMETER, "400")
    node2 = pgen.write_element(PROP, NAME_ICON, CLASS_ICON, NONE)
    node3 = pgen.write_element(PROP, NAME_COLOR, CLASS_COLOR, VAL_COLOR_PARAMETER)
    node4 = pgen.write_element(PROP, NAME_LOCATION, CLASS_LOCATION, "{1, 1}")

    pgen.top_element.appendChild(node1)
    node1.appendChild(node2)
    node2.appendChild(node3)
    node1.appendChild(node4)    

    pgen.write_to_xmlfile()
    pgen.print_xmlfile()
