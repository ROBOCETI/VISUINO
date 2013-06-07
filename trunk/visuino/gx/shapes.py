#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
"""
This module provides ``QPainterPath`` based classes with configurable shapes
that can be easily connected to another existing path. 

The blocks on Visuino are meant to be fully customizable, which means that
values such as corner/notch sizes (width and lenght), shapes, etc, will be
available to the end user through global configurations - i.e., changes will
apply to all blocks on each category.

This module can also be executed on his own for testing all variations of
attributes by using a simple GUI.
"""

from __future__ import division, print_function
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from visuino.gx.bases import GxSceneBlocks, GxView
from visuino.gx.utils import GxPainterPath
from visuino.utils import vlarg

__all__ = ['CornerPath', 'NotchPath']

class CornerPath(GxPainterPath):
    '''    
    Path with the shape of a corner to be connected with other paths.

    It has the following available shapes (``self.SHAPES``):
        
        * ``'trig'``: inclinated line (diagonal of the bounding rectangle);
        * ``'arc'``: circular - can be used to create rounded rectangles;
        * ``'rect'``: regular rectangular corner;
        
    For each one of those there is 4 possible places (see ``self.PLACES``).
    Here we have an example of some ``'top-right'`` corner of ``'trig'`` shape::

        -------------#\. . . .
                     . \     .
                     .  \    .
                     .   \   .
                     .    \  .
                     .     \ .
                     .      \ 
                     . . . . @
                             |

    Considering clockwise drawing, ``#`` would be the starting point and
    ``@``, the ending (and vice-versa for counterclockwise drawing).
    PS: The dotted lines indicates the bounding rectangle for the corner.

    The easiest way to go is using the ``connect()`` static method.    
    '''
    VALID_PLACES = ('bottom-left', 'bottom-right', 'top-left', 'top-right')
    VALID_SHAPES = ('trig', 'arc', 'rect')

    def __init__(self, start_point, rect_size, shape, place, clockwise=True):
        '''        
        :param start_point: ``QPointF``
            Point from where this path will begin to draw.
        :param rect_size: ``QSizeF``
            Size of the bounding rectangle of the corner area.
            This is used to calculate the final point of the corner path.
        :param shape: ``str`` in ``self.VALID_SHAPES``
            Indicates the appearence of the corner path.
        :param place: ``str`` in ``self.VALID_PLACES``
            Indicates what kind of corner this will be on the final picture.
        :param clockwise: ``bool``
            Direction of the drawing. 
        '''
        W, H = rect_size.width(), rect_size.height()

        GxPainterPath.__init__(self, start_point)

        if shape == 'trig':

            if clockwise:
                if place == 'top-right':
                    self.lineToInc(W, H)
                elif place == 'bottom-right':
                    self.lineToInc(-W, H)
                elif place == 'bottom-left':
                    self.lineToInc(-W, -H)
                elif place == 'top-left':
                    self.lineToInc(W, -H)
            else:
                if place == 'top-left':
                    self.lineToInc(-W, H)
                elif place == 'bottom-left':
                    self.lineToInc(W, H)
                elif place == 'bottom-right':
                    self.lineToInc(W, -H)
                elif place == 'top-right':
                    self.lineToInc(-W, -H)

        elif shape == 'arc':

            if clockwise:
                if place == 'top-right':
                    self.arcTo(self.x - W, self.y, 2*W, 2*H, -270, -90)
                elif place == 'bottom-right':
                    self.arcTo(self.x - 2*W, self.y - H, 2*W, 2*H, 0, -90)
                elif place == 'bottom-left':
                    self.arcTo(self.x - W, self.y - 2*H, 2*W, 2*H, -90, -90)
                elif place == 'top-left':
                    self.arcTo(self.x, self.y - H, 2*W, 2*H, -180, -90)
            else:
                if place == 'top-left':
                    self.arcTo(self.x - W, self.y, 2*W, 2*H, 90, 90)
                elif place == 'bottom-left':
                    self.arcTo(self.x, self.y - H, 2*W, 2*H, 180, 90)
                elif place == 'bottom-right':
                    self.arcTo(self.x - W, self.y - 2*H, 2*W, 2*H, 270, 90)
                elif place == 'top-right':
                    self.arcTo(self.x - 2*W, self.y - H, 2*W, 2*H, 0, 90)

        elif shape == 'rect':

            if clockwise:
                if place == 'top-right':
                    self.lineToInc(dx = W)
                    self.lineToInc(dy = H)
                elif place == 'bottom-right':
                    self.lineToInc(dy = H)
                    self.lineToInc(dx = -W)
                elif place == 'bottom-left':
                    self.lineToInc(dx = -W)
                    self.lineToInc(dy = -H)
                elif place == 'top-left':
                    self.lineToInc(dy = -H)
                    self.lineToInc(dx = W)
            else:
                if place == 'top-left':
                    self.lineToInc(dx = -W)
                    self.lineToInc(dy = H)
                elif place == 'bottom-left':
                    self.lineToInc(dy = H)
                    self.lineToInc(dx = W)
                elif place == 'bottom-right':
                    self.lineToInc(dx = W)
                    self.lineToInc(dy = -H)
                elif place == 'top-right':
                    self.lineToInc(dy = -H)
                    self.lineToInc(dx = -W)

    @staticmethod
    def connect(path, rect_size, shape, place, clockwise=True):
        '''        
        This method provides a nice and clean way of connecting a corner
        path to another path. Here is some usage example::
            
            >>> path = QPainterPath(QPointF(0, 0))
            >>> path.lineTo(50, 0)
            >>> CornerPath.connect(path, QSizeF(50, 50), 'trig', 'top-right')
            >>> print(path.currenPosition())
            QPointF(100.0, 50.0)
        
        :param path: ``QPainterPath``
            Path on which the corner will be connected. The current position
            will be used as the starting point for the corner path.
        :param rect_size: ``QSizeF``
            Size of the bounding rectangle of the corner area.
            This is used to calculate the final point of the corner path.
        :param shape: ``str`` in `self.VALID_SHAPES`
            Indicates the appearence of the corner path.
        :param place: ``str`` in ``self.VALID_PLACES``
            Indicates what kind of corner this will be on the final picture.
        :param clockwise: ``bool``
            Direction of the drawing. 
        '''
        path.connectPath(CornerPath(path.currentPosition(), rect_size,
                                    shape, place, clockwise))


