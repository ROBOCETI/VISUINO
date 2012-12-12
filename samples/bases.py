#-------------------------------------------------------------------------------
# Name:        bases.py
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Purpose:     Holds basic implementations for views and scenes.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class BaseView(QGraphicsView):
    def __init__(self, scene=None, parent=None, **kwargs):
        """
        scene: QGraphicsScene().
        parent: QWidget().

        kwargs:
         - wheel_zoom: boolean (True).
            Activates the wheel zooming functionality.
        """
        QGraphicsView.__init__(self, scene, parent)
        self.wheel_zoom = kwargs.get('wheel_zoom', True)
        self.zoom_level = 0     # incr/decr by 1 according to scalings

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

        self.setGeometry(100, 100, 800, 600)

        # click on the background to drag the whole scene
        self.setDragMode(QGraphicsView.RubberBandDrag)


    def wheelEvent(self, event):
        """
        Scales the scene based on some delta change on the mouse wheel
        movement. Its fairly the simpliest way of doing this.

        Re-implemented from base QGraphicsView.

        event: QWheelEvent().
        """
        QGraphicsView.wheelEvent(self, event)

        if self.wheel_zoom:

            ##TODO: understand this formula?! Can be useful for
            # smooth zooming implementations!
            factor = 1.41 ** (event.delta() / 240.0)
            self.scale(factor, factor)

            if factor < 1: self.zoom_level -= 1
            else: self.zoom_level += 1

            print(self.zoom_level)


class BaseScene(QGraphicsScene):

    BACKGROUND_COLOR = QColor(200, 200, 200)

    Z_INCR = 0.0000001

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        # information about the top-most item (changes with "bringToFront")
        self._top_item = {'z': 0.0, 'item': None}

        # if true, perform "self.bringToFront()" on the clicked item
        self.click_to_front = False

        ##TODO: use brush styles, like Qt.Dense7Pattern, for backg. grids
        self.setBackgroundBrush(QBrush(self.BACKGROUND_COLOR))
        self.setSceneRect(0, 0, 640, 480)

    def mousePressEvent(self, event):
        super(BaseScene, self).mousePressEvent(event)

        if self.click_to_front:
            # read the item on the scene mouse coordinates, and then
            # if it is not None, bring it to the front

            item = self.itemAt(event.scenePos())
            if isinstance(item, QGraphicsItem) and item.isSelected():
                self.bringToFront(item)

    def getTopItem(self):
        """
        Return the top-most item on the scene.
        """
        if self._top_item == None:
            items = self.items()
            if items:
                return items[0]
        else:
            return self._top_item['item']

    def bringToFront(self, item):
        """
        item: QGraphicsItem().
        """
        if item != self._top_item['item']:
            item.setZValue(self._top_item['z'] + self.Z_INCR)
            self._top_item['z'] = item.zValue()
            self._top_item['item'] = item


def main():
    app = QApplication([])

    scene = BaseScene()

    elli = scene.addEllipse(QRectF(50, 50, 400, 200), QPen(QColor('black')),
        QBrush(QColor('blue')))
    elli.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)

    text = scene.addText("Hello world", QFont("Comic Sans MS", 30))
    text.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)

    rect = scene.addRect(QRectF(200, 200, 300, 200), QPen(QColor('black')),
        QBrush(QColor('darkred')))
    rect.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)

    view = BaseView(scene)
    view.show()

    app.exec_()

if __name__ == '__main__':
    main()
