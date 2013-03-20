#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements a palette for blocks drag and drop.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['GxPalette', 'GxPaletteView']

from PyQt4 import QtGui, QtCore
import sys

from visuino.gx.bases import *
from visuino.gx.blocks import *
from visuino.gui import *


class GxPalette(QtGui.QGraphicsProxyWidget):
    def __init__(self, scene=None):
        QtGui.QGraphicsProxyWidget.__init__(self)

        self._scene = GxScene()
        self._scene.setSceneRect(0, 0, 200, 1000)

        self._view = GxView(self._scene)
        self._view.wheel_zoom = False
        self._view.setGeometry(0, 0, 200, 600)

        self.setWidget(self._view)

        if isinstance(scene, QtGui.QGraphicsScene):
            scene.addItem(self)

        self.setupBlocks()

    def setupBlocks(self):
        y = 10

        block_digital_read = GxBlockFunctionCall('digitalRead',
            [FieldInfo('pin', 'int', '0|13', 'combobox')],
            FieldInfo('value', 'int', 'HIGH,LOW', 'combobox'),
            StyleBlockFunctionCall(), self._scene)
        block_digital_read.setPos(10, y)
        y += block_digital_read.boundingRect().height() + 10

        block_digital_write = GxBlockFunctionCall('digitalWrite',
            [FieldInfo('pin', 'int', '0|13', 'combobox'),
             FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
            None, StyleBlockFunctionCall(), self._scene)
        block_digital_write.setPos(20, y)

    def mousePressEvent(self, event):
        QtGui.QGraphicsProxyWidget.mousePressEvent(self, event)

        block_icon = self._scene.itemAt(event.pos())
        if hasattr(block_icon, 'cloneMe'):

            print("mah oe")

            new_block = block_icon.cloneMe()
            self.scene().addItem(new_block)
            new_block.setFlags(QtGui.QGraphicsItem.ItemIsSelectable|
                               QtGui.QGraphicsItem.ItemIsMovable)
            new_block.setPos(self.pos().x() + 300, self.pos().y())
            if isinstance(self.scene(), GxScene):
                print("To front")
                self.scene().bringToFront(new_block)


class GxPaletteView(GxView):
    def __init__(self, parent=None, opengl=True):
        GxView.__init__(self, GxScene(), parent, opengl)

        self.scene().setSceneRect(0, 0, 1000, 2000)
        self.wheel_zoom = False

        self.palette = GxPalette(self.scene())

        my_style = StyleBlockFunctionCall()

    def scrollContentsBy(self, x, y):
        QtGui.QGraphicsView.scrollContentsBy(self, x, y)
        self.palette.setPos(self.mapToScene(0, 0))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create('Plastique'))

    win = QtGui.QMainWindow()
    win.setGeometry(200, 100, 1000, 600)

    gx_palette_view = GxPaletteView(parent=win)

    win.setCentralWidget(gx_palette_view)
    win.show()
    sys.exit(app.exec_())
