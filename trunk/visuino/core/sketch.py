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
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from pprint import pprint
import yaml

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from visuino.gx.blocks import *

__all__ = ['SketchBlocks']

SKETCH_YAML_EXAMPLE = \
"""
snippets:
    1:
        pos: [400, 200]
        body:
            - command: "function_call"
              name: "digitalWrite"
              library: "Arduino.h"
              args:
                  - command: "function_call"
                    name: "analogRead"
                    library: "Arduino.h"
                    args:
                  - command: "function_call"
                    name: "digitalRead"
                    library: "Arduino.h"
                    args:
                        - command: "function_call"
                          name: "digitalRead"
                          library: "Arduino.h"
                          args: null
              
            - command: "function_call"
              name: "delay"
              library: "Arduino.h"
              args: null              
"""

class SketchBlocks(object):
    def __init__(self, libs):
        ''' (LibraryDefinitions)
        '''
        self._libs = libs        
        self._snippet_id_count = 2
        
        self._root = yaml.load(SKETCH_YAML_EXAMPLE)        

#        self._root = {'snippets': {1: {'pos': [400, 200], 'body': [
#            {'command': 'function_call', 'name': 'digitalWrite', 
#             'library': 'Arduino.h', 'args': {}},
#            {'command': 'function_call', 'name': 'analogWrite',
#             'library': 'Arduino.h', 'args': {}},
#            {'command': 'function_call', 'name': 'digitalWrite'}
#            ]}}}
        
    def addSnippet(self, pos):
        ''' (QPointF)
        '''
        new_snippet = {'pos': [pos.x(), pos.y()], 'body': []}
        self._root['snippets'][self._snippet_id_count] = new_snippet
        self._snippet_id_count += 1
        return new_snippet
        
            
    def drawSnippet(self, s_id, scene, palette=None):
        ''' (int, QGraphicsScene) -> NoneType
        '''
        if not s_id in self._root['snippets']: 
            return
            
        s_pos = self._root['snippets'][s_id]['pos']        
        parent_vf = None
        
        for element in self._root['snippets'][s_id]['body']:
            
            new_block = self._createCommandBlock(element, scene, palette)             
            
            if parent_vf is None:
                new_block.setPos(s_pos[0], s_pos[1])
            else:
                new_block.plugVfFemale(parent_vf)
            
            parent_vf = new_block
            
            
    def _createCommandBlock(self, e, scene, palette):
        ''' (dict)    
        '''
        if e['command'] == 'function_call':
            print('Creating function call %s...' % e['name'])
            
            new_block = GxBlockFunctionCall(
                self._libs[e['library']]['functions'][e['name']], scene)
            
            if e['args']:
                for i, arg_command in enumerate(e['args']):
                    if arg_command is not None:                        
                        arg_block = self._createCommandBlock(arg_command, 
                                                             scene, palette)
                        self._setBlockProperties(arg_block, palette)
                        arg_block.plugIo(new_block.args_labels[i])
                
            self._setBlockProperties(new_block, palette)
            return new_block
            
        
    def _setBlockProperties(self, block, palette):
        block.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        block.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        block.palette_blocks = palette
        block.setCursor(Qt.OpenHandCursor)        
        
        
if __name__ == '__main__':
    sketch = SketchBlocks(None)
    pprint(sketch._root)
    
