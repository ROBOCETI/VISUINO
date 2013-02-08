# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 01:55:27 2013

@author: Nelso
"""

from __future__ import division
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *
from PyQt4.QtOpenGL import QGLWidget

##from PySide.QtGui import *
##from PySide.QtCore import *
##from PySide.QtSvg import *

from bases import *
from field_info import *
from shapes import *
from utils import *

class StyleBlockFunctionCall(object):
    def __init__(self, **kwargs):
        self._createKwAttr(kwargs, 'name_font_family', 'Verdana')
        self._createKwAttr(kwargs, 'name_font_size', 10)
        self._createKwAttr(kwargs, 'name_font_color', 'white')

        self._createKwAttr(kwargs, 'background_color', 'blue')
        self._createKwAttr(kwargs, 'border_color', 'black')
        self._createKwAttr(kwargs, 'border_width', 2)

        self._createKwAttr(kwargs, 'arg_font_family', 'Verdana')
        self._createKwAttr(kwargs, 'arg_font_size', 9)
        self._createKwAttr(kwargs, 'arg_font_color', 'black')

        self._createKwAttr(kwargs, 'arg_background_color', 'yellow')
        self._createKwAttr(kwargs, 'arg_border_color', 'black')
        self._createKwAttr(kwargs, 'arg_border_width', 2)

    def _createKwAttr(self, kwargs, attr_name, default_value):
        setattr(self, attr_name, kwargs.get(attr_name, default_value))

class GxInsertMarkNotchIO(QGraphicsPathItem):

    _DY = 10

    def __init__(self, color, notch_size, notch_shape, scene):

        self.pen = QPen(QColor(color), 8, Qt.SolidLine, Qt.RoundCap,
            Qt.RoundJoin)

        pw = self.pen.width()
        iow, ioh = notch_size

        path = GxPainterPath(QPointF(iow + pw, pw))
        path.lineToInc(dy = self._DY)
        path.connectPath(NotchIOPath(path.currentPosition(),
                                     notch_size, notch_shape , False))
        path.lineToInc(dy = self._DY)

        QGraphicsPathItem.__init__(self, path, None, scene)

        self._width = iow + 2*pw
        self._height = 2*self._DY + 2*pw + ioh

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)
        painter.setPen(self.pen)
        painter.drawPath(self.path())


class GxPathColliIoNotch(QGraphicsPathItem):
    # path line color (set None for transparent)
    _COLOR = None

    def paint(self, painter, option=None, widget=None):
        painter.setPen(QPen(Qt.transparent if not self._COLOR else
                            QColor(self._COLOR)))
        painter.drawPath(self.path())

class GxPathColliFemaleNotch(GxPathColliIoNotch):
    pass

class GxPathColliMaleNotch(GxPathColliIoNotch):
    pass

class GxArgLabel(QGraphicsItem):
    _CORNER_SIZE = [6, 6]
    _CORNER_STYLE = 'arc'

    _NOTCH_SIZE = [10, 20]
    _NOTCH_STYLE = 'arc'

    _H_PADD = 15
    _V_PADD = 5

    def __init__(self, field_info, max_name_size, style,
                 scene=None, parent=None):
        """
        :field_info: FieldInfo()
        :max_name_size: QSize()
        :style: StyleBlockFunctionCall()
        """
##        QGraphicsItem.__init__(self)
        QGraphicsItem.__init__(self, parent, scene)

        self._field_info = field_info
        self._max_name_size = max_name_size
        self._style = style

        self._width, self._height = 200, 100
        self._notch_start_y = 0
        self._colli_notch = None
        self.updateMetrics()

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QGraphicsItem.ItemClipsToShape, True)

    def updateMetrics(self):
        if isinstance(self._max_name_size, QSize):
            self._width = self._max_name_size.width() + 2*self._H_PADD
            self._height = self._max_name_size.height() + 2*self._V_PADD
        else:
            metrics = QFontMetrics(QFont(self._style.arg_font_family,
                                         self._style.arg_font_size))
            self._width = metrics.width(self._field_info.name) + \
                          2*self._H_PADD + self._NOTCH_SIZE[0]
            self._height = metrics.height() + 2*self._V_PADD
            if self._height < self._NOTCH_SIZE[1]:
                self._height = self._NOTCH_SIZE[1]

        self._notch_start_y = self._height/2 - self._NOTCH_SIZE[1]/2

        colli_path = QPainterPath(QPointF(0, 0))
        colli_path.addRect(0, 0, self._NOTCH_SIZE[0] * 1.5, self._NOTCH_SIZE[1])
        self._colli_notch = GxPathColliFemaleNotch(
            colli_path, self, self.scene())
        self._colli_notch.setPos(self._width - self._NOTCH_SIZE[0], self._notch_start_y)

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def getSize(self):
        return QSizeF(self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(QColor(self._style.arg_border_color),
                            self._style.arg_border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style.arg_background_color))

        b_padd = self._style.arg_border_width/2     # border padding
        W, H = self._width - b_padd, self._height - b_padd
        cw, ch = self._CORNER_SIZE
        nw, nh = self._NOTCH_SIZE

        x0, y0 = W, b_padd

        path = QPainterPath(QPointF(x0, y0))

        path.lineTo(W, H/2 - nh/2)

        path.connectPath(NotchIOPath(path.currentPosition(),
                                     self._NOTCH_SIZE, self._NOTCH_STYLE,
                                     clockwise=False))
        path.lineTo(W, H)
        path.lineTo(b_padd + cw, H)
        path.connectPath(CornerPath(QPointF(b_padd, H), 'bottom-left',
                                    QSize(cw, ch), self._CORNER_STYLE, True))

        path.lineTo(b_padd, b_padd + ch)
        path.connectPath(CornerPath(QPointF(b_padd, b_padd), 'top-left',
                                    QSize(cw, ch), self._CORNER_STYLE, True))
        path.lineTo(W, b_padd)
        painter.drawPath(path)

        painter.setFont(QFont(self._style.arg_font_family,
                              self._style.arg_font_size))
        painter.drawText(QRectF(b_padd, b_padd, W - nw, H),
                         Qt.AlignCenter, self._field_info.name)


class GxBlockFunctionCall(QGraphicsItem):

    _BORDER_PADDING = 10
    _NAME_PADDING = [5, 5]

    _CORNER_SIZE = [6, 6]
    _CORNER_SHAPE = 'arc'

    _NOTCH_IO_SIZE = [10, 20]
    _NOTCH_IO_SHAPE = 'arc'

    _NOTCH_VF_SIZE = [40, 5]
    _NOTCH_VF_SHAPE = 'trig/0.85'
    _NOTCH_VF_START_X = 20

    _ARGS_ALIGN = 'bellow'  # TODO: alternative 'right'
    _ARGS_V_PADD = -2
    _ARGS_MIN_LEFT_PADD = 10

    _IO_INSERT_MARKER_COLOR = '#111111'

    def __init__(self, name, args, return_=None, style=None,
                 scene=None, parent=None):
        """
        :name: str
        :args: list of FieldInfo()
        :return_: FieldInfo()
        :style: StyleBlockFunctionCall()
        """
##        QGraphicsItem.__init__(self)
        QGraphicsItem.__init__(self, parent, scene)

        self._name = name
        self._args = args
        self._return = return_
        self._style = style

        if not isinstance(style, StyleBlockFunctionCall):
            raise TypeError("Parameter 'style' must be of type %s. " % \
                StyleBlockFunctionCall + "Was given %s" % style.__class__)

        self._width, self._height = 200, 100

        self._colli_path_output = None
        self._io_insert_mark = None
        self._notch_io_start_y = 0

        self._name_height = 0
        self._max_arg_width = 0
        self._args_start_y = 0
        self._args_end_y = 0
        self._args_labels = []
        if self._args:
            self._setupArgsLabels()

        self._border_path = None
        self.updateMetrics()

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QGraphicsItem.ItemClipsToShape, True)

    def boundingRect(self):
        aj = 0
        return QRectF(-aj, -aj, self._width + aj, self._height + aj)

    def getSize(self):
        return QSizeF(self._width, self._height)

    def setBackgroundColor(self, color):
        self._bk_color = color
        self.repaint()

    def _setupArgsLabels(self):
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

#        for i, x in enumerate(self._args):
#            if isinstance(x, FieldInfo):
#                max_name_width = max(max_name_width,
#                                     arg_name_metrics.width(x.name))
#            else:
#                raise TypeError("All elements in tuple/list of the " + \
#                    "'args' parameter must be of type %s.\n" % FieldInfo + \
#                    "Was given %s in position %d." % (x.__class__, i))

        name_height = QFontMetrics(QFont(self._style.name_font_family,
                                         self._style.name_font_size)).height()

        for x in self._args:
            new_arg = GxArgLabel(x, QSize(max_name_width, name_height),
                                 self._style, self.scene(), parent=self)
            self._args_labels.append(new_arg)

            self._max_arg_width = max(self._max_arg_width,
                                      new_arg.boundingRect().width())

    def updateMetrics(self):
        self.prepareGeometryChange()

        self._font_name = QFont(self._style.name_font_family,
                                self._style.name_font_size)
        name_metrics = QFontMetrics(self._font_name)

        bw = self._style.border_width/2
        arg_bw = self._style.arg_border_width/2

        bp = self._BORDER_PADDING
        nhp, nvp = self._NAME_PADDING
        cw, ch = self._CORNER_SIZE
        vw, vh = self._NOTCH_VF_SIZE
        nw, nh = name_metrics.width(self._name), name_metrics.height()
        malp = self._ARGS_MIN_LEFT_PADD
        aw = self._max_arg_width
        iow, ioh = self._NOTCH_IO_SIZE

        center_width = max(nw, malp - nhp + aw, vw + self._NOTCH_VF_START_X)

        # setting up the width metrics
        if self._return:
            self._width = center_width + 2*bp + 2*cw + 2*nhp + iow
            self._height = 2*bp + 2*ch + 2*nvp + nh
            self._name_rect = QRectF(bp + iow + cw + nhp, bp + ch + nvp,
                                     center_width, nh)
        else:
            self._width = center_width + 2*bp + 2*cw + 2*nhp
            self._height = max(ch, vh) + 2*bp + 2*nvp + nh + ch + vh
            self._name_rect = QRectF(bp + cw + nhp, bp + max(ch, vh) + nvp,
                                     center_width, nh)

        # setting up all things related to arguments, including their
        # positions and height metrics for the global height
        ax = self._width - aw - bp + arg_bw
        ay = bp + max(ch, vh) + 2*nvp + nh       # start y coordinate
        for arg in self._args_labels:
            arg_h = arg.boundingRect().height()
            arg.setPos(ax, ay)
            ay += arg_h + self._ARGS_V_PADD
            self._height += arg_h + self._ARGS_V_PADD

        # creating the border path, based on the dimesions above
        x0, y0 = bp + cw, bp
        if self._return:
            x0 += iow

        path = GxPainterPath(QPointF(x0, y0))

        if not self._return:
            path.lineToInc(dx = self._NOTCH_VF_START_X)
            path.connectPath(NotchVFPath(path.currentPosition(),
                                         self._NOTCH_VF_SIZE,
                                         self._NOTCH_VF_SHAPE, clockwise=False))

        path.lineTo(self._width - bp - cw, path.currentPosition().y())

        path.connectPath(CornerPath(QPointF(self._width - bp, y0), 'top-right',
                                    QSizeF(cw, ch), self._CORNER_SHAPE,
                                    clockwise=True))
        path.lineTo(path.currentPosition().x(),
                    self._name_rect.top() + self._name_rect.height() + \
                    nvp + arg_bw)

        for arg in self._args_labels:
            path.lineToInc(dx = -self._NOTCH_IO_SIZE[0])
            path.lineToInc(dy = arg.boundingRect().height() - 3*arg_bw)
            path.lineToInc(dx = self._NOTCH_IO_SIZE[0])
            path.lineToInc(dy = self._ARGS_V_PADD + 3*arg_bw)

        # setup bottom right corner point (br_cp)
        if self._return:
            br_cp = QPointF(self._width - bp, self._height - bp + bw)
        else:
            br_cp = QPointF(self._width - bp, self._height - bp - vh + bw)

        path.connectPath(CornerPath(br_cp, 'bottom-right', QSizeF(cw, ch),
                                    self._CORNER_SHAPE, clockwise=True))
        if not self._return:
            path.lineTo(bp + cw + self._NOTCH_VF_START_X + vw,
                        path.currentPosition().y())

            path.connectPath(NotchVFPath(path.currentPosition(),
                                         self._NOTCH_VF_SIZE,
                                         self._NOTCH_VF_SHAPE, clockwise=True))
            path.lineTo(bp + cw, path.currentPosition().y())

            # bottom-left corner point
            bl_cp = QPointF(bp - bw, self._height - bp - vh + bw)

        else:
            path.lineTo(bp + cw + iow, path.currentPosition().y())
            bl_cp = QPointF(bp + iow, self._height - bp + bw)

        path.connectPath(CornerPath(bl_cp, 'bottom-left', QSizeF(cw, ch),
                                    self._CORNER_SHAPE, clockwise=True))

        if self._return:
            path.lineTo(path.currentPosition().x(),
                        bp + ch + (2*nvp + nh)/2 - ioh/2 + ioh)
            self._notch_io_start_y = path.currentPosition().y() - ioh
            path.connectPath(NotchIOPath(path.currentPosition(),
                                         self._NOTCH_IO_SIZE,
                                         self._NOTCH_IO_SHAPE,
                                         clockwise=True))
            path.lineTo(path.currentPosition().x(), bp + ch)

            tp_cp = QPointF(bp + iow, bp)
        else:
            path.lineTo(path.currentPosition().x(), bp + max(ch, vh))
            tp_cp = QPointF(bp - bw, bp)

        path.connectPath(CornerPath(tp_cp, 'top-left', QSizeF(cw, ch),
                                    self._CORNER_SHAPE, clockwise=True))

        self._border_path = path

        if self._return:
            colli_path = QPainterPath(QPointF(0, 0))
            colli_path.addRect(0, 0, iow/2, ioh)
            self._colli_path_output = GxPathColliMaleNotch(colli_path,
                self, self.scene())
            self._colli_path_output.setPos(bp, self._notch_io_start_y)

    def shape(self):
        return self._border_path

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(QColor(self._style.border_color),
                            self._style.border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style.background_color))
        painter.drawPath(self._border_path)

        painter.setFont(self._font_name)
        painter.setPen(QPen(QColor(self._style.name_font_color)))
        painter.drawText(self._name_rect, Qt.AlignLeft, self._name)

    def mouseMoveEvent(self, event):
        QGraphicsItem.mouseMoveEvent(self, event)

        cout = self._colli_path_output

        if cout:
            colli = [x for x in self.scene().collidingItems(cout)
                       if isinstance(x, GxPathColliFemaleNotch)]
            if colli:
                print "Found female notch!",
                c_parent = colli[0].parentItem()
                print c_parent._field_info.name

                if not self._io_insert_mark:
                    self._io_insert_mark = GxInsertMarkNotchIO(
                        self._IO_INSERT_MARKER_COLOR,
                        self._NOTCH_IO_SIZE, self._NOTCH_IO_SHAPE, self.scene())

                if self._io_insert_mark:

                    mapped_pos = c_parent.parentItem().mapToScene(c_parent.pos())
                    x, y = mapped_pos.x(), mapped_pos.y()
                    y -= self._io_insert_mark.boundingRect().height() / 2
                    y += c_parent.boundingRect().height() / 2
                    x += c_parent.boundingRect().width() - \
                        self._io_insert_mark.boundingRect().width() / 1.5

                    self._io_insert_mark.setPos(QPointF(x, y))
                    self.scene().bringToFront(self._io_insert_mark)
            else:
                if self._io_insert_mark:
                    self.scene().removeItem(self._io_insert_mark)
                    self._io_insert_mark = None

    def mouseReleaseEvent(self, event):
        QGraphicsItem.mouseReleaseEvent(self, event)

##        if self._io_insert_mark:
##            self.scene().removeItem(self._io_insert_mark)
##            self._io_insert_mark = None




if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()
    scene.setClickToFront(True)
##    scene.setItemIndexMethod(QGraphicsScene.NoIndex)

    block_digital_write = GxBlockFunctionCall('digitalWrite',
        [FieldInfo('pin', 'int', '0|13', 'combobox'),
         FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
        None, StyleBlockFunctionCall(), scene)
    block_digital_write.setPos(100, 100)
    block_digital_write.setFlags(QGraphicsItem.ItemIsMovable)

    block_digital_read = GxBlockFunctionCall('digitalRead',
        [FieldInfo('pin', 'int', '0|13', 'combobox')],
        FieldInfo('value', 'int', 'HIGH,LOW', 'combobox'),
        StyleBlockFunctionCall(), scene)
    block_digital_read.setPos(200, 300)
    block_digital_read.setFlags(QGraphicsItem.ItemIsMovable)

    block_delay = GxBlockFunctionCall('delay',
        [FieldInfo('milliseconds', 'int', '0|', 'edit')],
        None, StyleBlockFunctionCall(), scene)
    block_delay.setPos(400, 400)
    block_delay.setFlags(QGraphicsItem.ItemIsMovable)

    block_millis = GxBlockFunctionCall('millis', None,
        FieldInfo('milliseconds', 'int', '0|', 'edit'),
        StyleBlockFunctionCall(), scene)
    block_millis.setPos(400, 100)
    block_millis.setFlags(QGraphicsItem.ItemIsMovable)

##    svg_filename = 'C:\\Users\\nelso\\Desktop\\arg_label.svg'
##    create_svg_from_gx_item(block_digital_write, svg_filename)
##    svg_label = QGraphicsSvgItem(svg_filename)
##    svg_label.setFlags(QGraphicsItem.ItemIsMovable)
##    scene.addItem(svg_label)

##    io_marker = GxInsertMarkNotchIO('black', [10, 20], 'arc', scene)
##    io_marker.setPos(250, 200)
##    io_marker.setFlags(QGraphicsItem.ItemIsMovable)

    view = GxView(scene, win)
    view.setCacheMode(QGraphicsView.CacheBackground)
    view.setOptimizationFlags(QGraphicsView.DontSavePainterState)

    view.setViewport(QGLWidget())

    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())

