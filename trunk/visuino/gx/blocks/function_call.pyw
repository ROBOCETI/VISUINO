#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements Function Call Blocks with full customization and
#              input/output connections.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
from __future__ import division

__all__ = ['StyleBlockFunctionCall', 'GxIoInsertionMarker', 'GxIoColliPath', \
           'GxArgLabel', 'GxBlockFunctionCall']

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

from visuino.gui import FieldInfo
from visuino.gx.bases import *
from visuino.gx.shapes import *
from visuino.gx.utils import *


class StyleBlockFunctionCall(object):
    '''
    Collection of attributes to customize all the metrics of the function
    call block. Attributes starting with 'arg_' are used for customizing
    the GxArgLabel object.
    '''
    def __init__(self):
        self.background_color = 'blue'
        self.border_color ='black'
        self.border_width = 2
        self.corner_shape = 'arc'
        self.corner_size = [6, 6]

        self.io_insertion_marker_color = '#111111'
        self.io_notch_shape = 'arc'
        self.io_notch_size = [10, 20]
        self.vf_notch_shape = 'trig/0.85'
        self.vf_notch_size = [40, 5]
        self.vf_notch_x0 =  20

        self.name_font_color = 'white'
        self.name_font_family = 'Verdana'
        self.name_font_size = 10
        self.name_padding = [10, 6]

        self.arg_background_color = 'yellow'
        self.arg_border_color = 'black'
        self.arg_border_width = 2
        self.arg_corner_size = [6, 6]
        self.arg_corner_shape = 'arc'
        self.arg_name_padding = [7, 5]
        self.arg_min_left_padd = 40
        self.arg_spacing = -2
        self.arg_font_color = 'black'
        self.arg_font_family = 'Verdana'
        self.arg_font_size = 10


class GxIoInsertionMarker(QGraphicsPathItem):
    '''
    Insertion marker meant to be shown when of the collision male/female
    IO notches.
    '''
    def __init__(self, color, notch_size, notch_shape, scene):
        ''' (QColor, QSize, str in NotchIOPath.VALID_SHAPES,
             QGraphicsScene) -> NoneType
        '''
        self._pen = QPen(QColor(color), 8, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin)

        pw = self._pen.width()
        iow, ioh = notch_size
        DY = ioh/2

        path = GxPainterPath(QPointF(iow + pw, pw))
        path.lineToInc(dy = DY)
        self.io_notch_start_y = path.currentPosition().y()
        path.connectPath(NotchPath(path.currentPosition(), QSizeF(iow, ioh),
                         notch_shape, '+j', facing='left'))
        path.lineToInc(dy = DY)

        QGraphicsPathItem.__init__(self, path, None, scene)

        self._width = iow + 2*pw
        self._height = 2*DY + 2*pw + ioh

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(self._pen)
        painter.setBrush(Qt.transparent)
        painter.drawPath(self.path())

##        painter.setPen(QPen(Qt.black))
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self.boundingRect())


class GxIoColliPath(QGraphicsPathItem):
    '''
    Path used for detecting IO notch collisions.

    Can be of the kind male ('M') or female ('F)', according with the type
    of notch associated with it. The intersection of a moving male with a
    female is collision-detected an then the insertion marker can be activated.
    '''
    _OUTLINE_COLOR = Qt.transparent

    def __init__(self, kind, io_notch_size, io_notch_start, scene=None,
                 parent=None):
        ''' ('M'/'F', QSizeF, QPointF, QGraphicsScene,
             QGraphicsItem) -> NoneType
        '''
        self._kind = str(kind).upper()
        self._pen = QPen(QColor(self._OUTLINE_COLOR))

        iow, ioh = io_notch_size.width(), io_notch_size.height()

        if self.isFemale():
            W, H = 1.3*iow, ioh/2
        else:
            W, H = 6, 4*ioh/5

        path = QPainterPath()
        path.addRect(0, 0, W, H)

        QGraphicsPathItem.__init__(self, path, parent, scene)

        self.setPos(io_notch_start.x() - W/2,
                    io_notch_start.y() + ioh/2 - H/2)

    def isMale(self):
        ''' () -> bool
        '''
        return self._kind.upper() == 'M'

    def isFemale(self):
        ''' () -> bool
        '''
        return self._kind.upper() == 'F'

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.setPen(self._pen)
        painter.setBrush(Qt.transparent)
        painter.drawPath(self.path())


