#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Offer re-implementations of the two most basic objects on
#              the PyQt Graphics View Framework:
#                  - QGraphicsView ---> GxView
#                  - QGraphicsScene ---> GxScene.
#
#              Convention: All QGraphicsXXXXX related objects will have
#              their names started by "Gx" on this project.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free. Also, remember to keep the credits.
#-------------------------------------------------------------------------------
__all__ = ['GxView', 'GxScene', 'GxProxyToFront']

from PyQt4.QtGui import *
from PyQt4.QtCore import *
try:
    from PyQt4.QtOpenGL import QGLWidget
except:
    QGLWidget = None

import sys

class GxView(QGraphicsView):
    '''
    Holds desired optimization flags for the project in general, and also
    offers wheel zooming functionality.
    '''
    def __init__(self, scene=None, parent=None, opengl=False):
        ''' (QGraphicsScene, QWidget, bool) -> NoneType
        '''
        QGraphicsView.__init__(self, scene, parent)
##        QGraphicsView.__init__(self)  # for PySide

        self.wheel_zoom = True  # activates wheel zooming functionality
        self.zoom_level = 0     # incr/decr by 1 according to scaling calls
                                # just for monitoring purposes

        if QGLWidget and opengl:
            self.setViewport(QGLWidget())     # uses OpenGL for rendering

##        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # rectangle box selection
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.centerOn(0, 0)

    def wheelEvent(self, event):
        ''' QGraphicsView.wheelEvent(QWheelEvent) -> NoneType
        '''
        QGraphicsView.wheelEvent(self, event)

        if self.wheel_zoom:

            ##TODO: smooth zooming and keyboard shortcut zooming

            factor = 1.41 ** (event.delta() / 240.0)
            self.scale(factor, factor)

            if factor < 1: self.zoom_level -= 1
            else: self.zoom_level += 1

            print("Zoom level:", self.zoom_level)

            #self.centerOn(event.x(), event.y())


class GxScene(QGraphicsScene):
    '''
    Basically offers the "bring to front" functionality, where the itens
    can be brought to the front of the scene (by changing zValues).
    See also the "click to front" functionality.
    '''
    _BK_COLOR = 'lightgray'  # background color
    _Z_INCR = 0.0000000001   # increment on zValue for self.bringToFront()

    def __init__(self, parent=None):
        ''' (QObject) -> NoneType
        '''
        QGraphicsScene.__init__(self, parent)

##        scene.setItemIndexMethod(QGraphicsScene.NoIndex)

        # information about the top-most item (changes with "bringToFront")
        # {'z': float (item "stack" coordinate),
        #  'item': QGraphicsItem <None> (top-most item)}
        self._top_item = {'z': 0.0, 'item': None}

        # if true, perform "self.bringToFront()" on the clicked item
        self._click_to_front = True

        ##TODO: background grid option (is possible with brush styles?)
        self.setBackgroundBrush(QBrush(QColor(self._BK_COLOR)))
        self.setSceneRect(0, 0, 800, 600)

    def mousePressEvent(self, event):
        ''' QGraphicsScene.mousePressEvent(QGraphicsSceneMouseEvent)
            -> NoneType

        Appends treatement for the 'click to front' functionality.
        '''
        QGraphicsScene.mousePressEvent(self, event)

        grabber = self.mouseGrabberItem()   # item under the mouse
        if grabber and self._click_to_front:
            self.bringToFront(grabber)

    def setClickToFront(self, value):
        ''' (bool) -> NoneType

        Activates or not the "click to front" functionality, in which the
        clicked item always become the top-most one.
        '''
        if not isinstance(value, bool):
            raise ValueError('Parameter \'value\' must be of type bool.'+\
                ' Was given %s.' % value.__class__.__name__)

        self._click_to_front = value

    def getTopItem(self):
        ''' (None) -> QGraphicsItem

        Return the top-most item on the scene.
        '''
        if self._top_item == None:
            items = self.items()
            if items:
                return items[0]
        else:
            return self._top_item['item']

    def bringToFront(self, item):
        ''' (QGraphicsItem) -> NoneType

        Make the given item the top-most on the scene by setting properly
        a new zValue if necessary.
        '''
        if item != self._top_item['item']:
            item.setZValue(self._top_item['z'] + self._Z_INCR)
            self._top_item['z'] = item.zValue()
            self._top_item['item'] = item

    def drawBackground(self, painter, rect):
        ''' QtGui.QGraphicsScene.drawBrackground(
            QPainter, QRectF) -> NoneType

        rect: Exposed rectangle.
        '''
        painter.setPen(QPen(QColor(203, 203, 203)))
        painter.fillRect(rect, QColor(219, 219, 219))

        W, H = self.sceneRect().width(), self.sceneRect().height()
        for i in range(1, int(W), 20):
            painter.drawLine(i, 0, i, H)
        for j in range(1, int(H), 20):
            painter.drawLine(0, j, W, j)


