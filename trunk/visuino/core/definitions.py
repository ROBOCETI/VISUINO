#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Definitions
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['FunctionDefinition', 'ArgInfo']

class ArgInfo(object):
    def __init__(self, name, type_, restriction=None):
        ''' (str, str, str)
        '''
        self.name = name
        self.type = type_
        self.restriction = restriction
        
    def __repr__(self):
        return "ArgInfo('%s', '%s', '%s')" % \
            (self.name, self.type, self.restriction)
        
        
class FunctionDefinition(object):
    def __init__(self, name, return_type, section, args):
        ''' (str, str, list of ArfInfo)
        '''
        self.name = name
        self.return_type = return_type
        self.section = section
        self.args = args
        
    def __repr__(self):
        return ("\nFunctionDefinition(\n"
                    "   name='%s',\n"
                    "   return_type='%s',\n"
                    "   args=[%s]\n)") % (self.name, self.return_type,
                                          self._getArgsRepr())
    
    def _getArgsRepr(self):
        result = ''
        for x in self.args:
            result += "ArgInfo('%s', '%s', %s')\n\t" % (x.name, x.type, 
                                                        x.restriction)
        return result.strip()