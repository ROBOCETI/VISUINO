# -*- coding: utf-8 -*-
from __future__ import division, print_function

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

from visuino.gx.bases import *
from visuino.gx.shapes import *
from visuino.gx.connections import *
from visuino.gx.styles import *

class GxBlockLoopDoWhile (ModelBlock):

    def __init__ (self, scene, parent=None):
        ModelBlock.__init__ (self,scene, parent)
    
    def paint (self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType

        TO BE REIMPLEMENTED
        '''
        sdw = self.scene ().style.do_while
        painter.fillRect(self.boundingRect(),
                         QColor (sdw.background_color))
    
        pass

def main ():
    app =  QApplication(sys.argv);
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)    
    scene = GxSceneBlocks()
    block = GxBlockLoopDoWhile (scene)
    block.setFlags(QGraphicsItem.ItemIsMovable)
    view = GxView (scene,parent = win)
    win.setCentralWidget(view)
    win.show()
    app.exec_()

if __name__ == '__main__': 
    main()
    
    