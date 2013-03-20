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
__all__ = ['MainWindow', 'AppVisuino']

from PyQt4 import QtGui, QtCore
import sys

from visuino.gx.palette import *
from visuino.gx.blocks import *


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.initUI()

    def initUI(self):

        # --- Blocks Area ------------------------------------------------

        self.wg_blocks_view = QtGui.QWidget(self)
        self.wg_blocks_view = GxPaletteView(parent=self)

        # --- Code Area --------------------------------------------------

        self.wg_area_code = QtGui.QWidget(self)

        # ----------------------------------------------------------------

        self.wg_main_tab = QtGui.QTabWidget()
        self.wg_main_tab.addTab(self.wg_blocks_view, 'Blocks')
        self.wg_main_tab.addTab(self.wg_area_code, 'Code')

        self.setCentralWidget(self.wg_main_tab)
        self.setGeometry(200, 100, 1000, 600)


class AppVisuino(QtGui.QApplication):
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)
        self.setStyle(QtGui.QStyleFactory.create('Plastique'))

    def execute(self):
        splash_pix = QtGui.QPixmap('splash_loading.png')
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        self.processEvents()

        main_win = MainWindow()
        main_win.show()
        splash.finish(main_win)
        sys.exit(self.exec_())


if __name__ == '__main__':
    app = AppVisuino(sys.argv)
    app.execute()
