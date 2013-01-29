# -*- coding: utf-8 -*-
"""
@author: Nelso G. Jost
@email: nelsojost@gmail.com
@project: VISUINO - A visual programming toolkit for Arduino
"""
from __future__ import division

import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

from bases import *
from shapes import *

__all__ = ['NotchPath', 'CornerPath', 'GxShapeNotchLeft']

class GxExpression(GxShapeNotchLeft):
    _FIELD_V_PADD = 6
    _FIELD_H_PADD = 6  
    
    
    def __init__(self, notch='trig', scene=None, parent=None):
        GxShapeNotchLeft.__init__(self, notch, scene, parent)
        
        self._bk_color = "lightgreen"
        self._BORDER_WIDTH = 1
        self._NOTCH_SIZE = [10, 20]
        self._CORNER_STYLE = 'rect'
        self._CORNER_SIZE = [6, 6]
                
        field = GxField(notch=notch, scene=scene, parent=self)
        field.setPos(2 + self._FIELD_H_PADD, 
                     self._FIELD_V_PADD)
        
        self._width = -3 + self._NOTCH_SIZE[0] + self._FIELD_H_PADD + field._width
        self._height = 2*self._FIELD_V_PADD + field._height

        print field._width, field._height
        

class GxOperatorBlock(GxShapeNotchLeft):
    pass

class GxField(GxShapeNotchLeft):
    def __init__(self, notch='trig', scene=None, parent=None):
        GxShapeNotchLeft.__init__(self, notch, scene, parent)
        self._width, self._height = 40, 30
        self._NOTCH_SIZE = [10, 20]
        self._bk_color = 'white'
        self._BORDER_COLOR = Qt.transparent
        self._CORNER_STYLE = 'rect'
        self._CORNER_SIZE = [0, 0]
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()
                     
    expr = GxExpression(scene=scene)
    expr.setFlags(QGraphicsItem.ItemIsMovable | 
                  QGraphicsItem.ItemIsSelectable)
    expr.setPos(100, 100)
    
    field = GxField(scene=scene)
    
    view = GxView(scene, parent=win)    
    
    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())        