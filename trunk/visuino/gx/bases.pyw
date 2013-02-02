#-------------------------------------------------------------------------------
# Name:        gx_bases.pyw
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Purpose:     Offer re-implementations of the two most basic objects on
#              the PyQt Graphics View Framework:
#                  - QGraphicsView --> GxView
#                  - QGraphicsScene --> GxScene.
#
#              Convention: All QGraphics___ related objects will have
#              their names started by "Gx" on this project.
#
# Licence:     GPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

##from PySide.QtGui import *
##from PySide.QtCore import *

__all__ = ['GxView', 'GxScene', 'GxProxyToFront']

class GxView(QGraphicsView):
    def __init__(self, scene=None, parent=None, **kwargs):
        """
        :scene: QGraphicsScene().
        :parent: QWidget().

        kwargs:
         :wheel_zoom: bool <True>. Activates the wheel zooming functionality.
        """
##        QGraphicsView.__init__(self)
        QGraphicsView.__init__(self, scene, parent)

        self.wheel_zoom = kwargs.get('wheel_zoom', True)

#        self._wheel_zoom = getv_kw(
#            kwargs, 'wheel_zoom', True, (bool, GxScene))

        self.zoom_level = 0     # incr/decr by 1 according to scaling calls

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

        # click on the background to drag the whole scene
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
##        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

        self.centerOn(0, 0)


    def wheelEvent(self, event):
        """
        Scales the scene based on some delta change of the mouse wheel
        movement. Its fairly the simpliest way of doing this.

        Re-implemented from base QGraphicsView.

        :event: QWheelEvent().
        """
        QGraphicsView.wheelEvent(self, event)

        if self.wheel_zoom:

            ##TODO: smooth zooming

            factor = 1.41 ** (event.delta() / 240.0)
            self.scale(factor, factor)

            if factor < 1: self.zoom_level -= 1
            else: self.zoom_level += 1

            print "Zoom level:", self.zoom_level

            #self.centerOn(event.x(), event.y())


class GxScene(QGraphicsScene):

    BK_COLOR = 'lightgray'  # background color

    Z_INCR = 0.0000000001   # increment on zValue for .bringToFront()

    WIDTH = 800
    HEIGHT = 600

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        # information about the top-most item (changes with "bringToFront")
        self._top_item = {'z': 0.0, 'item': None}

        # if true, perform "self.bringToFront()" on the clicked item
        self._click_to_front = False

        ##TODO: use brush styles, like Qt.Dense7Pattern, for backg. grids
        self.setBackgroundBrush(QBrush(QColor(self.BK_COLOR)))
        self.setSceneRect(0, 0, self.WIDTH, self.HEIGHT)

    def _clickToFront(self, event):
        """
        If the flag self._click_to_front is True, then bring the clicked
        item to the front.

        :event: QGraphicsSceneMouseEvent.
        """
        # read the item on the scene mouse coordinates, and then
        # if it is not None, bring it to the front

        item = self.itemAt(event.scenePos())
        if isinstance(item, QGraphicsItem) and item.isSelected():
            self.bringToFront(item)

    def mousePressEvent(self, event):
        """
        Offers the "click to front" functionality.

        RE-IMPLEMENTED from QGraphicsScene.
        :event: QGraphicsSceneMouseEvent.
        """
        QGraphicsScene.mousePressEvent(self, event)

        if self._click_to_front:
            self._clickToFront(event)

    def setClickToFront(self, value):
        """
        Activates or not the "click to front" functionality, in which the
        clicked item always become the top-most one.

        :value: boolean.
        """
        if not isinstance(value, bool):
            raise ValueError('Parameter \'value\' must be of type bool.'+\
                ' Was given %s.' % value.__class__.__name__)

        self._click_to_front = value

    def getTopItem(self):
        """
        Return the top-most item on the scene.

        :return: QGraphicsItem.
        """
        if self._top_item == None:
            items = self.items()
            if items:
                return items[0]
        else:
            return self._top_item['item']

    def bringToFront(self, item):
        """
        Make the given item the top-most on the scene by setting properly
        a new zValue if necessary.

        :item: QGraphicsItem().
        """
        if not isinstance(item, QGraphicsItem):
            raise ValueError('Parameter \'item\' must be of type '+\
                'QGraphicsItem. Was given %s.' % item.__class__.__name__)

        if item != self._top_item['item']:
            item.setZValue(self._top_item['z'] + self.Z_INCR)
            self._top_item['z'] = item.zValue()
            self._top_item['item'] = item

class GxProxyToFront(QGraphicsProxyWidget):
    """
    New feature added: when clicked, brings its parent on the top
    of the scene.
    """
    def mousePressEvent(self, event):
        QGraphicsProxyWidget.mousePressEvent(self, event)
        self.scene().bringToFront(self.parentItem())


def main():

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()
    scene.setClickToFront(True)

    elli = scene.addEllipse(QRectF(50, 100, 400, 200), QPen(QColor('black')),
        QBrush(QColor('blue')))
    elli.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)
    elli.setPos(100, 50)

    text = scene.addText("Hello PyQt world", QFont("Comic Sans MS", 30))
    text.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)
    text.setPos(50, 50)

    rect = scene.addRect(QRectF(100, 250, 300, 200), QPen(QColor('black')),
        QBrush(QColor('red')))
    rect.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)

    car = scene.addPixmap(QPixmap('car.png'))
    car.setPos(400, 400)
    car.setFlags(QGraphicsItem.ItemIsMovable)

    view = GxView(scene, win, wheel_zoom=34)

    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
	main()