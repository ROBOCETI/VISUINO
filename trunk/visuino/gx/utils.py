# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 16:33:47 2013

@author: nelso
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *


__all__ = ['create_svg_from_gx_item', 'GxPainterPath']

class GxPainterPath(QPainterPath):
    def __init__(self, start_point):
        QPainterPath.__init__(self, start_point)
        
    def lineToInc(self, dx=None, dy=None):
        pos = self.currentPosition()
        
        dx = 0 if not isinstance(dx, (int, float)) else dx
        dy = 0 if not isinstance(dy, (int, float)) else dy
        
        self.lineTo(pos.x() + dx, pos.y() + dy)
        

def create_svg_from_gx_item(gx_item, filename):
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(filename)
    svg_gen.setSize(QSize(gx_item._width, gx_item._height))
    svg_gen.setViewBox(QRect(0, 0, gx_item._width, gx_item._height))

    painter = QPainter()
    painter.begin(svg_gen)
    gx_item.paint(painter)
    painter.end()