#!/usr/bin/env python

import sys, string, types, os
import getopt
import numpy as np
from xml.dom.minidom import parse, parseString, Document, getDOMImplementation

XML_HEADER1 = "<?xml version=\"1.0\" standalone=\"no\"?>"
XML_HEADER2 = """<!DOCTYPE entity PUBLIC \"-//UC Berkeley//DTD MoML 1//EN\"
\"http://ptolemy.eecs.berkley.edu/xml/dtd/MoML_1.dtd\">
"""

#XML_INIT = "entity "
class ptolemy_writer:
    def __init__(self, outfile_name, model_name):
        self.outfile = file(outfile_name, 'w')
        self.outfile.flush()
        self.model_name = model_name

        self.impl = getDOMImplementation('')
        #self.doctype  = self.impl.createDocumentType('entity', "-//UC Berkeley//DTD MoML 1//EN", "http://ptolemy.eecs.berkeley.edu/xml/dtd/MoML_1.dtd")
        #mod_model_name = "entity name=\""+model_name+"\" class=\"ptolemy.actor.TypedCompositeActor\""
        #self.doc = self.impl.createDocument(None, mod_model_name,
        #self.doctype)
        self.doc = self.impl.createDocument(None, 'entity', None)
        
        self.top_element = self.doc.documentElement
        

    def __del__(self):
        self.outfile.close()
        
    def write_element(self):
        #wml = self.doc.createElement('card')
        #self.top_element.appendChild(wml)

        maincard = self.doc.createElement("property")
        maincard.setAttribute("name", "_createby")
        maincard.setAttribute("class", "ptolemy.kernel.attributes.VersionAttribute")
        maincard.setAttribute("value", "8.0.1_20101021")
        self.top_element.appendChild(maincard)

        #w2 = self.doc.createElement("what")
        #w2.setAttribute("here", "2")
        #self.top_element.appendChild(w2)
        


    def write_to_xmlfile(self):
        outfile_temp = file('tmp_xml_read.xml', 'w')
        outfile_temp.write(self.doc.toprettyxml())
        outfile_temp.close()

        #outfile_fix = file('tmp_xml_fix.xml', 'w')
        infile_temp = file ('tmp_xml_read.xml', 'r')

        line = infile_temp.readline()
        print "line= ", line
        self.outfile.write(XML_HEADER1)
        #line = infile_temp.readline()
        print "line= ", line
        self.outfile.write("\n")
        self.outfile.write(XML_HEADER2)

        line = infile_temp.readline()
        mod_model_name = "<entity name=\""+self.model_name+"\" class=\"ptolemy.actor.TypedCompositeActor\">\n"
        self.outfile.write(mod_model_name)
        print "line= ", line
        
        line = infile_temp.readline()
        while line:
            self.outfile.write(line)
            line = infile_temp.readline()
        
        #print "LINE = ", line
        #self.outfile.write(self.doc.toprettyxml())

        outfile_temp.close()
        #outfile_fix.close()
        infile_temp.close()
        
    def print_xmlfile(self):
        print "XML File="
        print self.doc.toprettyxml()

if __name__ == "__main__":
    filename   = "xml-tmp.xml"
    model_name = "Test Receiver"

    pgen = ptolemy_writer(filename, model_name)
    pgen.write_element()
    pgen.print_xmlfile()
    pgen.write_to_xmlfile()



    #top_element.unlink()        