class GxArgLabel(QGraphicsItem):
    '''
    Label with the name of the an argument for the function call block.

    Its basically a rectangle with the name of the argument and also with
    the IO female notch shape on the right side.

    Used and managed by GxBlockFunctionCall.
    '''
    def __init__(self, field_info, style, max_name_size=None,
                 scene=None, parent=None):
        ''' (FieldInfo, StyleBlockFunctionCall, QSize, QGraphicsScene,
             QGraphicsItem) -> NoneType
        '''
        QGraphicsItem.__init__(self, parent, scene)

        self._field_info = field_info
        self._style = style

        self._width, self._height = 200, 100
        self._old_height = None
        self._border_path = None
        self._io_colli_path = None
        self._io_notch_start = QPointF(0, 0)
        self._io_child = None
        self._name_rect = QRectF(0, 0, self._width, self._height)

        self.updateMetrics(max_name_size)

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
##        self.setFlag(QGraphicsItem.ItemClipsToShape, True)

        self.child = None

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def shape(self):
        ''' QGraphicsItem.shape() -> QPainterPath
        '''
        return self._border_path

    def pos(self):
        ''' () -> QPointF
        '''
        if self.parentItem():
            return self.parentItem().pos()
        else:
            return QGraphicsItem.pos(self)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(QColor(self._style.arg_border_color),
                            self._style.arg_border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style.arg_background_color))
        painter.drawPath(self._border_path)

        painter.setPen(QPen(QColor(self._style.arg_font_color)))
        painter.setFont(QFont(self._style.arg_font_family,
                              self._style.arg_font_size))
        painter.drawText(self._name_rect, Qt.AlignCenter,
                         self._field_info.name)

    def updateMetrics(self, max_name_size=None, io_notch_y0=None,
                      new_height=None, restore_height=False):
        ''' (QSize, number, number, bool) -> NoneType

        Change its dimensions and recreates its border path. If all the
        parameters are None/False, then the dimensions will be only enough
        to accomodate the label name. Otherwise, we have the following order
        of priority (increasing, meaning 'ignore the previous one'):

        (i) If 'max_name_size', then the size will be this value. Can be used
            to generate labels with the same width (the max. name width).
        (ii) If 'new_height', ONLY the height will be changed (to new_height).
        (iii) If 'restore_height' is True, ONLY the height will be changed,
              back to the default height (font height + vertical padding).

        The 'io_notch_y0' can be used to align input and output notches.
        By default, is centralized on the height.
        '''
        self.prepareGeometryChange()

        metrics = QFontMetrics(QFont(self._style.arg_font_family,
                                     self._style.arg_font_size))
        nw, nh = metrics.width(self._field_info.name), metrics.height()

        bw = self._style.arg_border_width/2       # border width
        iow, ioh = self._style.io_notch_size      # io notch width and height
        nhp, nvp = self._style.arg_name_padding   # name horz and vert padd
        cw, ch = self._style.arg_corner_size      # corner width and height

        if restore_height:
            self._height = max(nh + 2*nvp + 2*bw, ioh)
        elif new_height:
            self._height = new_height
        else:
            if isinstance(max_name_size, QSize):
                # its going to have a predefined size (independent of its name)
                self._width = max_name_size.width() + iow + 2*nhp + 2*bw
                self._height = max_name_size.height() + 2*nvp + 2*bw
            else:
                # the width be just enough for the name
                self._width = max(20, iow + 2*nhp + 2*bw + nw)
                # the minimum height must be the io notch height
                self._height = max(nh + 2*nvp + 2*bw, ioh)

        W, H = self._width - bw, self._height - bw

        if io_notch_y0:
            self._io_notch_start = QPointF(W, io_notch_y0)
        else:
            # the io notch is gonna be centralized on the height
            self._io_notch_start = QPointF(W, H/2 - ioh/2)

        self._name_rect = QRectF(bw, self._io_notch_start.y() + (ioh/2 - nh/2),
                                 W - iow, nh)

        self._io_colli_path = GxIoColliPath('F', QSizeF(iow, ioh),
            self._io_notch_start, self.scene(), parent=self)

        # --- creating the border path (clockwise) -------------------------

        path = GxPainterPath(QPointF(W, bw))    # start: top-right corner
        path.lineTo(self._io_notch_start)
        path.connectPath(NotchPath(path.currentPosition(), QSizeF(iow, ioh),
                         self._style.io_notch_shape, '+j', facing='left'))
        path.lineTo(W, H)
        path.lineTo(bw + cw, H)
        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.arg_corner_shape,
                                    'bottom-left', clockwise=True))
        path.lineTo(bw, bw + ch)
        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.arg_corner_shape,
                                    'top-left', clockwise=True))
        path.lineTo(W, bw)
        path.moveTo(W, H)   # end point is the bottom-right corner

        self._border_path = path

        self.update()

        if isinstance(self.parentItem(), GxBlockFunctionCall):
            self.parentItem().updateMetrics()

    def plugIn(self, child):
        ''' (GxBlockFunctionCall) -> NoneType

        Glue or plug-in the given 'child' block onto its female notch by
        creating parent-child relationship.
        Its metrics are updated to match the height of the child, and also
        the child position is also aligned properly.
        '''
        if not isinstance(child, QGraphicsItem): return

        child.setParentItem(self)

        self.updateMetrics(None, child.getIoNotchStart().y() \
                           - self._style.border_width/2,
                           child.getSize().height() + self._style.border_width)
        child.setPos(self._io_notch_start.x() - self._style.io_notch_size[0]
                     -child._MARGIN_PADDING - self._style.border_width/2,
                     -child.getIoNotchStart().y() + child._MARGIN_PADDING
                     - self._style.border_width)

    def plugOut(self, child):
        ''' () -> NoneType

        Remove the child block connected to it, if any.
        Its height is then restored.
        '''
        if not isinstance(child, QGraphicsItem): return

        pos = self.mapToScene(child.pos())
        child.setParentItem(None)
        child.setPos(pos)
        child.scene().addItem(child)
        child.updateMetrics()

        self.updateMetrics(restore_height=True)

    def cloneMe(self):
        parent = self.parentItem()
        if isinstance(parent, GxBlockFunctionCall):
            return parent.cloneMe()



