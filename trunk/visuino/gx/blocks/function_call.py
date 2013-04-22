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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import sys

from visuino.gx.bases import *
from visuino.gx.shapes import *
from visuino.gx.utils import *
from visuino.gx.styles import *
from visuino.gx.blocks.arg_label import GxArgLabel
from visuino.gui import FieldInfo

class GxBlockFunctionCall(QGraphicsItem):

    MSG_ERR_TYPE_ARGS = \
        "On GxBlockFunctionCall.__init__(), parameter 'args' must be a "\
        "tuple/list of <class 'FieldInfo'>."

    MSG_ERR_NOT_FIELD_INFO = \
        "On GxBlockFunctionCall.__init__(), parameter 'args', invalid value"\
        " in position %d. Expected <class 'FieldInfo'>, but was given %s."

    def __init__(self, name, args, return_, style_arg_label, style_notch,
                 style_function_call, scene=None, parent_item=None):
        ''' (str, list of FieldInfo, FieldInfo, StyleArgLabel, StyleNotch,
             StyleFunctionCall, GxScene, QGraphicsItem)
        '''
        QGraphicsItem.__init__(self, parent_item, scene)

        self._width, self._height = 300, 300

        self._style_arg_label = style_arg_label \
            if isinstance(style_arg_label, StyleArgLabel) else StyleArgLabel()

        self._style_function_call = style_function_call \
            if isinstance(style_function_call, StyleFunctionCall) \
            else StyleFunctionCall()

        self._style_notch = style_notch \
            if isinstance(style_notch, StyleNotch) else StyleNotch()

        self._name, self._args, self._return = name, args, return_
        self._name_rect = self.boundingRect()
        self._arg_labels = []
        self._arg_name_font = None
        self._args_height = 0
        self.setupArgLabels()

        self._border_path = None
        self.updateMetrics()


    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(
            QBrush(QColor(self._style_function_call.border_color)),
            self._style_function_call.border_width,
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style_function_call.background_color))
        painter.drawPath(self._border_path)

        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(self._style_function_call.name_font_color)))
        painter.drawText(self._name_rect, Qt.AlignCenter, self._name)

##        painter.setPen(Qt.DashLine)
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self._name_rect)

    def shape(self):
        return self._border_path

    def setupArgLabels(self):
        if self._args is None:
            return
        elif not isinstance(self._args, (tuple, list)):
            raise TypeError(self.MSG_ERR_TYPE_ARGS)

        sa, sn = self._style_arg_label, self._style_notch
        self._arg_labels = []

        max_width = 0
        for i, x in enumerate(self._args):
            if not isinstance(x, FieldInfo):
               raise TypeError(self.MSG_ERR_NOT_FIELD_INFO % (i, x.__class__))
            else:
                new_label = GxArgLabel(x.name, sa, sn, self.scene(),
                                       parent_item=self)
                new_label.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
                new_label.setPos(0, i*50)