class NotchPath(GxPainterPath):
    '''
    Path with the shape of a notch to be used as "puzzle-like" connectors.

    The available shapes are:
        
        * ``'trig/%f'``: triangle or trapezium form;
        * ``'arc/%f'``: circular corners;

    The ``/%f`` part is optional on both cases, where ``%f`` must be a real 
    number between ``0.0`` (default) and ``1.0``. It determines the lenght of 
    the trapezium top side, relatively to the lenght of the trapezium base side. 
    If ``0.0``, results on a triangular form for ``'trig'`` shape, and 
    on a perfect half-circle/ellipse form for ``'arc'`` shape. If ``1.0``, then
    the lenght of the top is the same of the base, resulting on a rectangled
    notch for either shape value.

    With the ``'+i'`` and ``'-i'`` directions (horizontal shapes), it can be 
    facing ``'up'`` or ``'down'``; similarly, with the ``'+j'`` and ``'-j'``
    directions (vertical shapes), it can be facing ``'left'`` or ``'right'``.

    The following notch was constructed with ``'-j'`` direction and facing 
    ``'left'``::

                           |
                           @     +
                          /      |
                        /        |
                      /          |
               +     |           |
               |     |           |
          top  |     |           |  base
               +     |           |
                      \          |
                        \        |
                          \      |
                           #     +
                           |

    Here we have a ``'trig/0.4'`` shape, where ``#`` is the starting point 
    and ``@`` the ending. The lenght of the top is ``0.4`` times the lenght 
    of the base.
    '''
    VALID_SHAPES = ('trig/%f', 'arc/%f')
    VALID_DIRECTIONS = ('+i',   # horizontal to the right
                        '-i',   # horizontal to the left
                        '+j',   # vertical down right
                        '-j')   # vertical up right                        
    VALID_FACING_SIDES = ('up', 'down', 'left', 'right')

    def __init__(self, start_point, rect_size, shape, direction, facing):
        '''
        :param start_point: ``QPointF``
            Point from where this path will begin to draw.
        :param rect_size: ``QSizeF``
            Size of the bounding rectangle for this path.
        :param shape: ``str`` in ``self.VALID_SHAPES``
            Shape of the notch.
        :param direction: ``str`` in ``self.VALID_DIRECTIONS``
            Indicates the direction of the drawing (using vectorial notation).
        :param facing: ``str`` in ``self.VALID_FACING_SIDES``
            Indicates to which side the top of the trapezium is going to be
            pointing on.
        '''
        if direction[1] == 'j':
            facing = vlarg('facing', facing.lower(), str,
                                  ('left', 'right'))
        else:
            facing = vlarg('facing', facing.lower(), str,
                                  ('up', 'down'))

        valid_shapes = [x.split('/')[0] for x in self.VALID_SHAPES]

        tf = 0.0    # top factor
        given_shape = shape
        shape = vlarg('shape', shape, str).strip()
        if not shape.count('/'):
            shape = vlarg('shape', shape, str, valid_shapes)
        else:
            sp = shape.split('/')
            shape = vlarg('shape', sp[0].strip(), str, valid_shapes)
            try:
                tf = float(sp[1]) if sp[1].strip() != '' else 0.0
            except:
                raise ValueError("Argument 'shape' must have the format" +\
                    " '%%s/%%f'. Was given '%s'." % given_shape)
            tf = vlarg('shape', tf, float, range_='0.0|1.0')

        # setting up some useful dimensions
        W, H = rect_size.width(), rect_size.height()

        if direction[1] == 'j':
            tl = tf * H             # top lenght   (for vertical)
            ts = (H - tl)/2         # top spacing  (for vertical)
        else:
            tl = tf * W             # top lenght   (for horizontal)
            ts = (W - tl)/2         # top spacing  (for horizontal)

        QPainterPath.__init__(self, start_point)

        if shape == 'trig':

            if direction == '+j':
                if facing == 'left':
                    self.lineToInc(-W, ts)
                    self.lineToInc(dy = tl)
                    self.lineToInc(W, ts)
                elif facing == 'right':
                    self.lineToInc(W, ts)
                    self.lineToInc(dy = tl)
                    self.lineToInc(-W, ts)
            elif direction == '-j':
                if facing == 'left':
                    self.lineToInc(-W, -ts)
                    self.lineToInc(dy = -tl)
                    self.lineToInc(W, -ts)
                elif facing == 'right':
                    self.lineToInc(W, -ts)
                    self.lineToInc(dy = -tl)
                    self.lineToInc(-W, -ts)
            elif direction == '+i':
                if facing == 'up':
                    self.lineToInc(ts, -H)
                    self.lineToInc(dx = tl)
                    self.lineToInc(ts, H)
                elif facing == 'down':
                    self.lineToInc(ts, H)
                    self.lineToInc(dx = tl)
                    self.lineToInc(ts, -H)
            elif direction == '-i':
                if facing == 'up':
                    self.lineToInc(-ts, -H)
                    self.lineToInc(dx = -tl)
                    self.lineToInc(-ts, H)
                elif facing == 'down':
                    self.lineToInc(-ts, H)
                    self.lineToInc(dx = -tl)
                    self.lineToInc(-ts, -H)

        elif shape == 'arc':

            if direction == '+j':
                if facing == 'left':
                    self.arcTo(self.x - W, self.y, 2*W, 2*ts, 90, 90)
                    self.lineToInc(dy = tl)
                    self.arcTo(self.x, self.y - ts, 2*W, 2*ts, 180, 90)
                elif facing == 'right':
                    self.arcTo(self.x - W, self.y, 2*W, 2*ts, 90, -90)
                    self.lineToInc(dy = tl)
                    self.arcTo(self.x - 2*W, self.y - ts, 2*W, 2*ts, 0, -90)
            elif direction == '-j':
                if facing == 'left':
                    self.arcTo(self.x - W, self.y - 2*ts, 2*W, 2*ts, -90, -90)
                    self.lineToInc(dy = -tl)
                    self.arcTo(self.x, self.y - ts, 2*W, 2*ts, 180, -90)
                elif facing == 'right':
                    self.arcTo(self.x - W, self.y - 2*ts, 2*W, 2*ts, -90, 90)
                    self.lineToInc(dy = -tl)
                    self.arcTo(self.x - 2*W, self.y - ts, 2*W, 2*ts, 0, 90)
            elif direction == '+i':
                if facing == 'up':
                    self.arcTo(self.x, self.y - H, 2*ts, 2*H, 180, -90)
                    self.lineToInc(dx = tl)
                    self.arcTo(self.x - ts, self.y, 2*ts, 2*H, 90, -90)
                elif facing == 'down':
                    self.arcTo(self.x, self.y - H, 2*ts, 2*H, 180, 90)
                    self.lineToInc(dx = tl)
                    self.arcTo(self.x - ts, self.y - 2*H, 2*ts, 2*H, -90, 90)
            elif direction == '-i':
                if facing == 'up':
                    self.arcTo(self.x - 2*ts, self.y - H, 2*ts, 2*H, 0, 90)
                    self.lineToInc(dx = -tl)
                    self.arcTo(self.x - ts, self.y, 2*ts, 2*H, 90, 90)
                elif facing == 'down':
                    self.arcTo(self.x - 2*ts, self.y - H, 2*ts, 2*H, 0, -90)
                    self.lineToInc(dx = -tl)
                    self.arcTo(self.x - ts, self.y - 2*H, 2*ts, 2*H, -90, -90)

    @staticmethod
    def connect(path, rect_size, shape, direction, facing):
        '''
        This method provides a nice and clean way of connecting a notch
        path to another path. Here is some usage example::
            
            >>> path = QPainterPath(QPointF(0, 0))
            >>> path.lineTo(50, 0)
            >>> NotchPath.connect(path, QSizeF(100, 50), 'trig/0.8', 'i+', 'down')
            >>> print(path.currenPosition())
            QPointF(150.0, 0.0)
        
        :param path: ``QPainterPath``
            Path on which the notch will be connected. The current position
            will be used as the starting point for the notch path.
        :param rect_size: ``QSizeF``
            Size of the bounding rectangle for this path.
        :param shape: ``str`` in ``self.VALID_SHAPES``
            Shape of the notch.
        :param direction: ``str`` in ``self.VALID_DIRECTIONS``
            Indicates the direction of the drawing (using vectorial notation).
        :param facing: ``str`` in ``self.VALID_FACING_SIDES``
            Indicates to which side the top of the trapezium is going to be
            pointing on.
        '''
        path.connectPath(NotchPath(path.currentPosition(),
                                   rect_size, shape, direction, facing))

