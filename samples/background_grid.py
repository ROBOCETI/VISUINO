#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      nelso
#
# Created:     12/12/2012
# Copyright:   (c) nelso 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *

class GridBackView(BaseView):
    GRID_STEP = 30
    AREA_PROPORTION = (4, 3)
    AREA_SCALE = 320

    def __init__(self, scene=None, parent=None, **kwargs):

        super(GridBackView, self).__init__(scene, parent)

        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # problem: not preserve antialiasing
        #self.setCacheMode(QGraphicsView.CacheBackground)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.scene().setSceneRect(0, 0,
            self.AREA_PROPORTION[0]*self.AREA_SCALE,
            self.AREA_PROPORTION[1]*self.AREA_SCALE)

        print self.sceneRect()

    def drawBackground(self, painter, rect):

        brush = QBrush(self.scene().BACKGROUND_COLOR)
##        brush.setStyle(Qt.Dense7Pattern)

        painter.fillRect(rect, brush)

        pen = QPen(QColor(60, 60, 60))
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QColor(60, 60, 60))

        W = self.sceneRect().width()
        H = self.sceneRect().height()

        for i in xrange(0, int(W), self.GRID_STEP):
            for j in xrange(0, int(H), self.GRID_STEP):
                painter.drawPoint(i, j)


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = BaseScene()

    elli = scene.addEllipse(QRectF(50, 50, 400, 200), QPen(QColor('black')),
        QBrush(QColor('blue')))
    elli.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)

    view = GridBackView(scene)
    
    win.setCentralWidget(view)	
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
