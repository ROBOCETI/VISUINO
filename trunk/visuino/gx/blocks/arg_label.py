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

    def __init__(self, text, style_label=None, style_notch=None, scene=None,
                 **kwargs):
        ''' (str, StyleArgLabel, StyleNotch, GxScene, kwargs)

        kwargs:
            @ pos: <(0, 0)> tuple/list of 2 int. Format: (width, height)
            @ parent_item: <None> QGraphicsItem
        '''
        QGraphicsItem.__init__(self, kwargs.get('parent_item', None),
                               scene)

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setCursor(Qt.OpenHandCursor)
        self.setFlags(QGraphicsItem.ItemIsMovable)

        self._width, self._height = 200, 100

        pos = kwargs.get('pos', (0, 0))
        self.setPos(QPointF(pos[0], pos[1]))

        flags = kwargs.get('flags', None)
        if isinstance(flags, int):
            self.setFlags(flags)

        self._style_label = style_label if style_label is not None \
                                        else StyleArgLabel()
        self._style_notch = style_notch if style_notch is not None \
                                        else StyleNotch()

        self._text = text
        self._text_rect = QRectF(0, 0, self._width, self._height)
        self._text_font = None
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

        # drawing the text
        painter.setFont(self._text_font)
        painter.setPen(QPen(QColor(self._style_label.font_color)))
        painter.drawText(self._text_rect, Qt.AlignCenter, self._text)

        # drawing the text rectangle (for debugging purposes)