class GxExamplePaths(QGraphicsItem):
    '''
    Combines all 4 CornerPath positions and the 4 NotchPath directions
    on a single path. Can be tweaked, for purposes of demonstration.
    '''
    DEFAULT_SIZE = (200, 100)       # (width, height) of the graphics item

    BORDER_WIDTH = 3
    BORDER_COLOR = 'black'              # for QColor(...)
    BACKGROUND_COLOR = 'lightgreen'     # for QColor(...)

    def __init__(self, scene=None, parent=None):
        ''' (QGraphicsScene, QGraphicsItem) -> NoneType
        '''
        QGraphicsItem.__init__(self, parent, scene)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self._width, self._height = self.DEFAULT_SIZE

        self.corner_size = {'tl': QSizeF(50, 50),
                            'tr': QSizeF(50, 50),
                            'bl': QSizeF(50, 50),
                            'br': QSizeF(50, 50)}
        self.corner_shape = {'tl': 'arc', 'tr': 'arc',
                             'bl': 'arc', 'br': 'arc'}

        self.notch_data = {'top': {'shape': 'arc', 'base_fc': 0.7,
                                   'size': QSizeF(200, 50), 'facing': 'up'},
                           'bottom': {'shape': 'arc', 'base_fc': 0.7,
                                   'size': QSizeF(200, 50), 'facing': 'up'},
                           'left': {'shape': 'arc', 'base_fc': 0.7,
                                   'size': QSizeF(50, 150), 'facing': 'right'},
                           'right': {'shape': 'arc', 'base_fc': 0.7,
                                   'size': QSizeF(50, 150), 'facing': 'right'}}

        self.border_path = None
        self.updateMetrics()

        self.setPos(50, 150)

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(-50, -50, self._width + 400, self._height + 400)

    def setNotchData(self, notch, data, value):
        ''' (str in ['top', 'bottom', 'left', 'right],
             str in ['shape', 'base_fc', 'size', 'facing'],
             various) -> NoneType
        '''
        self.notch_data[notch][data] = value
        self.updateMetrics()

    def getNotch(self, path, notch, direction):
        ''' (str in ['top', 'bottom', 'left', 'right]) -> NotchPath
        '''
        return NotchPath(path.currentPosition(),
            self.notch_data[notch]['size'], self.notch_data[notch]['shape'] \
            + '/' + str(self.notch_data[notch]['base_fc']),
            direction, self.notch_data[notch]['facing'])

    def updateMetrics(self):
        ''' () -> NoneType

        Update its border path based on its size, by properly connecting
        the notch and corner paths.
        '''
        self.prepareGeometryChange()

        path = GxPainterPath(QPointF(100, 0))

        path.lineToInc(dx = 100)
        path.connectPath(self.getNotch(path, 'top', '+i'))
        path.lineToInc(dx = 100)
        path.connectPath(CornerPath(path.currentPosition(), self.corner_size['tr'],
                                    self.corner_shape['tr'], 'top-right'))
        path.lineToInc(dy = 50)
        path.connectPath(self.getNotch(path, 'right', '+j'))
        path.lineToInc(dy = 50)
        path.connectPath(CornerPath(path.currentPosition(), self.corner_size['br'],
                                    self.corner_shape['br'], 'bottom-right'))
        path.lineToInc(dx = -100)
        path.connectPath(self.getNotch(path, 'bottom', '-i'))
        path.lineToInc(dx = -100)

        path.connectPath(CornerPath(path.currentPosition(), self.corner_size['bl'],
                                    self.corner_shape['bl'], 'bottom-left'))
        path.lineToInc(dy = -50)
        path.connectPath(self.getNotch(path, 'left', '-j'))
        path.lineToInc(dy = -50)
        path.connectPath(CornerPath(path.currentPosition(), self.corner_size['tl'],
                                    self.corner_shape['tl'], 'top-left'))

        self.border_path = path

        self._width = path.boundingRect().width()
        self._height = path.boundingRect().height()
        self.update()

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)
        pen = QPen(QColor(self.BORDER_COLOR), self.BORDER_WIDTH,
                         Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QColor(self.BACKGROUND_COLOR))
        painter.drawPath(self.border_path)


