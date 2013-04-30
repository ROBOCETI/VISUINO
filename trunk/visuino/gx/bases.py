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
__all__ = ['GxSceneBlocks', 'GxBlock','GxView']

from PyQt4.QtGui import *
from PyQt4.QtCore import *

try:
    from PyQt4.QtOpenGL import QGLWidget
except:
    QGLWidget = None

import sys
from visuino.gx.styles import *

class GxView(QGraphicsView):
    '''
    Holds optimization flags for the project in general and also
    offers wheel zooming functionality.

    Attributes:
        wheel_zoom: bool. Enable/disable "wheel zooming" feature.
        zoom_level: int. Indicates the current zoom magnification.
    '''
    def __init__(self, scene=None, parent=None, opengl=False,
                 wheel_zoom=False):
        ''' (QGraphicsScene, QWidget, bool) -> NoneType
        '''
        QGraphicsView.__init__(self, scene, parent)
##        QGraphicsView.__init__(self)  # for PySide

        # activates wheel zooming functionality
        self.wheel_zoom = wheel_zoom
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

##    def drawBackground(self, painter, rect):
##        ''' QGraphicsScene.drawBrackground(QPainter, QRectF) -> NoneType
##        '''
##
##        painter.setPen(QPen(QColor(203, 203, 203)))
##        painter.fillRect(rect, QColor(219, 219, 219))
##
##        W, H = rect.width(), rect.height()
##        for i in range(1, int(W), 20):
##            painter.drawLine(i, 0, i, H)
##        for j in range(1, int(H), 20):
##            painter.drawLine(0, j, W, j)


class GxSceneBlocks(QGraphicsScene):
    '''
    In addition to the bring to front functionality, manages resources for
    the blocks, such as its styles and colli paths.

    Attributes:
        Z_INCR: float
        _top_item: QGraphicsItem <None>. Item with the highest zValue.
        _top_z: float. zValue of the top most item.
        _click_to_front: bool. Enable/disable "click to front" feature.
        _background_grid: bool. Enable/disable the background grid.
        style: StyleBlocks.
        #io_colli_paths: set of GxColliPath, of kind 'io'.
        #vf_colli_paths: set of GxColliPath, of kind 'vf'.
    '''
    Z_INCREMENT = 0.0000000001   # increment on zValue for self.bringToFront()

    def __init__(self, background_grid=True, parent=None):
        ''' (QObject) -> NoneType
        '''
        QGraphicsScene.__init__(self, parent)

        self.setSceneRect(0, 0, 800, 600)
##        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        self.style = StyleBlocks()

        # information about the top-most item (changes with "bringToFront")
        self._top_item = None
        self._top_z = 0.0

        # if true, perform "self.bringToFront()" on the clicked item
        self._click_to_front = True

        # holds all the collidable items
        self._vf_male_colli_paths = set()
        self._vf_female_colli_paths = set()
        self._io_female_colli_paths = set()

        self._background_grid = background_grid
        self.setBackgroundBrush(QBrush(QColor('lightgray')))

    @property
    def vf_male_colli_paths(self):
        return self._vf_male_colli_paths

    @property
    def vf_female_colli_paths(self):
        return self._vf_female_colli_paths

    @property
    def io_female_colli_paths(self):
        return self._io_female_colli_paths    

    def drawBackground(self, painter, rect):
        ''' QGraphicsScene.drawBrackground(QPainter, QRectF) -> NoneType

        If self._background_grid flag is True, then draws a series of vertical
        and horizontal paralell lines to form a squared grid.
        '''
        QGraphicsScene.drawBackground(self, painter, rect)
        if self._background_grid:
            painter.setPen(QPen(QColor(203, 203, 203)))
            painter.fillRect(rect, QColor(219, 219, 219))

            W, H = self.sceneRect().width(), self.sceneRect().height()
            for i in range(1, int(W), 20):
                painter.drawLine(i, 0, i, H)
            for j in range(1, int(H), 20):
                painter.drawLine(0, j, W, j)

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
        self._click_to_front = value

    def getTopItem(self):
        ''' () -> QGraphicsItem

        Return the top-most item on the scene.
        '''
        if self._top_item:
            return self._top_item
        else:
            items = self.items()
            if items:
                return items[0]

    def bringToFront(self, item):
        ''' (QGraphicsItem) -> NoneType

        Make the given item the top-most on the scene by setting properly
        a new zValue (if necessary).
        '''
        if item != self._top_item:
            item.setZValue(self._top_z + self.Z_INCREMENT)
            self._top_z = item.zValue()
            self._top_item = item


class GxBlock(QGraphicsItem):
    def __init__(self, scene, parent=None):
        QGraphicsItem.__init__(self, parent, scene)
        self._width, self._height = 200, 100

        path = QPainterPath()
        path.addRect(self.boundingRect())
        self._border_path = path

        self.palette_blocks = None
        self._palette_colliding = False
        self.new_block = False
        
        self._default_block_cursor = Qt.OpenHandCursor
#        self.setCursor(self._default_block_cursor)

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def shape(self):
        ''' QGraphicsItem.shape() -> QPainterPath
        '''
        return self._border_path

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType

        TO BE REIMPLEMENTED
        '''
        pass

    def updateMetrics(self):
        ''' TO BE REIMPLEMENTED
        '''
        pass

    def prepareRemove(self):
        ''' TO BE REIMPLEMENTED
        '''
        pass

    def cloneMe(self, scene):
        ''' (GxSceneBlocks)

        REIMPLEMENT IF YOU WANT THIS BLOCK TO BE ON THE PALETTE
        '''
        pass
    
    def getWidth(self):
        return self._border_path.boundingRect().width()

    def getHeight(self):
        return self._border_path.boundingRect().height()
        
    def checkPaletteCollide(self):
        if self.palette_blocks:
            collide = self.collidesWithItem(self.palette_blocks) 

            if collide and not self.new_block and not self._palette_colliding:
                self.setCursor(self.palette_blocks.cursor_collide)
                self._palette_colliding = True
            elif not collide:
                self.setCursor(self._default_block_cursor)
                self.new_block = False
                self._palette_colliding = False

    
    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        
    def mouseMoveEvent(self, event):
        QGraphicsItem.mouseMoveEvent(self, event)
        self.checkPaletteCollide()        

    def mouseReleaseEvent(self, event):
        QGraphicsItem.mouseReleaseEvent(self, event)
        
        # this is for the case when de item is grabbed on the mouse by
        # the palette, and not by some mouse click event (drag and drop)
        mouse_grabber = self.scene().mouseGrabberItem()
        if mouse_grabber and mouse_grabber is self:
            self.ungrabMouse()
        
        if self.palette_blocks and self.collidesWithItem(self.palette_blocks):
            self.removeFromScene()
        
    def removeFromScene(self):
        self.scene().removeItem(self)


# -------------------------------------------------------------------------
# all the defintions from here are just for demonstration purposes

class GxExampleItem(QGraphicsItem):
    '''
    Shows how to create a graphics item from scratch.

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


def main():

    app = QApplication(sys.argv)

    # experience shows that QGraphicsView, although QWidget-based, does not
    # act very well as a window - does not quit the application properly
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)     # screen positon (200, 100)

    scene = GxSceneBlocks()   # remember: this one is not a QWidget-based object
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

    # ---------------------------------------------------------------------

    # remember: this one is just and special kind of QAbstractScrollArea
    # which suports vizualizing the scene, i.e., it does not handle the items
    view = GxView(scene, parent=win, wheel_zoom=True)

    win.setCentralWidget(view)  # therefore, the size of the view will be the
                                # size of the window, and both are not
                                # related to the size of the scene!
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()