##        painter.setPen(Qt.DashLine)
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self._text_rect)


    def updateMetrics(self):
        ''' () -> NoneType

        Recreates its border path based on the current styles.
        '''
        self.prepareGeometryChange()

        self._text_font = QFont(self._style_label.font_family,
                                self._style_label.font_size)

        # border corrections
        bw = self._style_label.border_width/2

        # main dimensions
        text_metrics = QFontMetricsF(self._text_font)
        tw, th = text_metrics.width(self._text), text_metrics.height()
        hp, vp = self._style_label.padding
        cw, ch = self._style_label.corner_size
        iow, ioh = self._style_notch.io_size

        # prevents overlaping of corner height and vertical padding
        if 2*ch > 2*vp + max(th, ioh):
            ch = (2*vp + max(th, ioh))/ 2

        notch_shape = self._style_notch.io_shape + '/' \
                      + str(self._style_notch.io_basis)
        corner_shape = self._style_label.corner_shape
        corner_size = QSizeF(cw, ch)

        # corner corrections (occours if corner rect intercepts text rect)
        ccw = cw - hp if cw > hp else -(hp - cw)
        cch = ch - vp if ch > vp else -(vp - ch)

        # final dimensions of the border path (does not include bw corrections)
        W = cw + - ccw + tw + hp + iow
        H = 2*ch - 2*cch + max(th, ioh)

        # starts on the top-right corner
        path = GxPainterPath(QPointF(W + bw, bw))

        path.lineToInc(dx = - W + cw)

        path.connectPath(CornerPath(path.currentPosition(), corner_size,
                                    corner_shape, 'top-left',
                                    clockwise=False))

        path.lineToInc(dy = - cch + max(th, ioh) - cch)

        path.connectPath(CornerPath(path.currentPosition(), corner_size,
                                    corner_shape, 'bottom-left',

                                    clockwise=False))
        path.lineToInc(dx = W - cw)
        path.lineToInc(dy = - (H - ioh)/2)

        path.connectPath(NotchPath(path.currentPosition(), QSizeF(iow, ioh),
                                   notch_shape, '-j', 'left'))

        path.closeSubpath()
        self._border_path = path

        # updating the size considering border extra pixels
        self._width, self._height = W + 2*bw, H + 2*bw
        self._text_rect = QRectF(0, self._style_label.font_vcorrection,
                                 self._width - iow, self._height)


    def getStyle(self):
        ''' () -> dict

        Returns all the customizable properties of this graphical item on
        the form of a dict. They include attributes of StyleArgLabel and
        also StyleNotch.
        '''
        s, sn = self._style_label, self._style_notch

        return {'font_size': s.font_size, 'font_family': s.font_family,
                'font_color': s.font_color, 'background_color': s.background_color,
                'border_color': s.border_color, 'border_width': s.border_width,
                'hpadd': s.padding[0], 'vpadd': s.padding[1],
                'corner_width': s.corner_size[0], 'corner_height': s.corner_size[1],
                'corner_shape': s.corner_shape, 'io_notch_shape': sn.io_shape,
                'io_notch_width': sn.io_size[0], 'io_notch_height': sn.io_size[1],
                'font_vcorrection': s.font_vcorrection,
                'io_notch_basis': sn.io_basis}


    def setStyle(self, **kwargs):
        ''' (keyword arguments) -> NoneType

        The keys corresponds to the same at the dict returned by .getStyle().
        Uses the current value as default if some key is not provided.

        PS: The types of the values should be the valid ones - it doesn't do
        any verification nor conversion.
        '''
        s, sn = self._style_label, self._style_notch

        s.padding[0] = kwargs.get('hpadd', s.padding[0])
        s.padding[1] = kwargs.get('vpadd', s.padding[1])
        s.font_size = kwargs.get('font_size', s.font_size)
        s.font_family = kwargs.get('font_family', s.font_family)
        s.font_color = kwargs.get('font_color', s.font_color)
        s.corner_shape = kwargs.get('corner_shape', s.corner_shape)
        s.corner_size[0] = kwargs.get('corner_width', s.corner_size[0])
        s.corner_size[1] = kwargs.get('corner_height', s.corner_size[1])
        s.background_color = kwargs.get('background_color', s.background_color)
        s.border_color = kwargs.get('border_color', s.border_color)
        s.border_width = kwargs.get('border_width', s.border_width)
        s.font_vcorrection = kwargs.get('font_vcorrection', s.font_vcorrection)

        sn.io_shape = kwargs.get('io_notch_shape', sn.io_shape)
        sn.io_basis = kwargs.get('io_notch_basis', sn.io_basis)
        sn.io_size[0] = kwargs.get('io_notch_width', sn.io_size[0])
        sn.io_size[1] = kwargs.get('io_notch_height', sn.io_size[1])

        self.updateMetrics()
        self.update()


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
        self.arg_label = GxArgLabel('digitalWrite', scene=self.scene,
                                    pos=(30, 30))
        self.view = GxView(self.scene, parent=self, wheel_zoom=True,
                           opengl=True)
        self.setCentralWidget(self.view)

        dock_customize = QDockWidget('Customize', self)
        dock_customize.setWidget(self.ui)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_customize)

        sty = self.arg_label.getStyle()

        # take advantage of the following convention: the first word of
        # the object name identifies the type of widget, and the rest
        # (after the first '_') is some key of the sty dict above.
        # exemple: combobox_font_family --> 'font_family' key in sty.
        for k, wg in self.ui.__dict__.items():
            suffix = k[k.find('_')+1:]
            if isinstance(wg, QFrame) and not isinstance(wg, QLabel):
                # those QFrame are for color selection
                self._setupFrameClick(wg, suffix, sty)
            elif isinstance(wg, (QSpinBox, QComboBox, QSlider)):
                self._setupSignal(wg, suffix, sty)


    def _setupSignal(self, sender, attr, style):
        ''' (QSpinBox/QComboBox/QSlider, str, dict) -> NoneType

        Configures on the sender widget the current value of 'attr' in 'style',
        and also setup its suitable signal to customization changes.
        '''
        if isinstance(sender, QSpinBox):
            sender.setValue(style[attr])
            self.connect(sender, SIGNAL('valueChanged(int)'),
                         lambda: self.arg_label.setStyle(
                                 **{attr: sender.value()}))

        elif isinstance(sender, QComboBox):
            sender.setCurrentIndex(sender.findText(style[attr]))
            self.connect(sender, SIGNAL('currentIndexChanged(int)'),
                         lambda: self.arg_label.setStyle(
                                 **{attr: str(sender.currentText())}))

        elif isinstance(sender, QSlider):
            sender.setValue(style[attr]*100)
            self.connect(sender, SIGNAL('valueChanged(int)'),
                         lambda: self.arg_label.setStyle(
                                 **{attr: float(sender.value()/100)}))


    def _setupFrameClick(self, frame, attr, style):
        ''' (QFrame, str, dict) -> NoneType

        Configures the frame background color to the current color of
        'attr' in 'style', and also enable its mousePressEvent to execute
        a color dialog.
        '''
        palette = frame.palette()
        palette.setColor(QPalette.Background, QColor(style[attr]))
        frame.setPalette(palette)
        frame.mousePressEvent = \
            lambda event: self._chooseColor(frame, attr)


    def _chooseColor(self, frame, attr):
        ''' (QFrame, str) -> NoneType

        Saves the current color as 'old_color', then lanch the color dialog.
        Changes on the dialog are reflected immediately on the GxArgLabel.
        If the dialog is cancelled, restores 'old_color'.
        '''
        palette = frame.palette()
        old_color = palette.background().color()
        color_dialog = QColorDialog(old_color)

        self.connect(color_dialog,
                     SIGNAL('currentColorChanged ( const QColor &)'),
                     lambda: self.arg_label.setStyle(
                             **{attr: str(color_dialog.currentColor().name())}))

        answer = color_dialog.exec_()
        if answer == 1:
            new_color = color_dialog.currentColor()
            palette.setColor(QPalette.Background, new_color)
            frame.setPalette(palette)
            self.arg_label.setStyle(**{attr: str(new_color.name())})
        else:
            self.arg_label.setStyle(**{attr: str(old_color.name())})


def main():
    app = QApplication(sys.argv)
    win = WinCustomizeArgLabel()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
