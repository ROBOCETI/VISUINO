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
from visuino.gx.connections import *
from visuino.gx.blocks.arg_label import GxArgLabel

from visuino.gui import FieldInfo

class GxBlockFunctionCall(GxPluggableBlock):
    '''
    Block that represents the function call syntax on imperative languages.
    For instance, a funcion call in Python or C is given by:

        function_name(arg1, arg2, ..., argN)

    This blocks represents graphically that piece of syntax, where each
    argument is given by an GxArgLabel object and the function return
    (optional) is signaled by a male IO connector on the left side.

    Attributes:
        _name: str. Name of the function to be showed on the block.

        _args: list of FieldInfo <None>. Arguments of the function. A list
            of GxArgLabel objects will be created based on that attribute.

        _return: FieldInfo <None>. Information about the return value of this
            function call block. If None, then will have VF connectors; else,
            will have no VF connectores and one male IO on the left side.

        _name_rect: QRectF. Rectangle in which the name text will be drawn.
            Gets updated via updateMetrics(), using Style attributes.

        _args_labels: list of GxArgLabel. Saves reference for each one of the
            argument label object.

        _args_height: number. Total height of the GxArgLabel objects in
            self._args_labels, including the spacing between them.
            Gets updated via updateMetrics().
    '''

    MSG_ERR_TYPE_ARGS = \
        "On GxBlockFunctionCall.__init__(), parameter 'args' must be a "\
        "tuple/list of <class 'FieldInfo'>."

    MSG_ERR_NOT_FIELD_INFO = \
        "On GxBlockFunctionCall.__init__(), parameter 'args', invalid value"\
        " in position %d. Expected <class 'FieldInfo'>, but was given %s."

    def __init__(self, name, args, return_, scene, parent=None):
        ''' (str, list of FieldInfo, FieldInfo, GxSceneBlocks, QGraphicsItem)
        '''
        GxPluggableBlock.__init__(self, scene, parent)

        self._name, self._args, self._return = name, args, return_
        self._name_rect = self.boundingRect()
        self._args_labels = []
        self._args_height = 0

        self.setupArgLabels()
        self.updateMetrics()

        for arg in self._args_labels:
            arg.update_parent = True

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        sfc = self.scene().style.function_call

        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(
            QBrush(QColor(sfc.border_color)), sfc.border_width,
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(sfc.background_color))
        painter.drawPath(self._border_path)

        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(sfc.name_font_color)))
        painter.drawText(self._name_rect, Qt.AlignCenter, self._name)

##        painter.setPen(Qt.DashLine)
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self.boundingRect())

    def setupArgLabels(self):
        ''' () -> NoneType

        Should be called whenever self._args changes.
        '''
        if self._args is None or not isinstance(self._args, (tuple, list)):
            return
        sa, sn = self.scene().style.arg_label, self.scene().style.notch

        for arg in self._args_labels:
            arg.removeFromScene()
        self._args_labels = []

        max_width = 0
        self._args_height = 0
        for i, x in enumerate(self._args):
            if isinstance(x, FieldInfo):
                new_label = GxArgLabel(x.name, self.scene(), parent=self,
                                       update_parent=False)
                new_label.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
                new_label.setPos(0, i*50)
