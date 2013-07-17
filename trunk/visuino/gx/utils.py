#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Some facilities for working with the Graphics View framework.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

from visuino.gx.bases import *

__all__ = ['GxPainterPath', 'GxProxyToFront', 'item_to_svg', 
           'GxOutlinedText']

class GxPainterPath(QPainterPath):
    '''
    This class just append some facilities for the original QPainterPath,
    from the Graphics View Framework.

    For purposes of brevity and readability on the drawing code, you can
    now retrieve the current coordinates with the "x" and "y" properties.
    Also, the lineToInc() method provides a way to "walk" (forward/backward)
    on the path from the current position.

    Attributes:
        # x: current position's x-coordinate
        # y: current position's y-coordinate
    '''
    def __init__(self, start_point=None):
        ''' (QPointF) -> NoneType
        '''
        QPainterPath.__init__(self, start_point if start_point is not None
                                                else QPointF(0, 0))

    @property
    def x(self):
        ''' () -> float

        Return the x coordinate of the current position.
        '''
        return self.currentPosition().x()

    @property
    def y(self):
        ''' () -> float

        Return the y coordinate of the current position.
        '''
        return self.currentPosition().y()

    def lineToInc(self, dx=None, dy=None):
        ''' (number, number) -> NoneType

        From the current position, walks 'dx' on the x coordinate and 'dy'
        on the y coordinate. Use negative values to walk backwards on some
        direction.
        '''
        dx = 0 if not isinstance(dx, (int, float)) else dx
        dy = 0 if not isinstance(dy, (int, float)) else dy

        self.lineTo(self.x + dx, self.y + dy)


class GxProxyToFront(QGraphicsProxyWidget):
    '''
    When clicked on the scene, brings itself to the front, or its parents
    in case of having one. This is a fairly wanted effect for widgets on
    the scene, like comboboxes, for instance, where it's grop list should
    be always visible.

    Requirements: Item's scene must be GxScene.
    '''
    def mousePressEvent(self, event):
        ''' QGraphicsItem.mousePressEvent(QGraphicsSceneMouseEvent)
            -> NoneType

        Brings its parent to the front, if any and if the scene suports
        bringToFront() method.
        '''
        QGraphicsProxyWidget.mousePressEvent(self, event)

        if self.scene() and isinstance(self.scene(), GxScene) and \
            self.parentItem():
            self.scene().bringToFront(self.parentItem())
            

class GxOutlinedText(QGraphicsPathItem):
    '''
    Label that display outlined text.
    '''
    def __init__(self, text, font, scene, parent=None, **kwargs):
        '''
        :param text: ``str``
        :param font: ``QFont``
        :param scene: ``QGraphicsScene``
        :param parent: ``QGraphicsItem``
        :param kwargs:
            - 'outline_width': ``int``;
        '''
        self._text, self._font = text, font
        self._effect = QGraphicsDropShadowEffect()
        self._effect.setOffset(1.2, 1.2)
        
        self._outline_width = kwargs.get('outline_width', 1)
        
        path = QPainterPath(QPointF(0, 0))
        path.addText(path.currentPosition(), self._font, self._text)
        
        QGraphicsPathItem.__init__(self, path, parent, scene)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setGraphicsEffect(self._effect)
        self.setPos(0, 0)    
	
    def paint(self, painter, option=None, widget=None):
        painter.setPen(QPen(Qt.black, self._outline_width))
        painter.setBrush(Qt.white)
        painter.drawPath(self.path())
        
    def setPos(self, x, y):
        QGraphicsPathItem.setPos(self, x, y+self.boundingRect().height())

    
def test_outlined_text():
    app = QApplication([])
    win = QMainWindow()
    
    scene = GxSceneBlocks()
    view = GxView(scene)
    
    font = QFont('Verdana', 12, 40)
    font.setBold(True)
    out_text = GxOutlinedText("repita sempre", font, scene, outline_width=1)
    out_text.setPos(0, 0)
    
    win.setGeometry(200, 100, 800, 600)
    win.setCentralWidget(view)
    win.show()
    app.exec_()


def item_to_svg(gx_item, filename):
    ''' (QGraphicsItem, str) -> NoneType

    Prints the drawing of a graphics item onto a SVG file.
    '''
    svg_gen = QtSvg.QSvgGenerator()
    svg_gen.setFileName(filename)
    svg_gen.setSize(QtCore.QSize(gx_item._width, gx_item._height))
    svg_gen.setViewBox(QtCore.QRect(0, 0, gx_item._width, gx_item._height))

    painter = QtGui.QPainter()
    painter.begin(svg_gen)
    gx_item.paint(painter)
    painter.end()
    
if __name__ == '__main__':
    test_outlined_text()