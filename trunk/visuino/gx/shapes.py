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

__all__ = ['NotchIOPath', 'NotchVFPath', 'CornerPath', 'GxShapeNotchLeft']

class GxShapeNotchLeft(QGraphicsItem):

    _NOTCH_SIZE = (20, 40)

    _BORDER_WIDTH = 2
    _BORDER_COLOR = 'black'

    _CORNER_SIZE = (8, 8)
    _CORNER_STYLE = 'arc'

    def __init__(self, notch='rect', scene=None, parent=None):
        """
        :notch: str in ('rect', 'trig', 'arg')
        """
        QGraphicsItem.__init__(self, parent, scene)

        self._width, self._height = 200, 100
        self._bk_color = 'yellow'

        self._notch = notch

    def boundingRect(self):
        return QRectF(-20, -20, self._width + 30, self._height + 30)

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)

#        grad = QLinearGradient(0, 0, self._width, self._height)
#        grad.setColorAt(0.0, QColor(30, 30, 30))
#        grad.setColorAt(1.0, QColor(100, 100, 100))

        pen = QPen(QColor(self._BORDER_COLOR), self._BORDER_WIDTH,
                   Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        painter.setBrush(QColor(self._bk_color))

        W = self._width - self._BORDER_WIDTH/2
        H = self._height - self._BORDER_WIDTH/2
        sw, sh = self._NOTCH_SIZE            # slot dimensions
        cw, ch = self._CORNER_SIZE          # corner dimensions

        x0 = sw + self._BORDER_WIDTH/2
        y0 = ch + self._BORDER_WIDTH/2

        path = QPainterPath(QPointF(x0, y0))
        path.lineTo(x0, H/2 - sh/2)

        path.connectPath(NotchIOPath(path.currentPosition(),
                                     size=self._NOTCH_SIZE,
                                     shape=self._notch, clockwise=False))
        path.lineTo(x0, H - ch)

        path.connectPath(self._getCornerPath('bottom-left', QPointF(x0, H)))
        path.lineTo(W - cw, H)
        path.connectPath(self._getCornerPath('bottom-right', QPointF(W, H)))
        path.lineTo(W, y0)
        path.connectPath(self._getCornerPath('top-right', QPointF(W, y0 - ch)))
        path.lineTo(x0 + ch, y0 - ch)
        path.connectPath(self._getCornerPath('top-left', QPointF(x0, y0 - ch)))

        painter.drawPath(path)

    def _getCornerPath(self, place, origin):
        return CornerPath(origin, place, QSizeF(self._CORNER_SIZE[0],
                                                self._CORNER_SIZE[1]),
                          self._CORNER_STYLE)


class CornerPath(QPainterPath):
    """
    Path for nice and easy corner drawings, with various shapes supporting.

    Just give it the corner point of the destination shape, and then it
    will figures out the relative dimensions and creates the path. Then
    you can append this with the destination path.
    """
    def __init__(self, origin, place, size, style='rect', clockwise=False):
        """
        :origin: QPointF(). Corner point.
        :place: str in ('bottom-left', 'bottom-right', 'top-left', 'top-right')
        :size: QSizeF()
        :style: str in ['rect', 'arc', 'trig']
        :clockwise: True.
        """
        W, H = size.width(), size.height()      # corner size dimensions
        x0, y0 = 0, 0                           # starting point

        place = place.lower()
        # decides the starting point based on the given origin and place
        if clockwise:

            if place == 'bottom-left':
                x0, y0 = origin.x() + W, origin.y()
            elif place == 'top-left':
                x0, y0 = origin.x(), origin.y() + H
            elif place == 'top-right':
                x0, y0 = origin.x() - W, origin.y()
            elif place == 'bottom-right':
                x0, y0 = origin.x(), origin.y() - H

        else:   # counterclockwise

            if place == 'bottom-left':
                x0, y0 = origin.x(), origin.y() - H
            elif place == 'bottom-right':
                x0, y0 = origin.x() - W, origin.y()
            elif place == 'top-right':
                x0, y0 = origin.x(), origin.y() + H
            elif place == 'top-left':
                x0, y0 = origin.x() + W, origin.y()

        QPainterPath.__init__(self, QPointF(x0, y0))

        if style == 'rect':

            if clockwise:

                if place == 'bottom-left':
                    self.lineTo(x0 - W, y0)
                    self.lineTo(x0 - W, y0 - H)
                elif place == 'top-left':
                    self.lineTo(x0, y0 - H)
                    self.lineTo(x0 + W, y0 - H)
                elif place == 'top-right':
                    self.lineTo(x0 + W, y0)
                    self.lineTo(x0 + W, y0 + H)
                elif place == 'bottom-right':
                    self.lineTo(x0, y0 + H)
                    self.lineTo(x0 - W, y0 + H)

            else:

                if place == 'bottom-left':
                    self.lineTo(x0, y0 + H)
                    self.lineTo(x0 + W, y0 + H)
                elif place == 'bottom-right':
                    self.lineTo(x0 + W, y0)
                    self.lineTo(x0 + W, y0 - H)
                elif place == 'top-right':
                    self.lineTo(x0, y0 - H)
                    self.lineTo(x0 - W, y0 - H)
                elif place == 'top-left':
                    self.lineTo(x0 - W, y0)
                    self.lineTo(x0 - W, y0 + H)

        elif style == 'trig':

            if clockwise:

                if place == 'bottom-right':
                    self.lineTo(x0 - W, y0 + H)
                elif place == 'bottom-left':
                    self.lineTo(x0 - W, y0 - H)
                elif place == 'top-left':
                    self.lineTo(x0 + W, y0 - W)
                elif place == 'top-right':
                    self.lineTo(x0 + W, y0 + H)

            else:

                if place == 'top-right':
                    self.lineTo(x0 - W, y0 - H)
                elif place == 'top-left':
                    self.lineTo(x0 - W, y0 + H)
                elif place == 'bottom-left':
                    self.lineTo(x0 + W, y0 + H)
                elif place == 'bottom-right':
                    self.lineTo(x0 + W, y0 - W)

        elif style == 'arc':

            if clockwise:

                if place == 'bottom-right':
                    self.arcTo(x0 - 2*W, y0 - H, 2*W, 2*H, 0, -90)
                elif place == 'bottom-left':
                    self.arcTo(x0 - W, y0 - 2*H, 2*W, 2*H, -90, -90)
                elif place == 'top-left':
                    self.arcTo(x0, y0 - H, 2*W, 2*H, -180, -90)
                elif place == 'top-right':
                    self.arcTo(x0 - W, y0, 2*W, 2*H, -270, -90)

            else:

                if place == 'top-right':
                    self.arcTo(x0 - 2*W, y0 - H, 2*W, 2*H, 0, 90)
                elif place == 'top-left':
                    self.arcTo(x0 - W, y0, 2*W, 2*H, 90, 90)
                elif place == 'bottom-left':
                    self.arcTo(x0, y0 - H, 2*W, 2*H, 180, 90)
                elif place == 'bottom-right':
                    self.arcTo(x0 - W, y0 - 2*H, 2*W, 2*H, 270, 90)


class NotchIOPath(QPainterPath):
    """
    Input/output notch path, used to connect an output from function call
    or expression result to an input of the same shape, on some argument
    label or expression field, for instance.

    This class provides a painter path with shapes for left/right puzzle-
    like slots, which uses relative points so it can be easily connected
    to another path.
    """
    def __init__(self, start_point=None, size=(50, 100), shape='trig',
                 clockwise=True):
        """
        :start_point: QPointF().
        :size: tuple/list of 2 int. Format: (width, height).
        :shape: str in ['trig', 'rect', 'arc'].
        """
        if not isinstance(start_point, QPointF):
            start_point = QPointF(0, 0)
        if not isinstance(size, (tuple, list)) or len(size) != 2:
            size = (50, 100)

        DX, DY = size

        QPainterPath.__init__(self, start_point)
        x0, y0 = start_point.x(), start_point.y()

        if clockwise:
            if shape == 'trig':
                self.lineTo(x0 - DX, y0 - DY/2)
                self.lineTo(x0, y0 - DY)
            elif shape == 'arc':
                self.arcTo(x0 - DX, y0 - DY, 2*DX, DY, -90, -180)
        else:
            if shape == 'trig':
                self.lineTo(x0 - DX, y0 + DY/2)
                self.lineTo(x0, y0 + DY)
            elif shape == 'rect':
                self.lineTo(x0 - DX, y0)
                self.lineTo(x0 - DX, y0 + DY)
                self.lineTo(x0, y0 + DY)
            elif shape == 'arc':
                self.arcTo(x0 - DX, y0, 2*DX, DY, 90, 180)


class NotchVFPath(QPainterPath):
    """
    Vertical flow notch path, used to "glue" blocks vertically to compose
    the program flow. Function call with no return and assignments blocks
    are the ones to have this notch.

    This class provides a painter path with shapes for left/right puzzle-
    like slots, which uses relative points so it can be easily connected
    to another path.
    """
    def __init__(self, start_point=None, size=(200, 50), shape='trig/0.8',
                 clockwise=False):
        """
        :start_point: QPointF().
        :size: tuple/list of 2 int. Format: (width, height).
        :shape: str in ['trig-%f', 'rect', 'arc'].
        """
        if not isinstance(start_point, QPointF):
            start_point = QPointF(0, 0)
        if not isinstance(size, (tuple, list)) or len(size) != 2:
            size = (200, 50)

        W, H = size
        QPainterPath.__init__(self, start_point)
        x0, y0 = start_point.x(), start_point.y()

        if shape[:4] == 'trig':

            try:
                base_fraction = float(shape.split('/')[1])
            except:
                raise TypeError("Invalid format for 'shape' argument string.")

            base_start = W - (base_fraction * W)

            if clockwise:
                self.lineTo(x0 - base_start, y0 + H)
                self.lineTo(x0 - (W - base_start), y0 + H)
                self.lineTo(x0 - W, y0)
            else:
                self.lineTo(x0 + base_start, y0 + H)
                self.lineTo(x0 + (W - base_start), y0 + H)
                self.lineTo(x0 + W, y0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()

    field = GxShapeNotchLeft(scene=scene)
    field.setPos(300, 300)
    field.setFlags(QGraphicsItem.ItemIsMovable |
                   QGraphicsItem.ItemIsSelectable)

    rect = scene.addRect(400, 100, 200, 50)

    my_path = QPainterPath()
    my_path.connectPath(NotchIOPath(QPointF(200, 100), clockwise=False))
    my_path.connectPath(NotchIOPath(my_path.currentPosition(), shape='rect',
        clockwise=False))
    my_path.connectPath(NotchIOPath(my_path.currentPosition(), shape='arc',
        clockwise=False))

    pen = QPen(QColor('black'), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    path_item = scene.addPath(my_path, pen)
    path_item.setFlags(QGraphicsItem.ItemIsMovable |
                       QGraphicsItem.ItemIsSelectable)

#    scene.addPath(CornerPath(QPointF(400, 100), 'top-left',
#                             QSizeF(100, 100), 'rect'), pen)

    notch_vf = NotchVFPath(QPointF(400, 100), shape='trig/0.85')
    scene.addPath(notch_vf, pen)

    view = GxView(scene, parent=win)

    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())
