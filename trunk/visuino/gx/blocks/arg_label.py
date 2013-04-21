#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Nelso
#
# Created:     04/04/2013
# Copyright:   (c) Nelso 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import division, print_function

__all__ = ['GxArgLabel']

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import sys

from visuino.gx.bases import *
from visuino.gx.shapes import *
from visuino.gx.utils import *
from visuino.gx.styles import *


class GxArgLabel(QGraphicsItem):
    '''
    Shape that represents argument names to be used on function call blocks.
    It has a female IO notch on the right, and supports resizing according
    to the plugged male IO block.
    '''

    def __init__(self, name, style_label=None, style_notch=None, scene=None,
                 parent_item=None, **kwargs):
        ''' (str, StyleArgLabel, StyleNotch, GxScene, QGraphicsItem, ...)

        kwargs:
            @ fixed_width: number <None>
            @ fixed_height: number <None>
            @ fixed_io_notch_y0: number <None>
        '''
        QGraphicsItem.__init__(self, parent_item, scene)

        self._width, self._height = 0, 0
        self._child = None
        self._fixed_height = kwargs.get('fixed_height', None)
        self._fixed_width = kwargs.get('fixed_width', None)
        self._fixed_io_notch_y0 = kwargs.get('fixed_io_notch_y0', None)

        self._io_notch_start = QPointF(0, 0)

        self._style_label = style_label \
            if isinstance(style_label, StyleArgLabel) else StyleArgLabel()
        self._style_notch = style_notch \
            if isinstance(style_notch, StyleNotch) else StyleNotch()

        self._name = name
        self._name_rect = QRectF(0, 0, self._width, self._height)
        self._name_font = None
        self._border_path = QPainterPath()

        self.updateMetrics()

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def shape(self):
        ''' QGraphicsItem.shape() -> QPainterPath
        '''
        return self._border_path

    @property
    def io_notch_start(self):
        return self._io_notch_start

    @property
    def style_label(self):
        return self._style_label

    @property
    def style_notch(self):
        return self._style_notch

    def getWidth(self):
        return self._border_path.boundingRect().width()

    def getHeight(self):
        return self._border_path.boundingRect().height()

    def setFixedWidth(self, width):
        self._fixed_width = width
        self.updateMetrics()

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        # drawing the filled border path
        painter.setPen(QPen(QColor(self._style_label.border_color),
                            self._style_label.border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style_label.background_color))
        painter.drawPath(self._border_path)

        # drawing the name
        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(self._style_label.font_color)))
        painter.drawText(self._name_rect, Qt.AlignCenter, self._name)

        # drawing the name rectangle (for debugging purposes)
##        painter.setPen(Qt.DashLine)
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self._name_rect)


    def updateMetrics(self):
        ''' () -> NoneType

        Recreates its border path based on the current styles.
        '''
        self.prepareGeometryChange()

        self._name_font = QFont(self._style_label.font_family,
                                self._style_label.font_size)

        # border corrections
        bw = self._style_label.border_width/2

        # main dimensions
        name_metrics = QFontMetricsF(self._name_font)
        fvc = self._style_label.font_vcorrection
        nw, nh = name_metrics.width(self._name), name_metrics.height()
        hp, vp = self._style_label.getPadding()
        cw, ch = self._style_label.getCornerSize()
        iow, ioh = self._style_notch.getIoNotchSize()

        io_notch_shape = self._style_notch.io_notch_shape + '/' + \
                         str(self._style_notch.io_notch_basis)
        io_notch_size = QSizeF(iow, ioh)
        corner_shape = self._style_label.corner_shape

        # corner corrections (occours if corner rect intercepts name rect)
        ccw = cw - hp #if cw > hp else -(hp - cw)
        cch = ch - vp #if ch > vp else -(vp - ch)

        # default dimensions of the border path
        W = cw - ccw + nw + hp + iow
        H = 2*ch - 2*cch + max(nh, ioh)

        # prevents overlaping of corner height and vertical padding
        if 2*ch > H:
            ch = H/2

        corner_size = QSizeF(cw, ch)

        if self._fixed_height is not None:
            H = self._fixed_height
        if self._fixed_width is not None:
            W = self._fixed_width

        # starts on the top-right corner
        path = GxPainterPath(QPointF(W + bw, bw))
        path.lineToInc(dx = - W + cw)
        CornerPath.connect(path, corner_size, corner_shape, 'top-left', False)
        path.lineToInc(dy = H - 2*ch)
        CornerPath.connect(path, corner_size, corner_shape, 'bottom-left', False)
        path.lineToInc(dx = W - cw)

        if self._fixed_io_notch_y0 is None:
            path.lineToInc(dy = - (H - ioh)/2)
        else:
            path.lineToInc(dy = - (H - self._fixed_io_notch_y0 - ioh))

        NotchPath.connect(path, io_notch_size, io_notch_shape, '-j', 'left')
        self._io_notch_start = path.currentPosition()
        io_y0 = self._io_notch_start.y()

        path.closeSubpath()
        self._border_path = path

        # updating the size considering border extra pixels
        self._width, self._height = W + 2*bw, H + 2*bw

        self._name_rect = QRectF(2*bw, io_y0 + fvc - ((nh - ioh)/2),
                                 W - iow - bw, nh)

        self.update(self.boundingRect())

    def plugIn(self, child):
        self._fixed_height = child.getHeight()
        self._fixed_io_notch_y0 = child.getIoNotchStart().y()

        child.setParentItem(self)
        self._child = child
        self.updateMetrics()

    def plugOut(self):
        self._fixed_height = None
        self._fixed_io_notch_y0 = None
        self._childim = None
        self.updateMetrics()


