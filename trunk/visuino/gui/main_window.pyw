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

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys

from visuino.gx.bases import *

class BlocksView(GxView):
    def __init__(self, parent):
        QGraphicsView.__init__(self, GxScene(parent=parent), parent)
        self.wheel_zoom = False

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.initUI()

    def initUI(self):

        # --- Blocks Area ------------------------------------------------

        self.wg_area_blocks = QWidget(self)

        self.wg_blocks_view = BlocksView(parent=self)
        self.wg_pallete_area = QWidget(self)
        self.wg_pallete_area.setFixedWidth(200)

        hl = QHBoxLayout()
        hl.addWidget(self.wg_pallete_area)
        hl.addWidget(self.wg_blocks_view)
        self.wg_area_blocks.setLayout(hl)

        # --- Code Area --------------------------------------------------

        self.wg_area_code = QWidget(self)

        # ----------------------------------------------------------------

        self.wg_main_tab = QTabWidget()
        self.wg_main_tab.addTab(self.wg_area_blocks, 'Blocks')
        self.wg_main_tab.addTab(self.wg_area_code, 'Code')

        self.setCentralWidget(self.wg_main_tab)
        self.setGeometry(200, 100, 1000, 600)


class AppVisuino(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)

    def execute(self):
        splash_pix = QPixmap('splash_loading.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
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