class GxBlockFunctionCall(QGraphicsItem):
    '''
    Block used for generating function call statements.

    Graphically, consists of an rectangle with the name of the function and
    a vertical list of arguments, represented by GxArgLabel objects.

    If the function has a return value, then presents a female IO notch on
    the left side and none VF notches (which means that it can't be glued on
    the vertical flow off the program). Otherwise, presents no IO notch and
    a female/male VF notch respectivelly on the top/bottom edges, meaning that
    it CAN be glued on the vertical flow of the program.

    Implements mouse events with collision detection for the notches - when
    it happens, shown an insertion marker. If the user release the mouse when
    the marker is active, then the block will be glued with the other, on that
    notch/position.
    '''
    _MARGIN_PADDING = 5

    def __init__(self, name, args, return_=None, style=None,
                 scene=None, parent=None):
        ''' (str, list of FieldInfo, FieldInfo, StyleBlockFunctionCall,
             QGraphicsScene, QGraphicsItem) -> NoneType
        '''
        QGraphicsItem.__init__(self, parent, scene)

        self._name = name
        self._args = args
        self._return = return_
        self._style = style
        self.new_block = False
        self.palette = None

        self._width, self._height = 200, 100

        self._io_colli_path = None
        self._io_insert_mark = None
        self._io_parent = None
        self._io_notch_start = QPointF(0, 0)

        self._name_height = 0
        self._max_arg_width = 0
        self._args_y0 = 0
        self._args_end_y = 0
        self._args_labels = []
        if self._args:
            self._setupArgsLabels()

        self._border_path = None
        self.updateMetrics()

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
##        self.setFlag(QGraphicsItem.ItemClipsToShape, True)

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def shape(self):
        ''' QGraphicsItem.shape() -> QPainterPath
        '''
        return self._border_path

    def getSize(self):
        ''' () -> QSizeF

        Returns the size of its outline shape.
        '''
        return self.shape().boundingRect().size()

    def getIoNotchStart(self):
        ''' () -> QPointF

        Returns the starting position of the the vertical IO notch, if any.
        '''
        return QPointF(self._io_notch_start.x() - self._MARGIN_PADDING,
                       self._io_notch_start.y() - self._MARGIN_PADDING
                       + self._style.border_width/2)

    def _setupArgsLabels(self):
        ''' () -> NoneType

        Based on the self._args attribute, generates GxArgLabel objects
        for each argument. The width of all the labels is the same, based
        on the wider name of all the arguments.
        '''
        arg_name_metrics = QFontMetrics(QFont(self._style.arg_font_family,
                                              self._style.arg_font_size))
        name_height = arg_name_metrics.height()

        max_name_width = 0
        try:
            max_name_width = max(
                [arg_name_metrics.width(x.name) for x in self._args])
        except:
            raise TypeError("All elements in tuple/list of the " + \
                    "'args' parameter must be of type %s.\n" % FieldInfo)

        for x in self._args:
            new_arg = GxArgLabel(x, self._style,
                                 QSize(max_name_width, name_height),
                                 self.scene(), parent=self)
            self._args_labels.append(new_arg)

            self._max_arg_width = max(self._max_arg_width,
                                      new_arg.boundingRect().width())

    def updateMetrics(self):
        ''' () -> NoneType

        Update its dimensions and also generates the border path.
        If it has a GxArgLabel parent item, then also calls plugIn() method
        on this so it propagates the geometry changes.
        '''
        self.prepareGeometryChange()

        self._font_name = QFont(self._style.name_font_family,
                                self._style.name_font_size)
        name_metrics = QFontMetrics(self._font_name)

        bw = self._style.border_width/2
        arg_bw = self._style.arg_border_width/2

        mp = self._MARGIN_PADDING
        nw, nh = name_metrics.width(self._name), name_metrics.height()
        nhp, nvp = self._style.name_padding
        cw, ch = self._style.corner_size
        vfw, vfh = self._style.vf_notch_size
        iow, ioh = self._style.io_notch_size
        arg_min_lp = self._style.arg_min_left_padd
        arg_max_w = self._max_arg_width

        x0, y0 = mp + cw + bw, mp + bw    # start point for the path
        if self._return:
            x0 += iow

        if self._return:
            # block with return value, which means a male io notch on the
            # left side and none vf notch
            center_width = max(nw + nhp, arg_min_lp + arg_max_w)
            self._width = 2*mp + cw + iow + center_width + bw + nhp
            self._height = 2*mp + 2*ch + 2*nvp + nh
            self._name_rect = QRectF(x0 - cw + nhp + bw, y0,
                                     center_width, nh + 2*nvp)
        else:
            # block with no return value, which means only vf notches
            center_width = max(nw, arg_min_lp - nhp + arg_max_w,
                               vfw + self._style.vf_notch_x0)
            self._width = center_width + 2*mp + nhp + 2*cw
            self._height = max(ch, vfh) + 2*mp + 2*nvp + nh + ch + vfh
            self._name_rect = QRectF(x0 - cw + max(cw, nhp), y0 + vfh - 2,
                                     center_width, nh + 2*nvp)

        W, H = self._width - 2*mp, self._height - 2*mp

        # setting up all things related to arguments, including their
        # positions and height metrics for the global height
        ax = W - arg_max_w + arg_bw
        self._args_y0 = ay = self._name_rect.bottom()
        for arg in self._args_labels:
            arg_h = arg.boundingRect().height()
            arg.setPos(ax, ay)
            ay += arg_h + self._style.arg_spacing
            self._height += arg_h + self._style.arg_spacing

            if arg.child:
                arg.child.setPos(QPointF(
                    arg.pos().x() + arg.boundingRect().width() - mp - iow - bw,
                    arg.pos().y() - mp + bw))

        # --- creating the border path -------------------------------------

        path = GxPainterPath(QPointF(x0, y0))   # start: top-left corner

        shape_corner_io = self._style.corner_shape
        if self._return and self.parentItem():
            shape_corner_io = 'rect'

        if not self._return:
            path.lineToInc(dx = self._style.vf_notch_x0)
            path.connectPath(NotchPath(path.currentPosition(), QSizeF(vfw, vfh),
                         self._style.vf_notch_shape, '+i', facing='down'))

        path.lineTo(W - cw, path.currentPosition().y())

        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.corner_shape,
                                    'top-right', clockwise=True))

        if self._args:
            path.lineTo(path.currentPosition().x(),
                        self._name_rect.bottom() + 2*arg_bw)
            for arg in self._args_labels:
                path.lineToInc(dx = -iow - 2*arg_bw)
                path.lineTo(path.currentPosition().x(),
                            arg.y() + arg.boundingRect().height() - 2*arg_bw)
                path.lineToInc(dx = iow + 2*arg_bw)
                path.lineToInc(dy = self._style.arg_spacing + 4*arg_bw)
        else:
            path.lineTo(path.currentPosition().x(),
                        self._name_rect.bottom() - ch)

        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.corner_shape,
                                    'bottom-right', clockwise=True))

        if not self._return:
            path.lineTo(x0 + self._style.vf_notch_x0 + vfw,
                        path.currentPosition().y())
            path.connectPath(NotchPath(path.currentPosition(), QSizeF(vfw, vfh),
                         self._style.vf_notch_shape, '-i', facing='down'))

        path.lineTo(x0, path.currentPosition().y())
        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.corner_shape,
                                    'bottom-left', clockwise=True))

        if self._return:
            path.lineTo(path.currentPosition().x(),
                        self._name_rect.bottom() - self._name_rect.height()/2 \
                        + ioh/2)
            self._io_notch_start = QPointF(path.currentPosition().x(),
                                           path.currentPosition().y() - ioh)
            path.connectPath(NotchPath(path.currentPosition(), QSizeF(iow, ioh),
                             self._style.io_notch_shape, '-j', facing='left'))
            path.lineTo(path.currentPosition().x(), y0 + ch)
        else:
            path.lineTo(path.currentPosition().x(), y0 + max(ch, vfh))

        path.connectPath(CornerPath(path.currentPosition(), QSizeF(cw, ch),
                                    self._style.corner_shape,
                                    'top-left', clockwise=True))
        self._border_path = path

        # -------------------------------------------------------------

        if self._return:
            self._io_colli_path = GxIoColliPath('M', QSizeF(iow, ioh),
                self._io_notch_start, self.scene(), parent=self)

        self.update()

        if isinstance(self.parentItem(), GxArgLabel):
            self.parentItem().plugIn(self)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(QColor(self._style.border_color),
                            self._style.border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style.background_color))
        painter.drawPath(self._border_path)

        painter.setFont(self._font_name)
        painter.setPen(QPen(QColor(self._style.name_font_color)))
        painter.drawText(self._name_rect, Qt.AlignLeft | Qt.AlignVCenter,
                         self._name)

