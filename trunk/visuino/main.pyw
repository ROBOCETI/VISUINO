#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements Function Call Blocks with full customization and
#              input/output connections.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------

__all__ = ['execute']

import visuino
import sys

def execute():
    app = visuino.gui.AppVisuino(sys.argv)
    app.execute()

if __name__ == '__main__':
    execute()