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
from __future__ import division, print_function

__all__ = ['GxPalette', 'GxViewPalette']

from PyQt4 import QtGui, QtCore
import sys

from visuino.gx.bases import *
from visuino.gx.blocks import *
from visuino.gx.styles import *
from visuino.gui import *
from visuino.resources import *


class GxPalette(QtGui.QGraphicsProxyWidget):
    def __init__(self, scene=None, opengl=False):
        QtGui.QGraphicsProxyWidget.__init__(self)

        self._scene = GxSceneBlocks(background_grid=False)
        self._scene.setSceneRect(0, 0, 200, 1000)

        grad = QtGui.QLinearGradient(QtCore.QPointF(0, 0),
                                     QtCore.QPointF(200, 0))
        grad.setColorAt(0, QtGui.QColor('#444444'))
        grad.setColorAt(0.3, QtCore.Qt.gray)
        grad.setColorAt(1, QtGui.QColor('#444444'))
        self._scene.setBackgroundBrush(QtGui.QBrush(grad))

        self._view = GxView(self._scene, opengl=opengl)
        self._view.wheel_zoom = False
        self._view.setGeometry(0, 0, 200, 600)
        self._view.setFrameShape(QtGui.QFrame.NoFrame)
        self._view.setDragMode(QtGui.QGraphicsView.NoDrag)

        self.setWidget(self._view)

        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.cursor_collide = QtGui.QCursor(
            QtGui.QPixmap(':delete_icon.png').scaled(64, 64))
        self.cursor_add = QtGui.QCursor(
            QtGui.QPixmap(':add_icon.png').scaled(64, 64))

        if isinstance(scene, QtGui.QGraphicsScene):
            scene.addItem(self)
                
        self.setupBlocks()
        self._view.scale(0.85, 0.85)

    def setupBlocks(self):
        
        self._functions = [
            {'name': 'pinMode', 
             'args': [FieldInfo('pin', 'int', '0|13', 'combobox'),
                      FieldInfo('mode', 'const', 'INPUT,OUTPUT', 'combobox')],
             'return': None},
             
            {'name': 'digitalRead', 
             'args': [FieldInfo('pin', 'int', '0|13', 'combobox')],
             'return': FieldInfo('value', 'int', 'HIGH,LOW', 'combobox')},

            {'name': 'digitalWrite', 
             'args': [FieldInfo('pin', 'int', '0|13', 'combobox'),
                       FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
             'return': None},
             
            {'name': 'analogRead', 
             'args': [FieldInfo('pin', 'int', '0|13', 'combobox')],
             'return': FieldInfo('value', 'int', 'HIGH,LOW', 'combobox')},

            {'name': 'analogWrite', 
             'args': [FieldInfo('pin', 'int', '0|13', 'combobox'),
                       FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
             'return': None},

            {'name': 'pulseIn', 
             'args':  [FieldInfo('pin', 'int', '0|', 'edit'),
                        FieldInfo('value', 'int', '0|', 'edit'),
                        FieldInfo('timeout', 'int', '0|', 'edit')],
             'return': FieldInfo('pulse_lenght', 'int', '0|', 'edit')},

            {'name': 'millis', 
             'args': None,
             'return': FieldInfo('milliseconds', 'int', '0|', 'edit')}]
        
        v_spacing, left_padd = 10, 10
        y = v_spacing
        for x in self._functions:
            new_block = GxBlockFunctionCall(x['name'], x['args'], x['return'],
                                            self._scene)
            new_block.setPos(left_padd if x['return'] else left_padd \
                + self._scene.style.notch.io_notch_width, y)
            new_block.setCursor(QtCore.Qt.OpenHandCursor)
            new_block.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
            y += new_block.getHeight() + v_spacing        


    def mousePressEvent(self, event):
        ''' QtGui.QGraphicsProxyWidget.mousePressEvent(
                QGraphicsSceneMouseEvent) -> NoneType
        '''
        QtGui.QGraphicsProxyWidget.mousePressEvent(self, event)
        
        self.scene().clearSelection()

        block_icon = self._view.itemAt(event.pos().toPoint())
        if block_icon and block_icon.parentItem():
            block_icon = block_icon.parentItem()

        if hasattr(block_icon, 'cloneMe'):

            new_block = block_icon.cloneMe(self.scene())
            new_block.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
            new_block.setCacheMode(QtGui.QGraphicsItem.ItemCoordinateCache)

            new_block.palette_blocks = self
            new_block.new_block = True

            icon_mapped_pos = self._view.mapFromScene(block_icon.pos())
            new_block.setPos(QtCore.QPointF(
                self.pos().x() + icon_mapped_pos.x() + 2,
                self.pos().y() + icon_mapped_pos.y() + 2))

            new_block.grabMouse()
            new_block.setCursor(QtCore.Qt.OpenHandCursor)


class GxViewPalette(GxView):
    def __init__(self, parent=None, opengl=False):
        GxView.__init__(self, GxSceneBlocks(), parent, opengl)

        self.scene().setSceneRect(0, 0, 3000, 3000)
        self.scene().setParent(self)
        self.wheel_zoom = False

        self.palette = GxPalette(self.scene(), opengl)


    def scrollContentsBy(self, x, y):
        QtGui.QGraphicsView.scrollContentsBy(self, x, y)
        self.palette.setPos(self.mapToScene(0, 0).x(),
                            self.mapToScene(0, 0).y())
        if x != 0:
            self.scene().bringToFront(self.palette)


    def resizeEvent(self, event):
        QtGui.QGraphicsView.resizeEvent(self, event)
        self.palette._view.setFixedHeight(self.height())


def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create('Plastique'))

    win = QtGui.QMainWindow()
    win.setGeometry(100, 100, 900, 600)

    gx_palette_view = GxViewPalette(parent=win, opengl=True)

    win.setCentralWidget(gx_palette_view)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()