##        painter.setPen(QPen(QColor('black'), 1))
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self.boundingRect())

    def cloneMe(self):
        return GxBlockFunctionCall(self._name, self._args, self._return,
                                   self._style)

    def mousePressEvent(self, event):
        ''' QGraphicsItem.mousePressEvent(QGraphicsSceneMouseEvent)
            -> NoneType
        '''
        QGraphicsItem.mousePressEvent(self, event)
        self._paletteCollide()
        if self._return:
            self._ioRemove()
            self._ioCollide()

    def mouseMoveEvent(self, event):
        ''' QGraphicsItem.mouseMoveEvent(QGraphicsSceneMouseEvent)
            -> NoneType
        '''
        QGraphicsItem.mouseMoveEvent(self, event)
        self._paletteCollide()
        if self._return:
            self._ioCollide()


    def mouseReleaseEvent(self, event):
        ''' QGraphicsItem.mouseReleaseEvent(QGraphicsSceneMouseEvent)
            -> NoneType
        '''
        QGraphicsItem.mouseReleaseEvent(self, event)

        mouse_grabber = self.scene().mouseGrabberItem()
        if mouse_grabber and mouse_grabber is self:
            self.ungrabMouse()

        if [x for x in self.scene().collidingItems(self)
            if x.__class__.__name__ == 'GxPalette']:
            self.scene().removeItem(self)

        if self._return:
            self._ioConnect()

    def _cleanInsertMarker(self):
        ''' () -> NoneType

        Remove the insertion marker, if any.
        '''
        if self._io_insert_mark:
            self.scene().removeItem(self._io_insert_mark)
            self._io_insert_mark = None
            self._io_parent = None

    def _ioCollide(self):
        ''' () -> NoneType

        Checks if there is an IO collision. If so, activate the insertion
        effect. If not, just clean the insertion effect.
        '''
        if not self._return or not self._io_colli_path: return

        # retains only possible collided female notches
        colli = [x for x in self.scene().collidingItems(self._io_colli_path)
                   if isinstance(x, GxIoColliPath) and x.isFemale()]
        if colli:

            colli_path = colli[0]

            # creates the input/output insertion marker
            if not self._io_insert_mark:
                self._io_insert_mark = GxIoInsertionMarker(
                    self._style.io_insertion_marker_color,
                    self._style.io_notch_size,
                    self._style.io_notch_shape, self.scene())

                # saves the parent object for effactuation of the IO link
                self._io_parent = colli_path.parentItem()

                print("%s ---> %s" % (self._name,
                                      self._io_parent._field_info.name))

            if self._io_insert_mark:
                # keep the marker's position updated and also, upfront
                self._io_insert_mark.setPos(
                    colli_path.mapToScene(QPointF(-self._io_insert_mark.boundingRect().width()/2, colli_path.boundingRect().height()/2 + \
                        -self._io_insert_mark.boundingRect().height()/2)))

                self.scene().bringToFront(self._io_insert_mark)
        else:
            self._cleanInsertMarker()

    def _ioConnect(self):
        ''' () -> NoneType

        If there is any io_parent configured, then call plugIn() on it.
        '''
        if isinstance(self._io_parent, GxArgLabel):
            self._io_parent.plugIn(self)
            print(self.parentItem())

        self._cleanInsertMarker()

    def _ioRemove(self):
        ''' () -> NoneType

        Remove the io_parent, if any, by calling plugOut() on it.
        '''
        if isinstance(self.parentItem(), GxArgLabel):
            self.parentItem().plugOut(self)

    def _paletteCollide(self):
        ''' () -> NoneType
        '''
        if [x for x in self.scene().collidingItems(self)
            if x.__class__.__name__ == 'GxPalette']:
            if not self.new_block and self.palette:
                self.setCursor(self.palette.cursor_collide)
        else:
            self.new_block = False
            self.setCursor(QCursor(Qt.ArrowCursor))