##                new_label.setVisible(False)
                w, h = new_label.getWidth(), new_label.getHeight()

                max_width = w if w > max_width else max_width
                self._arg_labels.append(new_label)
                self._args_height += h

        if self._args:
            self._args_height += (len(self._args) - 1) * \
                self._style_function_call.arg_spacing

        for x in self._arg_labels:
            x.setFixedWidth(max_width)

    def updateMetrics(self):
        self.prepareGeometryChange()
        self.old_size = self.boundingRect().size()

        # half of the border width, for use as correction
        bw = self._style_function_call.border_width/2

        self._name_font = QFont(self._style_function_call.name_font_family,
                                self._style_function_call.name_font_size)
        name_metrics = QFontMetricsF(self._name_font)

        # setting up nice short names for all the metrics
        nw, nh = name_metrics.width(self._name), name_metrics.height()
        fvc = self._style_function_call.name_font_vcorrection
        hp, vp = self._style_function_call.getNamePadding()
        bp = self._style_function_call.bottom_padd
        cw, ch = self._style_function_call.getCornerSize()
        malp = self._style_function_call.arg_min_left_padd
        asp = self._style_function_call.arg_spacing
        iow, ioh = self._style_notch.getIoNotchSize()
        vfw, vfh = self._style_notch.getVfNotchSize()
        vfs = bw + self._style_notch.vf_notch_x0


        # some nice short names for more attributes
        corner_shape = self._style_function_call.corner_shape
        corner_size = QSizeF(cw, ch)
        io_shape = self._style_notch.io_notch_shape + '/' + \
                   str(self._style_notch.io_notch_basis)
        io_size = QSizeF(iow, ioh)
        vf_shape = self._style_notch.vf_notch_shape + '/' + \
                   str(self._style_notch.vf_notch_basis)
        vf_size = QSizeF(vfw, vfh)

        maw = 0    # minimum width to comport arguments, if any
        if self._arg_labels:
            maw = malp + self._arg_labels[0].getWidth()

        if self._return:
            # height from the top up to the args y0
            args_y0 = max(vp, ch) + nh + vp
            name_y0 = args_y0 - vp - nh
            if not self._args:
                name_y0 += 1

            # there are two metrics to limit the width:
            #   - name width + horizontal padding (2*max(hp, cw) + nw)
            #   - minimum argument left padding + arg label width (maw)
            W = iow + max(2*max(hp, cw) + nw, maw, 50)
            H = args_y0 + self._args_height + ch

            path = GxPainterPath(QPointF(bw + iow, bw + ch))
            CornerPath.connect(path, corner_size, corner_shape, 'top-left')
            path.lineTo(W - cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'top-right')
            path.lineTo(path.x, args_y0)

            self._placeArgs(path, iow, bw, W, asp)

            CornerPath.connect(path, corner_size, corner_shape, 'bottom-right')
            path.lineTo(bw + iow + cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'bottom-left')
            path.lineTo(path.x, name_y0 + ioh + (nh - ioh)/2 + 2)
            NotchPath.connect(path, io_size, io_shape, '-j', 'left')
            path.closeSubpath()

            self._name_rect = QRectF(bw + iow + hp, name_y0 + fvc,
                                     W - 2*hp - iow, nh)
        else:
            # height from the top up to the args y0
            args_y0 = vfh + 2*vp + nh

            # there are three metrics to limit the width:
            #   - name width + horizontal padding (2*max(hp, cw) + nw)
            #   - vf notch x0 + vf notch width (vfs + vfw)
            #   - minimum argument left padding + arg label width (maw)
            W = max(2*max(hp, cw) + nw, vfs + vfw + cw + 10, maw)
            H = args_y0 + self._args_height + ch + vfh

            path = GxPainterPath(QPointF(bw, bw + ch))
            CornerPath.connect(path, corner_size, corner_shape, 'top-left')
            path.lineToInc(vfs - cw)
            NotchPath.connect(path, vf_size, vf_shape, '+i', 'down')
            path.lineTo(W - cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'top-right')
            path.lineTo(path.x, args_y0)

            self._placeArgs(path, iow, bw, W, asp)

            CornerPath.connect(path, corner_size, corner_shape, 'bottom-right')
            path.lineToInc(dx = -W + vfs + cw + vfw)
            NotchPath.connect(path, vf_size, vf_shape, '-i', 'down')
            path.lineTo(bw + cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'bottom-left')
            path.closeSubpath()

            self._name_rect = QRectF(bw + hp, args_y0 - vp - nh + fvc,
                                     W - 2*hp, nh)

        self._border_path = path
        self._width, self._height = W + bw, H + bw

        self.update(self.boundingRect())

    def _placeArgs(self, path, iow, bw, W, asp):
        for arg in self._arg_labels:
            arg.setPos(W - arg.getWidth() - bw, path.y - bw)
            path.lineToInc(dx = -iow - 3*bw)
            path.lineToInc(dy = arg.getHeight())
            path.lineToInc(dx = iow + 3*bw)
            path.lineToInc(dy = asp)

    def setName(self, name):
        self._name = name
        self.updateMetrics()

    def setReturn(self, return_):
        if return_ is None:
            self._return = None
        elif isinstance(return_, FieldInfo):
            self._return = return_
        self.updateMetrics()

    def setArgs(self, args):
        self._args = args
        for arg in self._arg_labels:
            self.scene().removeItem(arg)
        self.setupArgLabels()
        self.updateMetrics()


class WinCustomizeFunctionCall(QMainWindow):
    def __init__(self, parent=None):
        super(WinCustomizeFunctionCall, self).__init__(parent)
        self.ui = uic.loadUi('form_customize_function_call.ui')
        self.initUi()

    def initUi(self):
        ''' () -> NoneType

        Creates the main widgets (GxView and dock customize) and also
        connect the proper signals.
        '''
        self.setGeometry(100, 100, 800, 600)

        self.scene = GxScene()

        sfc = self.style_function_call = StyleFunctionCall()
        sa = self.style_arg_label = StyleArgLabel()
        sn = self.style_notch = StyleNotch()
        self.args = ['pin', 'value']

        self.block_function_call = GxBlockFunctionCall('digitalWrite',
            self._strToFieldInfo(self.args), None, sa, sn, sfc, self.scene)
        self.block_function_call.setPos(100, 100)
        self.block_function_call.setFlags(QGraphicsItem.ItemIsMovable)
        self.block_function_call.setCursor(Qt.OpenHandCursor)
        self.block_function_call.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.view = GxView(self.scene, parent=self, wheel_zoom=True,
                           opengl=True)
        self.setCentralWidget(self.view)

        dock_customize = QDockWidget('Customize', self)
        dock_customize.setWidget(self.ui)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_customize)

        self.ui.edit_fc_name.textChanged[str].connect(
            lambda: self.block_function_call.setName(
                    self.ui.edit_fc_name.text()))
        self.ui.checkbox_fc_return.stateChanged[int].connect(
            lambda: self._changeReturn(self.ui.checkbox_fc_return))
        self.ui.edit_fc_args.textChanged[str].connect(
            lambda: self._updateArgs(self.ui.edit_fc_args.text()))

        # UI name convention:
        #   widget kind + '_' + tab identifier + '_' + style attribute

        s_tabs = {'fc': sfc, 'arg': sa, 'nch': sn}
        for k, wg in self.ui.__dict__.items():
            suffix = k[k.find('_')+1:]
            tab_prefix = suffix[:suffix.find('_')]
            style_attr = suffix[suffix.find('_')+1:]
