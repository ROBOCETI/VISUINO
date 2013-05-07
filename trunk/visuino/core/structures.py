#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Provides all the block connection mechanism through the class
#              GxPluggableBlock.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free. Also, remember to keep the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function     

class Sketch(object):
    def __init__(self):
        self.global_variables = {'int'}
        self.functions = {
            'setup': ['function_call']}

