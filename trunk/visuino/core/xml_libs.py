#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements a palette for blocks drag and drop.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['Libraries', 'LibraryDefinitions']

from collections import OrderedDict
import xml.etree.ElementTree as ET

from visuino.core.definitions import *
                
class LibraryDefinitions(dict):
    def __init__(self, library_element):
        ''' (str)
        '''
        dict.__init__(self)
        self.name = library_element.attrib['name']
        self.sections = OrderedDict()
        
        for x in library_element:
#            print("Parsing '%s' ..." % x.tag)
            self.parseFunctionDefinition(x)
            

    def parseFunctionDefinition(self, element):
        if element.tag == 'function':
            atb = element.attrib
            
            for required_attr in ('name', 'return_type', 'section'):
                if not required_attr in atb:
                    raise XmlMissingAttributeError(element, required_attr)
            
            name, section = atb['name'], atb['section']
            new_func = FunctionDefinition(name, atb['return_type'],
                section, self.parseArguments(element))
                
            if not section in self.sections:
                self.sections[section] = []
                
            self.sections[section].append(new_func)
            self[name] = new_func
                
        else:
            raise XmlInvalidTagError(element, expecting='function')
            
    def parseArguments(self, element):
        result = []
        for x in element:
#            print("Parsing '%s'..." % x.tag)
            
            if x.tag == 'arg':                
                atb = x.attrib
                
                for required_attr in ('name', 'type'):
                    if required_attr not in atb:
                        raise XmlMissingAttributeError(x, required_attr)
                
                restriction = None
                if 'restriction' in atb:
                    restriction = atb['restriction']
                
                type_arg = atb['type'] if len(atb['type']) else None                    
                result.append(ArgInfo(atb['name'], type_arg, restriction))            
            else:
                raise XmlInvalidTagError(x, expecting='arg')
            
        return result
            

class Libraries(OrderedDict):
    def __init__(self, xml_data):
        ''' (str)
        '''
        OrderedDict.__init__(self)
        
        root = ET.fromstring(xml_data)
                    
        for element in root:  
#            print("Parsing '%s' ..." % element.tag)
            
            if element.tag == 'library':
                if 'name' in element.attrib:                    
                    self[element.attrib['name']] = LibraryDefinitions(element)                                          
                else:
                    raise XmlMissingAttributeError(element, 'name')
            else:
                raise XmlInvalidTagError(element, expecting='library')          
            

class XmlInvalidTagError(Exception):
    def __init__(self, element, expecting=None):
        ''' (xml.etree.ElementTree.Element, str)
        '''
        self.message = "Invalid element tag: '%s'." % element.tag
        if expecting:
            self.message += " Was expecting '%s'." % expecting
            
    def __str__(self):
        return self.message     
           

class XmlMissingAttributeError(Exception):
    def __init__(self, element, attribute):
        ''' (xml.etree.ElementTree.Element, str)
        '''
        self.message = ("Mandatory attribute '%s' was not found on "
            "this '%s' element.") % (attribute, element.tag)
            
    def __str__(self):
        return self.message 
        

XML_START = \
"""<?xml version="1.0" encoding="UTF-8"?>
<Libraries>
    <library name="Arduino.h"/>
</Libraries>
"""

XML_LIBRARIES = \
"""<?xml version="1.0" encoding="UTF-8"?>
<Libraries>
	<library name="Arduino.h">
		<function name="digitalWrite" return_type="None" section="I/O">
			<arg name="pin" type="int" restriction="[1,13]"/>
			<arg name="value" type="int" restriction="HIGH,LOW"/>
		</function>
		<function name="digitalRead" return_type="int" section="I/O">
			<arg name="pin" type="int" restriction="[1,13]"/>
		</function>		
		<function name="pinMode" return_type="None" section="I/O">
			<arg name="pin" type="int" restriction="[0,)"/>
			<arg name="mode" type="int" restriction="INPUT,OUTPUT"/>
		</function>
		<function name="delay" return_type="None" section="Time">
			<arg name="milliseconds" type="int" restriction="[0,)"/>
		</function>
	</library>
</Libraries>
"""
        

if __name__ == '__main__':
    lbs = Libraries(XML_LIBRARIES)
    print(lbs['Arduino.h']['digitalWrite'])
    print('-'*30)
    print(lbs['Arduino.h'].sections['I/O'])