class GxProxyToFront(QGraphicsProxyWidget):
    '''
    When clicked on the scene, brings its parent item to the front.

    Ps: Only works on GxScene.
    '''
    def mousePressEvent(self, event):
        ''' QGraphicsItem.mousePressEvent(QGraphicsSceneMouseEvent)
            -> NoneType
        '''
        QGraphicsProxyWidget.mousePressEvent(self, event)

        if self.scene() and isinstance(self.scene(), GxScene) and \
            self.parentItem():
            self.scene().bringToFront(self.parentItem())

# -------------------------------------------------------------------------
# all the defintions from here are just for demonstration, and not for
# the project

class GxExampleItem(QGraphicsItem):
    '''
    Shows how to create an graphics item from scratch.

    There are two mandatory virtual methods to be re-implemented:
        - boundingRect(), which returns the rectangle that defines the
          area of the item on the scene.
        - paint(), which actually perform the painting operations.
    '''
    def __init__(self, scene=None, parent=None):
        ''' (QGraphicsScene, QGraphicsItem) -> NoneType
        '''
        QGraphicsItem.__init__(self, parent, scene)
        self._width, self._height = 300, 100
        self._bk_color = QColor('darkgreen')

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), self._bk_color)


def config_item(item, pos=None, opengl=True):
    ''' (QGraphicsItem, tuple/list of 2 int/float, bool) -> NoneType

    Set the proper flags to the item and also its position.
    '''
    # required for anti-alias on open GL rendering
    if opengl:
        item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    item.setFlags(QGraphicsItem.ItemIsSelectable |
                  QGraphicsItem.ItemIsMovable)
    if pos:
        item.setPos(pos[0], pos[1])


if __name__ == '__main__':

    app = QApplication(sys.argv)

    # experience shows that QGraphicsView, although QWidget-based, does not
    # act very well as a window - does not quit the application properly
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)     # screen positon (200, 100)

    scene = GxScene()   # remember: this one is not a QWidget-based object
                        # it only acts as an indexing-manager container

    # ---- sample items ---------------------------------------------------

    elli = scene.addEllipse(QRectF(50, 100, 400, 200), QPen(QColor('black')),
                            QBrush(QColor('blue')))
    config_item(elli, [50, 100])

    text = scene.addText("Hello PyQt world", QFont("Comic Sans MS", 30))
    config_item(text, [50, 50])

    rect = scene.addRect(QRectF(100, 250, 300, 200), QPen(QColor('black')),
                         QBrush(QColor('red')))
    config_item(rect)

    example_item = GxExampleItem(scene)
    config_item(example_item, [420, 150])

    # here is how you put a widget on the scene: first create the widget,
    # then create a QGraphicsProxyWidget and set its parent to some item
    # already on the scene
    combobox = QComboBox()
    combobox.addItems(['hello', 'pyqt', 'world'])
    combobox.setFont(QFont('Verdana', 20))
    proxy = GxProxyToFront(example_item)
    proxy.setWidget(combobox)
    proxy.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
    proxy.setPos(50, 20)    # note that those coordinates are in respect
                            # with the proxy parent item (example_item)

    # ---------------------------------------------------------------------

    # remember: this one is just and special kind of QAbstractScrollArea
    # which suports vizualizing the scene, i.e., it does not handle the items
    view = GxView(scene, parent=win)

    win.setCentralWidget(view)  # therefore, the size of the view will be the
                                # size of the window, and both are not
                                # related to the size of the scene!
    win.show()
    sys.exit(app.exec_())
