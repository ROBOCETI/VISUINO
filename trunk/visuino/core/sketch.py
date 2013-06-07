#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
"""
The main purpose of the Visuino programming tool is to generate C/C++ Arduino 
code. That is, a *sketch* (".pde" file) so to speak. Although the Arduino 
subset of the C language allows definition of classes and methods, the initial 
goal is to provide at least all the basic elements for the C procedural 
programming style.

This module provides the ``SketchBlocks`` class, which keep track of all the
syntax elements on the sketch. 
 
   
              setup
        _______|__ ___
       /          \
      fc1
     /   \
    ex1  ex2

Here is a basic structure of a Arduino sketch::
    
    int my_var = 13;   // variable declaration
    
    void setup()       // mandatory function (runs only once when connecting)
    {
        someFunction(led_pin, OUTPUT);   // function call
    }
    
    void loop()       // mandatory function (runs forever while there is power)
    {
        if (condition)
        {
            // if "true" branch
        }
        else
        {
            // if "false" branch
        }
        
        while
    }
    

Each graphical block on the Visuino interface provides elements of the syntax
    
There always gonna be these two functions: ``setup()``, which runs just once
when the board is turned on; and ``loop()`` which keeps running forever while
the board is on. Even on the simplistic blink example above we already 
"""

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
                        - null
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
              args:
                  - null
                 
            - command: "function_call"
              name: "digitalWrite"
              library: "Arduino.h"
              args:
                  - null
                  - null
"""

class SketchBlocks(object):
    ''' 
    This class holds the sketch dictionary 
    '''
    def __init__(self, libs):
        '''
        :param libs: ``visuino.core.LibraryDefinitions``.
            Required to recovery things like function definitions to construct
            function calls.
        '''
        self._libs = libs        
        self._snippet_id_count = 1       
        self._root = {'snippets': {}}
        
#        self._root = yaml.load(SKETCH_YAML_EXAMPLE)        

#        self._root = {'snippets': {1: {'pos': [400, 200], 'body': [
#            {'command': 'function_call', 'name': 'digitalWrite', 
#             'library': 'Arduino.h', 'args': {}},
#            {'command': 'function_call', 'name': 'analogWrite',
#             'library': 'Arduino.h', 'args': {}},
#            {'command': 'function_call', 'name': 'digitalWrite'}
#            ]}}}

    def loadSketch(self, filename):
        '''
        :param filename: ``str``.
            Load a sketch from some filename
        '''
        stream = open(filename, 'r')
        self._root = yaml.load(stream)
#        print('#'*40)
#        print('The following content was loaded:')
#        print('-'*40)
#        pprint(yaml.dump(self._root), indent=4)
#        print('#'*40)        
        stream.close()
        
    def dumpSketch(self, filename):
        stream = open(filename, 'w')
        yaml.dump(self._root, stream, indent=4)
#        print('#'*40)
#        print('The following content was saved:')
#        print('-'*40)
#        pprint(yaml.dump(self._root), indent=4)
#        print('#'*40)
        stream.close()
        
    def addSnippet(self, first_block):
        ''' (GxPluggableBlock) -> int
        '''
        new_id = self._snippet_id_count
        first_block.snippet_id = new_id
        new_snippet = {'pos': [first_block.pos().x(), first_block.pos().y()], 
                       'body': []}
        self._root['snippets'][new_id] = new_snippet
        self._snippet_id_count += 1
        self.updateSnippet(first_block)
        
#        print('Created new snippet!')
        return new_id 
        
    def drawSnippets(self, scene, palette):
        for snippet_id in self._root['snippets'].keys():
#            print('Drawing snippet %d...' % snippet_id)
            self.drawSnippet(snippet_id, scene, palette)
            
    def drawSnippet(self, snippet_id, scene, palette=None):
        ''' (int, QGraphicsScene, GxPalette)
        '''
        if not snippet_id in self._root['snippets']: 
            return
        snippet = self._root['snippets'][snippet_id]
                
        parent_vf = None
        
        for element in snippet['body']:
            
            new_block = self._drawElementBlock(element, scene, palette)             
            
            if parent_vf is None:
                new_block.setPos(snippet['pos'][0], snippet['pos'][1])
                new_block.sketch = self
                new_block.snippet_id = snippet_id
            else:
                new_block.plugVfFemale(parent_vf, update_snippet=False)
            
            parent_vf = new_block

    def updateSnippet(self, first_block):
        ''' (GxPluggableBlock)
        '''
        s_id = first_block.snippet_id
        if not s_id or s_id not in self._root['snippets']:
            return

        snippet = self._root['snippets'][s_id]        
        snippet['body'] = [first_block.element]
        child_vf = first_block.child_vf
        
        while child_vf:
            snippet['body'].append(child_vf.element)
            child_vf = child_vf.child_vf
            
#        print('Updated snippet %d!' % s_id)

    def updateSnippetPos(self, snippet_id, pos):
        ''' (int, QPointF)
        '''
        if snippet_id in self._root['snippets']:
            self._root['snippets'][snippet_id]['pos'] = \
                [pos.x(), pos.y()]
                
    def removeSnippet(self, snippet_id, update_id_count=True):
        ''' (int, bool)
        '''
        del self._root['snippets'][snippet_id]
        if update_id_count:
            if len(self._root['snippets'].keys()) == 0:
                self._snippet_id_count = 1
            else:
                self._snippet_id_count = max(self._root['snippets'].keys()) + 1
            
    def getSnippetCodeString(self, snippet_id):
        ''' (int)
        '''
        if not snippet_id in self._root['snippets']: 
            return
        snippet = self._root['snippets'][snippet_id]
        
        result = ''
        for command in snippet['body']:
            result += self._getElementCodeString(command) + ';\n'
            
        return result[:-1]
        
    def _getElementCodeString(self, element):
        ''' (dict)
        '''
        if element['command'] == 'function_call':
        
            result = element['name'] + '('
            
            if element['args'] is not None:
                for arg in element['args']:
                    if arg:
                        result += self._getElementCodeString(arg)
                    result += ', '
                if len(element['args']) > 0:
                    result = result[:-2]
                    
            return result + ')'
            
        return ''
                
    def _drawElementBlock(self, element, scene, palette):
        ''' (dict, GxSceneBlocks, GxPalette)    
        '''
        e = element
        if e['command'] == 'function_call':
#            print('Creating function call %s...' % e['name'])
            
            new_block = GxBlockFunctionCall(
                self._libs[e['library']]['functions'][e['name']], scene)
            
            if e['args']:
                for i, arg in enumerate(e['args']):
                    if arg is not None:                        
                        arg_block = self._drawElementBlock(arg, scene, palette)
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
    
