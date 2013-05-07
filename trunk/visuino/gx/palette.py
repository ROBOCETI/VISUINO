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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from collections import OrderedDict

from visuino.gx.bases import *
from visuino.gx.blocks import *
from visuino.gx.styles import *
from visuino.gui import *
from visuino.resources import *

from visuino.core.xml_libs import *

XML_LIBRARIES = \
"""<?xml version="1.0" encoding="UTF-8"?>
<Libraries>
	<library name="Arduino.h">
		<function name="pinMode" return_type="" section="I/O">
			<arg name="pin" type="int" restriction="[0,)"/>
			<arg name="mode" type="int" restriction="INPUT,OUTPUT"/>
		</function> 
		<function name="digitalWrite" return_type="" section="I/O">
			<arg name="pin" type="int" restriction="[1,13]"/>
			<arg name="value" type="int" restriction="HIGH,LOW"/>
		</function>
		<function name="digitalRead" return_type="int" section="I/O">
			<arg name="pin" type="int" restriction="[1,13]"/>
		</function>		
        <function name="pulseIn" return_type="int" section="I/O">
            <arg name="pin" type="int" restriction="[1,13]"/>
            <arg name="value" type="int" restriction="HIGH,LOW"/>
            <arg name="timeout" type="int" restriction="0|"/>
        </function>
        <function name="millis" return_type="int" section="Time"/>
		<function name="delay" return_type="" section="Time">
			<arg name="milliseconds" type="int" restriction="[0,)"/>
		</function>
	</library>
</Libraries>
"""

class GxPaletteSection(QGraphicsItem):
    def __init__(self, scene, title, items, parent=None):
        QGraphicsItem.__init__(self, parent, scene)
        
        self._title = title
        
        self._width, self._height = 200, 40
        self._background_color = 'black'
        self._font_color = 'white'
        self._font = QFont('Verdana', 10)
        
        self._collapsed = False        
        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, widget=None, option=None):
        painter.fillRect(self.boundingRect(), 
                         QColor(self._background_color))
        painter.setPen(QPen(QColor(self._font_color)))
        painter.setFont(self._font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter,
                         self._title)


class GxLibrarySections(QGraphicsProxyWidget):
    def __init__(self, scene=None, opengl=False):
        QGraphicsProxyWidget.__init__(self)
        
        self._scene = QGraphicsScene()
        self._scene.setSceneRect(QRectF(0, 0, 200, 900))
        self._scene.setBackgroundBrush(QBrush(Qt.white))
        self._view = GxView(self._scene, opengl=opengl)
        self._view.setGeometry(0, 0, 200, 600)
        
        self.setWidget(self._view)
        self.setPos(400, 0)
        
        if isinstance(scene, QGraphicsScene):
            scene.addItem(self)
            
        self.sections = OrderedDict()


class GxPalette(QGraphicsProxyWidget):
    def __init__(self, scene=None, opengl=False):
        QGraphicsProxyWidget.__init__(self)

        self._scene = GxSceneBlocks(background_grid=False)
        self._scene.setSceneRect(0, 0, 200, 1000)

        grad = QLinearGradient(QPointF(0, 0),
                                     QPointF(200, 0))
        grad.setColorAt(0, QColor('#444444'))
        grad.setColorAt(0.3, Qt.gray)
        grad.setColorAt(1, QColor('#444444'))
        self._scene.setBackgroundBrush(QBrush(grad))

        self._view = GxView(self._scene, opengl=opengl)
        self._view.wheel_zoom = False
        self._view.setGeometry(0, 0, 200, 600)
        self._view.setFrameShape(QFrame.NoFrame)
#        self._view.setDragMode(QGraphicsView.NoDrag)

        self.setWidget(self._view)

        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.cursor_collide = QCursor(
            QPixmap(':delete_icon.png').scaled(64, 64))
        self.cursor_add = QCursor(
            QPixmap(':add_icon.png').scaled(64, 64))

        if isinstance(scene, QGraphicsScene):
            scene.addItem(self)

        self.setupBlocks()
        self._view.scale(0.85, 0.85)

    def setupBlocks(self):

        self._libs = Libraries(XML_LIBRARIES)
    
        v_spacing, left_padd = 10, 10
        y = v_spacing
        for k, function_def in self._libs['Arduino.h'].items():
            new_block = GxBlockFunctionCall(function_def, self._scene)
            new_block.setPos(left_padd if function_def.return_type else \
                left_padd + self._scene.style.notch.io_notch_width, y)
            new_block.setCursor(Qt.OpenHandCursor)
            new_block.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
            y += new_block.getHeight() + v_spacing


    def mousePressEvent(self, event):
        ''' QGraphicsProxyWidget.mousePressEvent(
                QGraphicsSceneMouseEvent) -> NoneType
        '''
        QGraphicsProxyWidget.mousePressEvent(self, event)

        self.scene().clearSelection()

        block_icon = self._view.itemAt(event.pos().toPoint())
        if block_icon and block_icon.parentItem():
            block_icon = block_icon.parentItem()

        if hasattr(block_icon, 'cloneMe'):

            new_block = block_icon.cloneMe(self.scene())
            new_block.setFlags(QGraphicsItem.ItemIsMovable)
            new_block.setCacheMode(QGraphicsItem.ItemCoordinateCache)

            new_block.palette_blocks = self
            new_block.new_block = True

            icon_mapped_pos = self._view.mapFromScene(block_icon.pos())
            new_block.setPos(QPointF(
                self.pos().x() + icon_mapped_pos.x() + 2,
                self.pos().y() + icon_mapped_pos.y() + 2))

            new_block.grabMouse()
            new_block.setCursor(Qt.OpenHandCursor)


class GxViewPalette(GxView):
    def __init__(self, parent=None, opengl=False):
        GxView.__init__(self, GxSceneBlocks(), parent, opengl)

        self.scene().setSceneRect(0, 0, 3000, 3000)
        self.scene().setParent(self)
        self.wheel_zoom = False

        self.palette = GxPalette(self.scene(), opengl)
        
#        self.palette_sections = GxLibrarySections(self.scene(), opengl)


    def scrollContentsBy(self, x, y):
        QGraphicsView.scrollContentsBy(self, x, y)
        self.palette.setPos(self.mapToScene(0, 0).x(),
                            self.mapToScene(0, 0).y())
        if x != 0:
            self.scene().bringToFront(self.palette)


    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.palette._view.setFixedHeight(self.height())


def main():
    app = QApplication(sys.argv)
#    app.setStyle(QStyleFactory.create('Plastique'))

    win = QMainWindow()
    win.setGeometry(100, 100, 900, 600)

    gx_palette_view = GxViewPalette(parent=win, opengl=True)

    win.setCentralWidget(gx_palette_view)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()