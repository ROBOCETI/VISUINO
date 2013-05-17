#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function    
from pprint import pprint
from collections import OrderedDict
 
import yaml

__all__ = ['LibraryDefinitions']
    
DEFAULT_YAML_LIBS = \
"""
Arduino.h:
    functions:
        - name: "digitalWrite"
          palette_section: "Digital I/O"
          return_type: "" 
          args:
              - name: "pin"
                type: "int"
                restriction: "1|13"
              - name: "value"
                type: "const"
                restriction: "HIGH,LOW"
                
        - name: "digitalRead"
          palette_section: "Digital I/O"
          return_type: "int"
          args:
              - name: "pin"
                type: "int"
                restriction: "1|13"        
                
        - name: "analogRead"
          palette_section: "Analog I/O"
          return_type: None
          args:
              - name: "pin"
                type: "int"
                restriction: "1|13"
                
        - name: "analogWrite"
          palette_section: "Analog I/O"
          return_type: ""
          args:
              - name: "pin"
                type: "int"
                restriction: "1|13"
              - name: "value"
                type: "int"
                restriction: "0|255"
                
        - name: "delay"
          palette_section: "Time"
          return_type: ""
          args:
              - name: "milliseconds"
                type: "int"
                restriction: "0|"
                
        - name: "millis"
          palette_section: "Time"
          return_type: "int"
          args: null
"""

class LibraryDefinitions(dict):
    def __init__(self):
        dict.__init__(self)
        self.parseYAML()

    def parseYAML(self):
        
        self._root = yaml.load(DEFAULT_YAML_LIBS)
        
        for lib_name, lib_dict in self._root.items():            
            functions, sections = {}, OrderedDict()

            if 'functions' in lib_dict:
                
                for defn in lib_dict['functions']:
                    
                    defn['library'] = lib_name
                    
#                    print('parsing function %s (%s)...' % (defn['name'], 
#                          defn['palette_section']))
                    
                    functions[defn['name']] = defn
                    
                    if 'palette_section' in defn:
                        sec = defn['palette_section']
                        if sec not in sections:
                            sections[sec] = []                            
                        sections[sec].append(defn)                                        
                    
            self[lib_name] = {'functions': functions, 
                              'palette_sections': sections}
        
if __name__ == '__main__':
    libs = LibraryDefinitions()
    print('-'*70)
    print("  Sections in 'Arduino.h':")
    print('-'*70)    
    pprint(libs['Arduino.h']['palette_sections'])
    print('-'*70)
    print("  Functions in 'Arduino.h':")
    print('-'*70)
    pprint(libs['Arduino.h']['functions'])