##            print('Testing %s' % k)

            if (not hasattr(sa, style_attr) and not hasattr(sn, style_attr) \
                and not hasattr(sfc, style_attr)):
                continue
            elif isinstance(wg, (QSpinBox, QComboBox, QSlider)):
                self._setupSignal(wg, s_tabs[tab_prefix], style_attr)
            elif isinstance(wg, QFrame) and not isinstance(wg, QLabel):
                # those QFrame are for color selection
                self._setupFrameClick(wg, s_tabs[tab_prefix], style_attr)

        self.ui.slider_vf_notch_x0.setValue(sn.vf_notch_x0)
        self.ui.slider_vf_notch_x0.valueChanged[int].connect(
            lambda: self._updateStyle(sn, 'vf_notch_x0',
                    self.ui.slider_vf_notch_x0.value()))

    def _strToFieldInfo(self, str_list):
        return [FieldInfo(x, 'int', '0|', 'edit') for x in str_list]

    def _changeReturn(self, checkbox):
        if checkbox.isChecked():
            self.block_function_call.setReturn(
                FieldInfo('value', 'int', '0|', 'edit'))
        else:
            self.block_function_call.setReturn(None)

    def _updateArgs(self, text):
        self.args = []
        if len(text.strip()) != 0:
            for x in [x.strip() for x in text.split(',')]:
                self.args.append(FieldInfo(x, 'int', '|', 'edit'))
        self.block_function_call.setArgs(self.args)


    def _updateStyle(self, style, attr, value):
        setattr(style, attr, value)
        if isinstance(style, StyleFunctionCall) or not self.args:
            self.block_function_call.updateMetrics()
        elif self.args:
            self.block_function_call.setArgs(
                [FieldInfo(x, 'int', '0|', 'edit') for x in self.args])


    def _setupSignal(self, sender, style, attr):
        ''' (QSpinBox/QComboBox/QSlider, str) -> NoneType

        Configures on the sender widget the current value of 'attr' in 'style',
        and also setup its suitable signal to customization changes.
        '''
        if isinstance(sender, QSpinBox):
            sender.setValue(getattr(style, attr, 0))
            sender.valueChanged[int].connect(
                lambda: self._updateStyle(style, attr, sender.value()))

        elif isinstance(sender, QComboBox):
            sender.setCurrentIndex(sender.findText(getattr(style, attr, '')))
            sender.currentIndexChanged[int].connect(
                lambda: self._updateStyle(style, attr,
                                           str(sender.currentText())))

        elif isinstance(sender, QSlider):
            sender.setValue(getattr(style, attr, 0)*100)
            sender.valueChanged[int].connect(
                lambda: self._updateStyle(style, attr,
                                           float(sender.value()/100)))

    def _setupFrameClick(self, frame, style, attr):
        ''' (QFrame, str) -> NoneType

        Configures the frame background color to the current color of
        'attr' in 'style', and also enable its mousePressEvent to execute
        a color dialog.
        '''
        palette = frame.palette()
        current_color = QColor(getattr(style, attr, 'white'))
        palette.setColor(QPalette.Background, current_color)
        frame.setPalette(palette)
        frame.mousePressEvent = \
            lambda event: self._chooseColor(frame, style, attr)

    def _chooseColor(self, frame, style, attr):
        ''' (QFrame, Style, str) -> NoneType

        Saves the current color as 'old_color', then launch the color dialog.
        Changes on the dialog are reflected immediately on the GxArgLabel.
        If the dialog is cancelled, restores 'old_color'.
        '''
        palette = frame.palette()
        old_color = palette.background().color()
        color_dialog = QColorDialog(old_color)

        color_dialog.currentColorChanged[QColor].connect(
            lambda: self._updateStyle(style, attr,
                    str(color_dialog.currentColor().name())))

        answer = color_dialog.exec_()
        if answer == 1:
            new_color = color_dialog.currentColor()
            palette.setColor(QPalette.Background, new_color)
            frame.setPalette(palette)
            self._updateStyle(style, attr, str(new_color.name()))
        else:
            self._updateStyle(style, attr, str(old_color.name()))


def main():
    app = QApplication(sys.argv)
    win = WinCustomizeFunctionCall()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
