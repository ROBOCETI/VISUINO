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
"""
The Graphics View Framework of PyQt relies on the following three main objects:
    
    * **QGraphicsItem** : Represents a 2D graphical object. Can be drawn using
      primitives from ``QPainter`` or also can load images.
    
    * **QGraphicsScene** : Container for ``QGraphicsItem`` objects, managing
      all the itens positions, rectangles and stacking order.
    
    * **QGraphicsView** : A ``QWidget`` specialized on draw contents from some
      ``QGraphicsScene``.
    
This module provides re-implementations for each one of those objects, by
setting up some attributes project-specific and also adding some new funtionality.

**Convention**: Classes beginning with ``Gx`` mean that they are somehow related
to the Graphics View Framework or represents subclasses of ``QGraphicsItem``,
i.e., can be inserted on the scene.
"""

from __future__ import division, print_function
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

try:
    from PyQt4.QtOpenGL import QGLWidget
except:
    QGLWidget = None

__all__ = ['GxSceneBlocks', 'GxBlock','GxView']

class GxView(QGraphicsView):
    '''
    Holds optimization flags for the project in general and also
    offers wheel zooming.
    
    :ivar wheel_zoom: ``bool`` <False>. 
        Enable/disable the wheel zooming feature.
    :ivar _zoom_level: ``int`` <0>. 
        Keeps track of how many scalings have occured.
    '''
    def __init__(self, scene=None, parent=None, opengl=False,
                 wheel_zoom=False):
        '''        
        :param scene: ``QGraphicsScene`` <None>.
            *QGraphicsView.__init__()*.
        :param parent: ``QWidget`` <None>.
            *QGraphicsView.__init__()*.
        :param opengl: ``bool`` <False>.
            Enables use of Open GL rendering through **PyQt4.QtOpenGL.QGLWidget**.
        :param wheel_zoom: ``bool`` <False>.
            Enables wheel zooming functionality.
        '''
        QGraphicsView.__init__(self, scene, parent)

        self.wheel_zoom = wheel_zoom
        self._zoom_level = 0

        if QGLWidget and opengl:
            self.setViewport(QGLWidget())

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
        ''' *QGraphicsView.wheelEvent(QWheelEvent) -> NoneType*
        
        Provides the wheel zooming functionality by calling 
        ``QGraphicsView.scale()`` according to the amount of scrolling.
        '''
        QGraphicsView.wheelEvent(self, event)

        if self.wheel_zoom:

            ##TODO: smooth zooming and keyboard shortcut zooming

            factor = 1.41 ** (event.delta() / 240.0)
            self.scale(factor, factor)

            if factor < 1: self._zoom_level -= 1
            else: self._zoom_level += 1

            print("Zoom level:", self._zoom_level)

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
    Besides adding the "bring to front" functionality (along with "click to
    front"), this class also holds sets of paths used to detect collision 
    between notches (see ``visuino.gx.connections``).
        
    :ivar background_grid: ``bool`` <True>.
        Enables the drawing of a grid on the background layer of the scene.
        
    :ivar click_to_front: ``bool`` <True>.
        Enables the "click to front" feature, on which the clicked item always        
        is brought to the front of the scene.
        
    :ivar vf_male_colli_paths: ``set`` of ``visuino.gx.connections.GxColliPath``.
        Hold paths for detecting collision of moving female -> male VF notches.
        
    :ivar vf_female_colli_paths: ``set`` of ``visuino.gx.connections.GxColliPath``.
        Hold paths for detecting collision of moving male -> female VF notches.
        
    :ivar io_female_colli_paths: ``set`` of ``visuino.gx.connections.GxColliPath``.
        Hold paths for detecting collision of moving male -> female IO notches.        
        
    :ivar _top_item: ``QGraphicsItem`` <None>.
        Holds the last item brought to the front. Therefore, changes with 
        ``self.bringToFront()``.
    
    :ivar _top_z: ``float`` <None>.
        zValue of the top-most item on the scene. Changes with 
        ``self.bringToFront()``.
    '''
    #: Increment on zValue for use on ``self.bringToFront()``
    Z_INCREMENT = 0.0000000001       

    def __init__(self, parent=None, background_grid=True):
        '''
        :param parent: ``QObject``. *QGraphicsScene.__init__()*
        :param background_grid: ``bool``.
            Enables drawing of a grid on the background layer of the scene.
        '''
        QGraphicsScene.__init__(self, parent)
        
        self.background_grid = background_grid
        self.setSceneRect(0, 0, 800, 600)        
        self.setBackgroundBrush(QBrush(QColor('lightgray')))        
##        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # if true, perform "self.bringToFront()" on the clicked item
        self.click_to_front = True

        # holds all the collidable items
        self.vf_male_colli_paths = set()
        self.vf_female_colli_paths = set()
        self.io_female_colli_paths = set()
        
        # information about the top-most item (changes with "bringToFront")
        self._top_item = None
        self._top_z = 0.0     
        
    def getTopItem(self):
        ''' 
        :return: ``QGraphicsItem`` - The top-most item on the scene.
        '''
        if self._top_item:
            return self._top_item
        else:
            items = self.items()
            if items:
                return items[0]

    def bringToFront(self, item):
        '''
        Make the given item the top-most on the scene by setting properly
        a new zValue (if necessary).
        
        :param item: ``QGraphicsItem``.        
        '''
        if item != self._top_item:
            item.setZValue(self._top_z + self.Z_INCREMENT)
            self._top_z = item.zValue()
            self._top_item = item        

    def drawBackground(self, painter, rect):
        ''' *QGraphicsScene.drawBrackground(QPainter, QRectF) -> NoneType*

        If ``self.background_grid`` flag is ``True``, then draws a series of 
        vertical and horizontal paralell lines to form a squared grid.
        '''
        QGraphicsScene.drawBackground(self, painter, rect)
        if self.background_grid:
            painter.setPen(QPen(QColor(203, 203, 203)))
            painter.fillRect(rect, QColor(219, 219, 219))

            W, H = self.sceneRect().width(), self.sceneRect().height()
            for i in range(1, int(W), 20):
                painter.drawLine(i, 0, i, H)
            for j in range(1, int(H), 20):
                painter.drawLine(0, j, W, j)

    def mousePressEvent(self, event):
        ''' *QGraphicsScene.mousePressEvent(QGraphicsSceneMouseEvent) -> NoneType*

        Appends the "click to front" functionality.
        '''
        QGraphicsScene.mousePressEvent(self, event)
        
        grabber = self.mouseGrabberItem()   # item under the mouse
        if grabber and self.click_to_front:
            self.bringToFront(grabber)    


class GxBlock(QGraphicsItem):
    '''
    Abstract base class that implements basic attributes and functionality for
    any graphical block to be inserted on ``GxSceneBlocks``.
    
    The virtual method ``paint()`` of ``QGraphicsItem`` base class must be
    re-implemented, also with the three following ones:
        
        * ``getBorderWidth()``;        
        * ``updateMetrics()``;        
        * ``cloneMe()``;
          
    No need to re-implement ``QGraphicsItem.boundingRect()``.
    
    :ivar _width: ``number`` <200>. 
        Width of the bounding rectangle.
        
    :ivar _height: ``number`` <100>.
        Height of the bounding rectangle.
        
    :ivar _border_path: ``QPainterPath``.
        Path that defines the shape of this item. The default path is a rect
        that contains its bounding rectangle.
        
    :ivar _default_block_cursor: ``QCursor`` <Qt.OpenHandCursor>.
        Cursor used when the block is not colliding with the palette.
        
    :ivar _palette_colliding: ``bool``.
        Flag to indicate palette collision. See ````self.checksPaletteCollide()``.
    
    :ivar palette_blocks: ``visuino.gx.palette.GxPalette`` <None>.
        Used to detecting collision with the palette. Should be set only 
        by the palette itself. See ``self.checksPaletteCollide()``.

    :ivar new_block: ``bool``.
        Tells if this block has just been instantiated by the palette.
        See ``self.checksPaletteCollide()``. Should be set only by the palette
        itself.
    '''
    def __init__(self, scene, parent=None):
        '''
        :param scene: ``GxSceneBlocks``.
            By convention, in this project all blocks are inserted on the
            scene right here, on instantiation.
        :param parent: ``GxBlock``.
        '''
        QGraphicsItem.__init__(self, parent, scene)
        self._width, self._height = 200, 100

        path = QPainterPath()
        path.addRect(self.boundingRect())
        self._border_path = path

        self._palette_colliding = False
        self.palette_blocks = None
        self.new_block = False
        
        self._default_block_cursor = Qt.OpenHandCursor
#        self.setCursor(self._default_block_cursor)

    def _checkPaletteCollide(self):
        '''        
        Check if it is colliding with the palette and respond properly
        by updating the cursor shape. Designed to be called on the mouse 
        move event of this item.
        '''
        if self.palette_blocks:
            collide = self.collidesWithItem(self.palette_blocks) 

            if collide and not self.new_block and not self._palette_colliding:
                self.setCursor(self.palette_blocks.cursor_collide)
                self._palette_colliding = True
            elif not collide:
                self.setCursor(self._default_block_cursor)
                self.new_block = False
                self._palette_colliding = False
        
    def boundingRect(self):
        ''' *QGraphicsItem.boundingRect() -> QRectF*
        
        :return: ``QRectF`` - retangle with dimensions (``self._width``, 
                 ``self._height``).
        '''
        return QRectF(0, 0, self._width, self._height)

    def shape(self):
        '''        
        :return: ``QPainterPath`` - Item delimiting shape.
        '''
        return self._border_path

    def updateMetrics(self):
        ''' *TO BE RE-IMPLEMENTED*
        
        The purpose of this method should be to update the block dimentions
        and also its border path according to its contents.
        
        Example::
        
            def updateMetrics(self):
                self.prepareGeometryChange()
            
                self._width, self._height = 200, 100
        
                path = QPainterPath()
                path.addRect(self.boundingRect())
                self._border_path = path
        
                self.update(self.boundingRect())
            
        ''' 
        pass        

    def cloneMe(self, scene):
        ''' *TO BE RE-IMPLEMENTED*
        
        Should return an instance of itself, with the very same attribute 
        values. This method is used mainly ``visuino.gx.palette.GxPalette`` 
        to instantiate new blocks on the given scene.
        
        :param scene: ``GxSceneBlocks``.
        :return: ``GxBlock`` subclass.
        '''
        return GxBlock(scene)
    
    def getBorderWidth(self):
        ''' *TO BE RE-IMPLEMENTED*
        
        Should return the correct border width value for this kind of block.
        See ``visuino.settings``.
        '''        
        return 2
    
    def getWidth(self):
        '''
        :return: ``number``. Width of its path bounding rectangle.
        '''
        return self._border_path.boundingRect().width()

    def getHeight(self):
        '''
        :return: ``number``. Height of its path bounding rectangle.
        '''
        return self._border_path.boundingRect().height()
        
    def getTopParentItem(self):
        '''
        :return: ``GxBlock`` - The top-most parent item (if no parent, then return ``self``).
        '''
        parent = self.parentItem()
        if not parent:
            return self
        else:
            while True:
                if parent.parentItem() is None:
                    return parent
                else:
                    parent = parent.parentItem()

    def removeFromScene(self):
        '''
        This method should be used to remove a ``GxBlock`` from the scene.
        First, it calls ``removeFromScene`` on all its childs, because some
        of them might be ``visuino.gx.connections.GxColliPath``, which has
        its on ``removeFromScene()`` special behavior.
        '''
        for child in self.childItems():
            child.removeFromScene()
        if self.scene():
            self.scene().removeItem(self)
                            
#    def mousePressEvent(self, event):
#        ''' *QGraphicsItem.mousePressEvent(QGraphicsSceneMouseEvent) -> NoneType*
#        '''
#        QGraphicsItem.mousePressEvent(self, event) 
        
    def mouseMoveEvent(self, event):
        ''' *QGraphicsItem.mouseMoveEvent(QGraphicsSceneMouseEvent) -> NoneType*
        
        Calls ``self._checkPaletteCollide()``.
        '''        
        QGraphicsItem.mouseMoveEvent(self, event)
        self._checkPaletteCollide()        

    def mouseReleaseEvent(self, event):
        ''' *QGraphicsItem.mouseReleaseEvent(QGraphicsSceneMouseEvent) -> NoneType*
        
        If it is colliding with the palette, then remove itself from the scene.
        '''   
        QGraphicsItem.mouseReleaseEvent(self, event)
        
        # this is for the case when de item is grabbed on the mouse by
        # the palette, and not by some mouse click event (drag and drop)
        mouse_grabber = self.scene().mouseGrabberItem()
        if mouse_grabber and mouse_grabber is self:
            self.ungrabMouse()
        
        if self.palette_blocks:
            scene = self.scene() 
            if self.collidesWithItem(self.palette_blocks):
                self.removeFromScene()
            for item in scene.selectedItems():
                if item and item.collidesWithItem(item.palette_blocks):
                    item.removeFromScene()                  


# ------------------------------------------------------------------------------
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