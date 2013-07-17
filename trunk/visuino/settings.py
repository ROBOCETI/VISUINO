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
import yaml

from PyQt4.QtGui import *
from PyQt4.QtCore import *

# VISUINO GLOBAL SETTINGS
VGS = {}

DEFAULT_SETTINGS = \
"""
styles:
    
    notch:
        insertion_marker_color: '#111111'
        insertion_marker_width: 10

        io_shape: 'arc'
        io_basis: 0.0
        io_size:
            width: 10
            height: 20

        vf_shape: 'trig'
        vf_basis: 0.85
        vf_x0: 20
        vf_size:
            width: 40
            height: 5            

    block_function_call:

        background_color: '#0055d4'
        border_color: '#003380'
        border_width: 2
        corner_shape: 'arc'
        corner_size:
            width: 6
            height: 6

        name_font_color: 'white'
        name_font_family: 'Verdana'
        name_font_size: 11
        name_padding:
            horizontal: 8
            vertical: 5
        name_vcorrection: -1

        arg_min_left_padd: 40
        arg_spacing: 0
        bottom_padd: 5

    block_arg_label:

        background_color: 'yellow'
        border_color: '#333333'
        border_width: 2
        corner_shape: 'arc'
        corner_size:
            width: 10
            height: 10

        font_color: 'black'
        font_family: 'Verdana'
        font_size: 10
        font_vcorrection: -1

        padding:
            horizontal: 10
            vertical: 5

    block_expression:

        background_color: 'green'
        field_color: 'lightgreen'
        field_padd: 10
        border_width: 2
        border_color: 'black'

        item_spacing: 5
        padding:
            horizontal: 10
            vertical: 10

    block_start_end:
        
        border_width: 2
        corner_shape: 'arc'
        corner_size:
            width: 6
            height: 6
            
        background_color: '#808080'
        font:
            color: 'white'
            outline_color: 'black'
            family: 'Verdana'
            size: 10
            vcorrection: -1
            bold: True
            italic: False
            
        label_padding:
            horizontal: 50
            vertical: 10
            
        start_label_text: 'Início'
        end_label_text: 'Fim'
"""

class StyleBlocks(dict):
    def __init__(self, style_dict):
        dict.__init__(self, style_dict)
    
    def getFont(self):
        if 'font' not in self: return None
        
        font = QFont(self['font']['family'], self['font']['size'])
        font.setBold(self['font']['bold'])
        font.setItalic(self['font']['italic'])
        
        return font
        
    def getCornerSize(self):
        return (self['corner_size']['width'], self['corner_size']['height'])    
        

class VisuinoGlobalSettings(dict):
    def __init__(self, start_dict={}):
        dict.__init__(self, start_dict)
        
    def getBlockStyle(self, block_name):
        if block_name not in self['styles']:
            raise KeyError("'%s' is not a valid block!" % block_name)
            
        sty = StyleBlocks(self['styles'][block_name])


def load_default():
    global VGS, DEFAULT_SETTINGS
    VGS = VisuinoGlobalSettings(yaml.safe_load(DEFAULT_SETTINGS))


def load_config_file(filename):
    global VGS
    stream = open(filename, 'r')
    VGS = yaml.load(stream)
    stream.close()

def save_config_file(filename):
    global VGS
    stream = open(filename, 'w')
    yaml.dump(VGS, stream)
    stream.close()
