#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Used to build an windows executable for the project, by using
#              cx_Freeze (http://cx-freeze.sourceforge.net/).
#              Just run the following on the command line:
#
#              > python setup.py build
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------

from cx_Freeze import setup, Executable

includes = ['sip', 're', 'PyQt4.QtCore', 'PyQt4.QtGui']

exe = Executable(
    script='visuino/main.py',
    base='Win32GUI',
	compress=True,
	targetName='Visuino.exe',
	icon='visuino/resources/python_arduino.ico'
)

setup(
    options = {'build_exe': {'includes': includes}},
    executables = [exe]
)
