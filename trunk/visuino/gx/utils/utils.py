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
__all__ = ['GxPainterPath', 'gx_item_to_svg']

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

class GxPainterPath(QPainterPath):
    def __init__(self, start=None):
        ''' (QPointF) -> NoneType
        '''
        QPainterPath.__init__(self, start if isinstance(start, QPointF)
                                    else QPointF(0, 0))

    def lineToInc(self, dx=None, dy=None):
        ''' (float, float) -> NoneType
        '''
        pos = self.currentPosition()

        dx = 0 if not isinstance(dx, (int, float)) else dx
        dy = 0 if not isinstance(dy, (int, float)) else dy

        self.lineTo(pos.x() + dx, pos.y() + dy)

    def getPos(self):
        ''' () -> (float, float)

        Return a tuple with the current position.
        '''
        return self.currentPosition().x(), self.currentPosition().y()

    @property
    def x(self):
        ''' () -> float

        Return the x coordinate of the current position
        '''
        return self.currentPosition().x()

    @property
    def y(self):
        ''' () -> float

        Return the y coordinate of the current position
        '''
        return self.currentPosition().y()


def gx_item_to_svg(gx_item, filename):
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(filename)
    svg_gen.setSize(QSize(gx_item._width, gx_item._height))
    svg_gen.setViewBox(QRect(0, 0, gx_item._width, gx_item._height))

    painter = QPainter()
    painter.begin(svg_gen)
    gx_item.paint(painter)
    painter.end()