if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Plastique'))

    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()

    my_style = StyleBlockFunctionCall()

    arg_label = GxArgLabel(FieldInfo('pin', 'int', '0|', 'edit'),
                           my_style, None, scene)
    arg_label.setFlag(QGraphicsItem.ItemIsMovable, True)

    block_digital_read = GxBlockFunctionCall('digitalRead',
        [FieldInfo('pin', 'int', '0|13', 'combobox')],
        FieldInfo('value', 'int', 'HIGH,LOW', 'combobox'),
        StyleBlockFunctionCall(), scene)
    block_digital_read.setPos(200, 300)
    block_digital_read.setFlags(QGraphicsItem.ItemIsMovable)

    block_digital_write = GxBlockFunctionCall('digitalWrite',
        [FieldInfo('pin', 'int', '0|13', 'combobox'),
         FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
        None, StyleBlockFunctionCall(), scene)
    block_digital_write.setPos(100, 100)
    block_digital_write.setFlags(QGraphicsItem.ItemIsMovable)

    block_delay = GxBlockFunctionCall('delay',
        [FieldInfo('milliseconds', 'int', '0|', 'edit')],
        None, StyleBlockFunctionCall(), scene)
    block_delay.setPos(400, 400)
    block_delay.setFlags(QGraphicsItem.ItemIsMovable)

    block_millis = GxBlockFunctionCall('millis', None,
        FieldInfo('milliseconds', 'int', '0|', 'edit'),
        StyleBlockFunctionCall(), scene)
    block_millis.setPos(400, 200)
    block_millis.setFlags(QGraphicsItem.ItemIsMovable)

    block_do_something = GxBlockFunctionCall('doSomething', None, None,
                            StyleBlockFunctionCall(), scene)
    block_do_something.setPos(300, 500)
    block_do_something.setFlags(QGraphicsItem.ItemIsMovable)

    block_pulse_in = GxBlockFunctionCall('pulseIn',
        [FieldInfo('pin', 'int', '0|', 'edit'),
         FieldInfo('value', 'int', '0|', 'edit'),
         FieldInfo('timeout', 'int', '0|', 'edit')],
        FieldInfo('pulse_lenght', 'int', '0|', 'edit'),
        StyleBlockFunctionCall(), scene)
    block_pulse_in.setPos(400, 0)
    block_pulse_in.setFlags(QGraphicsItem.ItemIsMovable)

    view = GxView(scene, parent=win)

    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())