class HollowItem:
    def __init__(self, height, io_y0):
        self.height = height
        self.io_notch_y0 = io_y0

    def getHeight(self):
        return self.height

    def getIoNotchStart(self):
        return QPointF(0, self.io_notch_y0)

    def setValues(self, height, io_y0):
        self.height = height
        self.io_notch_y0 = io_y0

    def setParentItem(self, item):
        pass


class WinCustomizeArgLabel(QMainWindow):
    '''
    Provides a window with a dock panel full of configuration fields to
    fully customize the GxArgLabel object. The changes are reflected
    immediately.

    __init__(QWidget)
    '''
    def __init__(self, parent=None):
        super(WinCustomizeArgLabel, self).__init__(parent)
        self.ui = uic.loadUi('form_arg_label_customize_.ui')
        self.setupUI()

    def setupUI(self):
        ''' () -> NoneType

        Creates the main widgets (GxView and dock customize) and also
        connect the proper signals.
        '''
        self.setGeometry(100, 100, 800, 600)

        self.scene = GxScene()

        sa = self.style_arg_label = StyleArgLabel()
        sn = self.style_notch = StyleNotch()

        self.arg_label = GxArgLabel('value', sa, sn, self.scene)
        self.arg_label.setPos(30, 30)
        self.arg_label.setFlags(QGraphicsItem.ItemIsMovable)
        self.arg_label.setCursor(Qt.OpenHandCursor)
        self.arg_label.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.child_label = HollowItem(200, 20)

        self.view = GxView(self.scene, parent=self, wheel_zoom=True,
                           opengl=True)
        self.setCentralWidget(self.view)

        dock_customize = QDockWidget('Customize', self)
        dock_customize.setWidget(self.ui)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_customize)

        # take advantage of the following convention: the first word of
        # the object name identifies the type of widget, and the rest
        # (after the first '_') is some key of the sty dict above.
        # exemple: combobox_font_family --> 'font_family' key in sty.
        for k, wg in self.ui.__dict__.items():
            suffix = k[k.find('_')+1:]
            if not hasattr(sa, suffix) and not hasattr(sn, suffix):
                continue
            elif isinstance(wg, QFrame) and not isinstance(wg, QLabel):
                # those QFrame are for color selection
                self._setupFrameClick(wg, suffix)
            elif isinstance(wg, (QSpinBox, QComboBox, QSlider)):
                self._setupSignal(wg, suffix)

        self.ui.checkbox_plug_io.stateChanged[int].connect(
            self._updatePluggedIO)
        self.ui.slider_io_plugged_height.valueChanged[int].connect(
            self._updatePluggedIO)
        self.ui.slider_io_notch_y0.valueChanged[int].connect(
            self._updatePluggedIO)


    def _setupSignal(self, sender, attr):
        ''' (QSpinBox/QComboBox/QSlider, str) -> NoneType

        Configures on the sender widget the current value of 'attr' in 'style',
        and also setup its suitable signal to customization changes.
        '''
        sty, sa, sn = None, self.style_arg_label, self.style_notch
        if hasattr(sa, attr):
            sty = sa
        elif hasattr(sn, attr):
            sty = sn
        else:
            return

        if isinstance(sender, QSpinBox):
            sender.setValue(getattr(sty, attr, 0))
            sender.valueChanged[int].connect(
                lambda: self._updateStyles(sty, attr, sender.value()))

        elif isinstance(sender, QComboBox):
            sender.setCurrentIndex(sender.findText(getattr(sty, attr, '')))
            sender.currentIndexChanged[int].connect(
                lambda: self._updateStyles(sty, attr,
                                           str(sender.currentText())))

        elif isinstance(sender, QSlider):
            sender.setValue(getattr(sty, attr, 0)*100)
            sender.valueChanged[int].connect(
                lambda: self._updateStyles(sty, attr,
                                           float(sender.value()/100)))

    def _setupFrameClick(self, frame, attr):
        ''' (QFrame, str) -> NoneType

        Configures the frame background color to the current color of
        'attr' in 'style', and also enable its mousePressEvent to execute
        a color dialog.
        '''
        palette = frame.palette()
        current_color = QColor(getattr(self.style_arg_label, attr, 'white'))
        palette.setColor(QPalette.Background, current_color)
        frame.setPalette(palette)
        frame.mousePressEvent = \
            lambda event: self._chooseColor(frame, attr)


    def _chooseColor(self, frame, attr):
        ''' (QFrame, str) -> NoneType

        Saves the current color as 'old_color', then launch the color dialog.
        Changes on the dialog are reflected immediately on the GxArgLabel.
        If the dialog is cancelled, restores 'old_color'.
        '''
        palette, sa = frame.palette(), self.style_arg_label
        old_color = palette.background().color()
        color_dialog = QColorDialog(old_color)

        color_dialog.currentColorChanged[QColor].connect(
            lambda: self._updateStyles(sa, attr,
                    str(color_dialog.currentColor().name())))

        answer = color_dialog.exec_()
        if answer == 1:
            new_color = color_dialog.currentColor()
            palette.setColor(QPalette.Background, new_color)
            frame.setPalette(palette)
            self._updateStyles(sa, attr, str(new_color.name()))
        else:
            self._updateStyles(sa, attr, str(old_color.name()))

    def _updateStyles(self, style, attr, value):
        setattr(style, attr, value)
        self.arg_label.updateMetrics()

    def _updatePluggedIO(self):
        if self.ui.checkbox_plug_io.isChecked():
            self.child_label.setValues(
                self.ui.slider_io_plugged_height.value(),
                self.ui.slider_io_notch_y0.value())
            self.arg_label.plugIn(self.child_label)
        else:
            self.arg_label.plugOut()


def main():
    app = QApplication(sys.argv)
    win = WinCustomizeArgLabel()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