class ExampleMainWindow(QMainWindow):
    POSITIONS = ('top', 'bottom', 'left', 'right')
    DIMENSIONS = ('w', 'h')
    CORNER_PLACES = ('tl', 'tr', 'bl', 'br')

    def __init__(self, parent=None):
        ''' (QWidget) -> NoneType
        '''
        QMainWindow.__init__(self, parent)

        self.scene = GxSceneBlocks()
        self.scene.setSceneRect(0, 0, 800, 800)
        self.gx_example_path = GxExamplePaths(self.scene)

        self.initUI()

    def initUI(self):
        ''' () -> NoneType
        '''

        # --- corner settings ----------------------------------------------

        self.wg_area_corners = QWidget(self)

        self.wg_gbx_bl_corner = self.setupCornerGroupBox(' Bottom-Left ',
            'bl', 'tl', 'br', self.wg_area_corners)

        self.wg_gbx_br_corner = self.setupCornerGroupBox(' Bottom-Right ',
            'br', 'tr', 'bl', self.wg_area_corners)

        self.wg_gbx_tl_corner = self.setupCornerGroupBox(' Top-Left ',
            'tl', 'bl', 'tr', self.wg_area_corners)

        self.wg_gbx_tr_corner = self.setupCornerGroupBox(' Top-Right ',
            'tr', 'br', 'tl', self.wg_area_corners)

        vl = QVBoxLayout()
        vl.addWidget(self.wg_gbx_bl_corner)
        vl.addWidget(self.wg_gbx_br_corner)
        vl.addWidget(self.wg_gbx_tl_corner)
        vl.addWidget(self.wg_gbx_tr_corner)
        self.wg_area_corners.setLayout(vl)

        # ---- notch settings ----------------------------------------------

        self.wg_area_notch = QWidget(self)

        self.wg_gbx_top_notch = self.setupNotchGroupBox(' Top ',
            'top', 'bottom', None, self.wg_area_notch)

        self.wg_gbx_bottom_notch = self.setupNotchGroupBox(' Bottom ',
            'bottom', 'top', None, self.wg_area_notch)

        self.wg_gbx_left_notch = self.setupNotchGroupBox(' Left ',
            'left', None, 'right', self.wg_area_notch)

        self.wg_gbx_right_notch = self.setupNotchGroupBox(' Right ',
            'right', None, 'left', self.wg_area_notch)

        vl = QVBoxLayout()
        vl.addWidget(self.wg_gbx_top_notch)
        vl.addWidget(self.wg_gbx_bottom_notch)
        vl.addWidget(self.wg_gbx_left_notch)
        vl.addWidget(self.wg_gbx_right_notch)
        self.wg_area_notch.setLayout(vl)

        # --------------------------------------------------------------

        self.wg_area_win = QWidget(self)

        self.wg_view = GxView(self.scene, parent=self)

        self.wg_tab_command = QTabWidget(self)
        self.wg_tab_command.addTab(self.wg_area_corners, 'Corners')
        self.wg_tab_command.addTab(self.wg_area_notch, 'Notch')
        self.wg_tab_command.setFixedWidth(200)

        hl = QHBoxLayout()
        hl.addWidget(self.wg_view)
        hl.addWidget(self.wg_tab_command, 200)
        self.wg_area_win.setLayout(hl)

        self.setGeometry(200, 50, 1000, 550)
        self.setCentralWidget(self.wg_area_win)

    def setupNotchGroupBox(self, title, notch, follow_w, follow_h, parent):
        ''' (str, str in self.POSITIONS, QWidget) -> QGroupBox
        '''
        groupbox = QGroupBox(title, parent)

        combobox_shape = QComboBox(parent)
        combobox_shape.addItems(['trig', 'arc'])
        combobox_shape.setCurrentIndex(combobox_shape.findText(
            self.gx_example_path.notch_data[notch]['shape']))
        self.connect(combobox_shape, SIGNAL('currentIndexChanged(int)'),
            lambda: self.gx_example_path.setNotchData(notch, 'shape',
                    combobox_shape.currentText()))

        slider_base = QSlider(parent)
        slider_base.setOrientation(Qt.Horizontal)
        slider_base.setRange(0, 100)
        slider_base.setSingleStep(1)
        slider_base.setValue(
            self.gx_example_path.notch_data[notch]['base_fc'] * 100)
        self.connect(slider_base, SIGNAL('valueChanged(int)'),
            lambda: self.gx_example_path.setNotchData(notch, 'base_fc',
                    slider_base.value()/100))

        combobox_facing = QComboBox(parent)
        combobox_facing.addItems(['up', 'down'] if notch in ('top', 'bottom')
                                                else ['left', 'right'])
        combobox_facing.setCurrentIndex(combobox_facing.findText(
            self.gx_example_path.notch_data[notch]['facing']))
        self.connect(combobox_facing, SIGNAL('currentIndexChanged(int)'),
            lambda: self.gx_example_path.setNotchData(notch, 'facing',
                    combobox_facing.currentText()))

        slider_width = QSlider()
        slider_width.setOrientation(Qt.Horizontal)
        if notch in ('top', 'bottom'):
            slider_width.setRange(0, 300)
        else:
            slider_width.setRange(0, 100)
        slider_width.setSingleStep(1)
        slider_width.setValue(
            int(self.gx_example_path.notch_data[notch]['size'].width()))
        self.connect(slider_width, SIGNAL('valueChanged(int)'),
            lambda: self.setNotchSize('w', notch, follow_w,
                    slider_width))

        slider_height = QSlider()
        slider_height.setOrientation(Qt.Horizontal)
        if notch in ('top', 'bottom'):
            slider_height.setRange(0, 100)
        else:
            slider_height.setRange(0, 300)
        slider_height.setSingleStep(1)
        slider_height.setValue(
            int(self.gx_example_path.notch_data[notch]['size'].height()))
        self.connect(slider_height, SIGNAL('valueChanged(int)'),
            lambda: self.setNotchSize('h', notch, follow_h,
                    slider_height))

        setattr(self, 'wg_slider_%s_notch_size_w' % notch, slider_width)
        setattr(self, 'wg_slider_%s_notch_size_h' % notch, slider_height)

        gl = QGridLayout()
        gl.addWidget(QLabel('shape', parent), 0, 0)
        gl.addWidget(combobox_shape, 0, 1)
        gl.addWidget(QLabel('base', parent), 1, 0)
        gl.addWidget(slider_base, 1, 1)
        gl.addWidget(QLabel('facing', parent), 2, 0)
        gl.addWidget(combobox_facing, 2, 1)
        gl.addWidget(QLabel('width', parent), 3, 0)
        gl.addWidget(slider_width, 3, 1)
        gl.addWidget(QLabel('height', parent), 4, 0)
        gl.addWidget(slider_height, 4, 1)
        groupbox.setLayout(gl)

        return groupbox

    def setNotchSize(self, dimension, notch, follow_notch, slider):
        ''' (str in self.DIMENSIONS, str in self.DIRECTIONS,
             float) -> NoneType
        '''
        value = slider.value()

        if dimension == 'w':
            new_size = QSizeF(value, self.gx_example_path.\
                              notch_data[notch]['size'].height())
        else:
            new_size = QSizeF(
                self.gx_example_path.notch_data[notch]['size'].width(), value)

        self.gx_example_path.notch_data[notch]['size'] = new_size

        if follow_notch is not None:
            if dimension == 'w':
                new_follow_size = QSizeF(value, self.gx_example_path.\
                                  notch_data[follow_notch]['size'].height())
            else:
                new_follow_size = QSizeF(self.gx_example_path.notch_data \
                                         [follow_notch]['size'].width(), value)

            self.gx_example_path.notch_data[follow_notch]['size'] = \
                new_follow_size
            getattr(self, 'wg_slider_%s_notch_size_%s' % \
                (follow_notch, dimension)).setValue(value)

        self.gx_example_path.updateMetrics()

    def setupCornerGroupBox(self, title, corner, follow_w, follow_h, parent):
        ''' (str, str in self.CORNER_PLACES, QWidget) -> QGroupBox
        '''
        corner = corner.lower()
        follow_w, follow_h = follow_w.lower(), follow_h.lower()

        groupbox = QGroupBox(title, parent)

        combobox = QComboBox(parent)
        combobox.addItems(['trig', 'arc', 'rect'])
        combobox.setCurrentIndex(1)
        self.connect(combobox, SIGNAL('currentIndexChanged(int)'),
            lambda: self.setCornerShape(combobox, corner))

        slider_width = self.setupCornerSlider('w', corner, follow_w, parent)
        slider_height = self.setupCornerSlider('h', corner, follow_h, parent)

        setattr(self, 'wg_cbx_%s_corner_shape' % corner, combobox)
        setattr(self, 'wg_slider_%s_corner_size_w' % corner, slider_width)
        setattr(self, 'wg_slider_%s_corner_size_h' % corner, slider_height)

        gl = QGridLayout()
        gl.addWidget(QLabel('shape', parent), 0, 0)
        gl.addWidget(combobox, 0, 1)
        gl.addWidget(QLabel('width', parent), 1, 0)
        gl.addWidget(slider_width, 1, 1)
        gl.addWidget(QLabel('height', parent), 2, 0)
        gl.addWidget(slider_height, 2, 1)
        groupbox.setLayout(gl)

        return groupbox

    def setupCornerSlider(self, dimension, corner, follow_corner, parent):
        ''' (str in self.DIMENSIONS, str in self.CORNER_PLACES,
             str in self.CORNER_PLACES, QWidget) -> QSlider
        '''
        slider = QSlider(parent)
        slider.setOrientation(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setSingleStep(1)
        slider.setValue(50)
        self.connect(slider, SIGNAL('valueChanged(int)'),
            lambda: self.setCornerSize(slider, dimension[:], corner,
                                       follow_corner))
        return slider

    def setCornerShape(self, cbx, corner):
        ''' (QComboBox, str in self.CORNER_PLACES) -> NoneType
        '''
        self.gx_example_path.corner_shape[corner] = cbx.currentText()
        self.gx_example_path.updateMetrics()

    def setCornerSize(self, slider, dimension, corner, follow_corner):
        ''' (QSlider, str in self.DIMENSIONS, str in self.CORNER_PLACES,
             str in self.CORNER_PLACES) -> NoneType
        '''

        value = slider.value()
        if dimension == 'w':
            self.gx_example_path.corner_size[corner].setWidth(value)
            self.gx_example_path.corner_size[follow_corner].setWidth(value)
        else:
            self.gx_example_path.corner_size[corner].setHeight(value)
            self.gx_example_path.corner_size[follow_corner].setHeight(value)
        getattr(self, 'wg_slider_%s_corner_size_%s' % \
                (follow_corner, dimension)).setValue(value)
        self.gx_example_path.updateMetrics()


def _AppExampleShapes():
    ''' () -> NoneType

    Executes some simple example PyQt application that uses the resources
    of this module.
    '''
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    window = ExampleMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    _AppExampleShapes()