##                new_label.setVisible(False)
                w = new_label.getWidth()

                max_width = w if w > max_width else max_width
                self._args_labels.append(new_label)
            else:
                raise TypeError(self.MSG_ERR_NOT_FIELD_INFO % (i, x.__class__))

        for arg in self._args_labels:
            arg.setFixedWidth(max_width)
            arg.update_parent = True


    def updateMetrics(self):
        ''' () -> NoneType


        '''
        self.prepareGeometryChange()
        self.old_size = self.boundingRect().size()

        style_fc = self.scene().style.function_call
        style_notch = self.scene().style.notch

        # half of the border width, for use as correction
        bw = style_fc.border_width/2

        self._name_font = QFont(style_fc.name_font_family,
                                style_fc.name_font_size)
        name_metrics = QFontMetricsF(self._name_font)

        # setting up nice short names for all the metrics
        nw, nh = name_metrics.width(self._name), name_metrics.height()
        fvc = style_fc.name_font_vcorrection
        hp, vp = style_fc.getNamePadding()
        bp = style_fc.bottom_padd
        cw, ch = style_fc.getCornerSize()
        malp = style_fc.arg_min_left_padd
        asp = style_fc.arg_spacing
        iow, ioh = style_notch.getIoNotchSize()
        vfw, vfh = style_notch.getVfNotchSize()
        vfs = bw + style_notch.vf_notch_x0

        # some nice short names for more attributes
        corner_shape = style_fc.corner_shape
        corner_size = QSizeF(cw, ch)
        io_shape = style_notch.io_notch_shape + '/' + \
                   str(style_notch.io_notch_basis)
        io_size = QSizeF(iow, ioh)
        vf_shape = style_notch.vf_notch_shape + '/' + \
                   str(style_notch.vf_notch_basis)
        vf_size = QSizeF(vfw, vfh)

        maw = 0    # minimum width to comport arguments, if any
        if self._args_labels:
            maw = malp + self._args_labels[0].getWidth()
        else:
            fvc += 1

        # updating the total argument height
        self._args_height = 0
        for arg in self._args_labels:
            self._args_height += arg.getHeight()

        if self._args:
            self._args_height += (len(self._args) - 1) * \
                self.scene().style.function_call.arg_spacing

        if self._return:
            # height from the top up to the args y0
            args_y0 = max(vp, ch) + nh + vp
            name_y0 = args_y0 - vp - nh

            # there are two metrics to limit the width:
            #   - name width + horizontal padding (2*max(hp, cw) + nw)
            #   - minimum argument left padding + arg label width (maw)
            W = iow + max(2*max(hp, cw) + nw, maw, 50)
            H = args_y0 + self._args_height + ch + bp

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
            self.io_male_start = path.currentPosition()
            path.closeSubpath()

            self._name_rect = QRectF(bw + iow + hp, name_y0 + fvc,
                                     W - 2*hp - iow, nh)
            self.vf_female_start = None
            self.vf_male_start = None
        else:
            # height from the top up to the args y0
            args_y0 = vfh + 2*vp + nh

            # there are three metrics to limit the width:
            #   - name width + horizontal padding (2*max(hp, cw) + nw)
            #   - vf notch x0 + vf notch width (vfs + vfw)
            #   - minimum argument left padding + arg label width (maw)
            W = max(2*max(hp, cw) + nw, vfs + vfw + cw + 10, maw)
            H = args_y0 + self._args_height + ch + vfh + bp

            path = GxPainterPath(QPointF(bw, bw + ch))
            CornerPath.connect(path, corner_size, corner_shape, 'top-left')
            path.lineToInc(dx = vfs - cw)
            self.vf_female_start = path.currentPosition()
            NotchPath.connect(path, vf_size, vf_shape, '+i', 'down')
            path.lineTo(W - cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'top-right')
            path.lineTo(path.x, args_y0)

            self._placeArgs(path, iow, bw, W, asp)

            CornerPath.connect(path, corner_size, corner_shape, 'bottom-right')
            path.lineToInc(dx = -W + vfs + cw + vfw)
            NotchPath.connect(path, vf_size, vf_shape, '-i', 'down')
            self.vf_male_start = path.currentPosition()
            path.lineTo(bw + cw, path.y)
            CornerPath.connect(path, corner_size, corner_shape, 'bottom-left')
            path.closeSubpath()

            self._name_rect = QRectF(bw + hp, args_y0 - vp - nh + fvc,
                                     W - 2*hp, nh)
            self.io_male_start = None

        self._border_path = path
        self._width, self._height = W + bw, H + bw

        print('Updating connectors GxBlockFunctionCall ', self._name)
        self.updateConnections()
        self.update(self.boundingRect())

        if isinstance(self.parentItem(), GxBlock):
            print("Updating %s parent!" % self._name)
            self.parentItem().updateMetrics()

    def _placeArgs(self, path, iow, bw, W, asp):
        ''' (GxPainterPath, number, number, number, number) -> NoneType

        From the current position on the path, set the GxArgLabel objects
        final positions.
        '''
        for arg in self._args_labels:
            arg.setPos(W - arg.getWidth() - bw, path.y - bw)
            path.lineToInc(dx = -iow - 3*bw)
            path.lineToInc(dy = arg.getHeight())
            path.lineToInc(dx = iow + 3*bw)
            path.lineToInc(dy = asp)

    def setName(self, name):
        ''' (str) -> NoneType

        Set the function name attribute, and also update the graphics.
        '''
        self._name = name
        self.updateMetrics()

    def setReturn(self, return_):
        ''' (FieldInfo) -> NoneType

        Set the return value attribute, and also update the graphics.
        '''
        if isinstance(return_, FieldInfo):
            self._return = return_
        else:
            self._return = None
        self.updateMetrics()

    def setArgs(self, args):
        ''' (list of FieldInfo) -> NoneType

        Set its arguments information, and also update the graphics.
        '''
        self._args = args
        self.setupArgLabels()
        self.updateMetrics()

    def cloneMe(self, scene):
        ''' (GxSceneBlocks) -> GxBlockFunctionCall
        '''
        return GxBlockFunctionCall(self._name, self._args, self._return,
                                   scene)

    def __repr__(self):
        return "GxBlockFunctionCall " + str(self._name)


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

        self.scene = GxSceneBlocks()

        sfc = self.scene.style.function_call
        sa = self.scene.style.arg_label
        sn = self.scene.style.notch
        self.args = ['pin', 'value']

        self.block_function_call = GxBlockFunctionCall('digitalWrite',
            self._strToFieldInfo(self.args), None, self.scene)
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
        if not self.args:
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
