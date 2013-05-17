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
import sys
if __name__ == '__main__':
    sys.path.append('../../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

from visuino.gx.bases import *
from visuino.gx.shapes import *
from visuino.gx.utils import *
from visuino.gx.styles import *
from visuino.gx.connections import *

__all__ = ['GxArgLabel']

class GxArgLabel(GxPluggableBlock):
    '''
    Shape that represents argument names to be used on function call blocks.
    It has a female IO notch on the right and resizes itself according to the 
    plugged male IO block.
    '''

    def __init__(self, arg_info, scene=None, parent=None, **kwargs):
        ''' (dict, GxSceneBlocks, QGraphicsItem, **)

        kwargs:
            @ fixed_width: number <None>
            @ update_parent: True <False>
        '''
        GxPluggableBlock.__init__(self, scene, parent, mouse_active=False)
        self._arg_info = arg_info

        self._fixed_width = kwargs.get('fixed_width', None)
        self.update_parent = kwargs.get('update_parent', True)
        
        self._name_rect = self.boundingRect()
        self._name_font = QFont('Verdana', 12)

        self.updateMetrics()
        
            
    def __repr__(self):
        return "<GxArgLabel '%s'>" % str(self._arg_info['name'])
        
    @property
    def element(self):
        parent_fc = self.parentItem()
        if parent_fc:
            return parent_fc.element
        else:
            return None

    def getBorderWidth(self):
        return self.scene().style.arg_label.border_width        

    def setFixedWidth(self, width):
        ''' (number) -> NoneType
        '''
        self._fixed_width = width
        self.updateMetrics()

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        sa = self.scene().style.arg_label
        painter.fillRect(self.boundingRect(), Qt.transparent)

        # drawing the filled border path
        painter.setPen(QPen(QColor(sa.border_color), sa.border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(sa.background_color))
        painter.drawPath(self._border_path)

        # drawing the name
        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(sa.font_color)))
        painter.drawText(self._name_rect, Qt.AlignCenter, self._arg_info['name'])

        # drawing the name rectangle (for debugging purposes)
##        painter.setPen(Qt.DashLine)
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self._name_rect)

    def updateMetrics(self):
        ''' () -> NoneType

        Recreates its border path based on the current styles.
        '''
        self.prepareGeometryChange()

        style_label = self.scene().style.arg_label
        style_notch = self.scene().style.notch

        self._name_font = QFont(style_label.font_family,
                                style_label.font_size)

        # border corrections
        bw = style_label.border_width/2

        # main dimensions
        name_metrics = QFontMetricsF(self._name_font)
        fvc = style_label.font_vcorrection
        nw, nh = name_metrics.width(self._arg_info['name']), name_metrics.height()
        hp, vp = style_label.getPadding()
        cw, ch = style_label.getCornerSize()
        iow, ioh = style_notch.getIoNotchSize()

        io_notch_shape = style_notch.io_notch_shape + '/' + \
                         str(style_notch.io_notch_basis)
        io_notch_size = QSizeF(iow, ioh)
        corner_shape = style_label.corner_shape

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

        if self.child_io:
            H = self.child_io.getHeight()
        if self._fixed_width is not None:
            W = self._fixed_width

        # starts on the top-right corner
        path = GxPainterPath(QPointF(W + bw, bw))
        path.lineToInc(dx = - W + cw)
        CornerPath.connect(path, corner_size, corner_shape, 'top-left', False)
        path.lineToInc(dy = H - 2*ch)
        CornerPath.connect(path, corner_size, corner_shape, 'bottom-left', False)
        path.lineToInc(dx = W - cw)

        if self.child_io:
            path.lineToInc(dy = - (H - self.child_io.io_male_start.y() - ioh))
        else:
            path.lineToInc(dy = - (H - ioh)/2)

        NotchPath.connect(path, io_notch_size, io_notch_shape, '-j', 'left')
        self.io_female_start, io_y0 = path.currentPosition(), path.y
        path.closeSubpath()
        self._border_path = path

        # updating the size considering border extra pixels
        self._width, self._height = W + 2*bw, H + 2*bw

        self._name_rect = QRectF(2*bw, io_y0 + fvc - ((nh - ioh)/2),
                                 W - iow - bw, nh)

#        print('Updating connectors GxArgLabel', self._name)
        self.updateConnections()

        self.update(self.boundingRect())

        if self.update_parent:
            if isinstance(self.parentItem(), GxBlock):
                self.parentItem().updateMetrics()

    def updateElement(self, new_element):
        ''' (dict)
        '''
        parent_fc = self.parentItem()   # must be GxBlockFunctionCall
        if not parent_fc: return
        
        for i, arg in enumerate(parent_fc.definition['args']):
            if arg['name'] == self._arg_info['name']:
                break
#        print('Updated parent fc element on arg %d..' % i)
        parent_fc.element['args'][i] = new_element
            

class HollowItem(object):
    def __init__(self, height, y0):
        self.height = height
        self.io_male_start = QPointF(0, y0)
        
    def getBorderWidth(self):
        return 2
        
    def getHeight(self):
        return self.height
        


class WinCustomizeArgLabel(QMainWindow):
    '''
    Provides a window with a dock panel full of configuration fields to
    fully customize the GxArgLabel object. The changes are reflected
    immediately.

    __init__(QWidget)
    '''
    def __init__(self, parent=None):
        super(WinCustomizeArgLabel, self).__init__(parent)
        self.ui = uic.loadUi('form_customize_arg_label.ui')
        self.setupUI()

    def setupUI(self):
        ''' () -> NoneType

        Creates the main widgets (GxView and dock customize) and also
        connect the proper signals.
        '''
        self.setGeometry(100, 100, 800, 600)

        self.scene = GxSceneBlocks()

        self.arg_label = GxArgLabel({'name': 'value', 'type': 'int', 
                                     'restriction': 'HIGH,LOW'}, 
                                    self.scene)
        self.arg_label.setPos(30, 30)
        self.arg_label.setFlags(QGraphicsItem.ItemIsMovable)
        self.arg_label.setCursor(Qt.OpenHandCursor)
        self.arg_label.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.view = GxView(self.scene, parent=self, wheel_zoom=True,
                           opengl=True)
        self.setCentralWidget(self.view)

        dock_customize = QDockWidget('Customize', self)
        dock_customize.setWidget(self.ui)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_customize)

        sa, sn = self.scene.style.arg_label, self.scene.style.notch

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
                
        self.hollow_item = HollowItem(200, 20)

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
        sty, sa, sn = None, self.scene.style.arg_label, self.scene.style.notch
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
        current_color = QColor(getattr(self.scene.style.arg_label,
                                       attr, 'white'))
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
        palette, sa = frame.palette(), self.scene.style.arg_label
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
            
            self.hollow_item.height = self.ui.slider_io_plugged_height.value()
            self.hollow_item.io_male_start = QPointF(
                self.hollow_item.io_male_start.x(),
                self.ui.slider_io_notch_y0.value())

            self.arg_label.child_io = self.hollow_item
        else:
            self.arg_label.child_io = None
            
        self.arg_label.updateMetrics()


def main():
    app = QApplication(sys.argv)
    win = WinCustomizeArgLabel()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

