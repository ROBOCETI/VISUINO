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

from visuino.settings import VGS

__all__ = ['GxArgLabel']

class GxArgLabel(GxPluggableBlock):
    '''
    Shape that represents argument names to be used on function call blocks.
    It has a female IO notch on the right and resizes itself according to the 
    plugged male IO block.
    '''

    def __init__(self, arg_info, scene=None, parent=None, **kwargs):
        ''' (dict, GxSceneBlocks, GxBlock, **)

        kwargs:
            @ fixed_width: number <None>
            @ update_parent: True <False>
        '''
        GxPluggableBlock.__init__(self, scene, parent)
        self.mouse_active = False
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
        return VGS['styles']['block_arg_label']['border_width']      

    def setFixedWidth(self, width):
        ''' (number) -> NoneType
        '''
        self._fixed_width = width
        self.updateMetrics()

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        sa = VGS['styles']['block_arg_label']
        painter.fillRect(self.boundingRect(), Qt.transparent)

        # drawing the filled border path
        painter.setPen(QPen(QColor(sa['border_color']), sa['border_width'],
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(sa['background_color']))
        painter.drawPath(self._border_path)

        # drawing the name
        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(sa['font_color'])))
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

        sa, sn = VGS['styles']['block_arg_label'], VGS['styles']['notch']       

        self._name_font = QFont(sa['font_family'], sa['font_size'])

        # border corrections
        bw = sa['border_width']/2

        # main dimensions
        metrics = QFontMetricsF(self._name_font)
        nw, nh = metrics.width(self._arg_info['name']), metrics.height()
        fvc = sa['font_vcorrection']
        hp, vp = sa['padding']['horizontal'], sa['padding']['vertical']
        cw, ch = sa['corner_size']['width'], sa['corner_size']['height']
        c_shape = sa['corner_shape']
        iow, ioh = sn['io_size']['width'], sn['io_size']['height']

        io_notch_shape = sn['io_shape'] + '/' + str(sn['io_basis'])
        io_notch_size = QSizeF(iow, ioh)        

        # corner corrections (occours if corner rect intercepts name rect)
        ccw = cw - hp #if cw > hp else -(hp - cw)
        cch = ch - vp #if ch > vp else -(vp - ch)

        # default dimensions of the border path
        W = cw - ccw + nw + hp + iow
        H = 2*ch - 2*cch + max(nh, ioh)

        # prevents overlaping of corner height and vertical padding
        if 2*ch > H:
            ch = H/2

        c_size = QSizeF(cw, ch)

        if self.child_io:
            H = self.child_io.getHeight()
        if self._fixed_width is not None:
            W = self._fixed_width

        # starts on the top-right corner
        path = GxPainterPath(QPointF(W + bw, bw))
        path.lineToInc(dx = - W + cw)
        CornerPath.connect(path, c_size, c_shape, 'top-left', False)
        path.lineToInc(dy = H - 2*ch)
        CornerPath.connect(path, c_size, c_shape, 'bottom-left', False)
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

        self.arg_label = GxArgLabel({'name': 'value', 'type': 'const', 
                                     'restriction': 'HIGH,LOW'}, self.scene)
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
        
        self.hollow_item = HollowItem(200, 20) 
        
        sa, sn = VGS['styles']['block_arg_label'], VGS['styles']['notch']
        
        self._setupSignal(self.ui.spinbox_hpadd, sa['padding'], 'horizontal')        
        self._setupSignal(self.ui.spinbox_vpadd, sa['padding'], 'vertical') 
        self._setupSignal(self.ui.spinbox_font_vcorrection, sa) 
        
        self._setupSignal(self.ui.spinbox_font_size, sa)
        self._setupSignal(self.ui.frame_font_color, sa)
        self._setupSignal(self.ui.combobox_font_family, sa)
        
        self._setupSignal(self.ui.frame_border_color, sa)
        self._setupSignal(self.ui.spinbox_border_width, sa)        
        self._setupSignal(self.ui.frame_background_color, sa)
        
        self._setupSignal(self.ui.combobox_corner_shape, sa)

        self._setupSignal(self.ui.spinbox_corner_width, sa['corner_size'], 
                          'width')
        self._setupSignal(self.ui.spinbox_corner_height, sa['corner_size'], 
                          'height')
                          
        self._setupSignal(self.ui.combobox_io_shape, sn)
        self._setupSignal(self.ui.slider_io_basis, sn)
        self._setupSignal(self.ui.spinbox_io_width, sn['io_size'], 
                          'width')
        self._setupSignal(self.ui.spinbox_io_height, sn['io_size'], 
                          'height')                        
   
        self.ui.checkbox_plug_io.stateChanged[int].connect(
            self._updatePluggedIO)
        self.ui.slider_io_plugged_height.valueChanged[int].connect(
            self._updatePluggedIO)
        self.ui.slider_io_notch_y0.valueChanged[int].connect(
            self._updatePluggedIO)


    def _setupSignal(self, sender, style, attr=None):
        '''
        :param sender: ``QObject``
        :param style: ``dict``
        :param attr: ``str`` <None>
            Attribute name (key on the style dict)
        '''        
        if attr is None:
            n = str(sender.objectName())
            attr = n[n.find('_')+1:]
            
        if attr not in style:
            return
            
        if isinstance(sender, QSpinBox):
            sender.setValue(int(style[attr]))
            sender.valueChanged[int].connect(
                lambda: self._updateStyle(style, attr, sender.value()))

        elif isinstance(sender, QComboBox):
            sender.setCurrentIndex(sender.findText(str(style[attr])))
            sender.currentIndexChanged[int].connect(
                lambda: self._updateStyle(style, attr,
                                          str(sender.currentText())))

        elif isinstance(sender, QSlider):
            sender.setValue(int(style[attr])*100)
            sender.valueChanged[int].connect(
                lambda: self._updateStyle(style, attr,
                                          float(sender.value()/100)))
                                          
        elif isinstance(sender, QFrame) and not isinstance(sender, QLabel):
            palette = sender.palette()
            palette.setColor(QPalette.Background, QColor(style[attr]))
            sender.setPalette(palette)
            sender.mousePressEvent = \
                lambda event: self._chooseColor(sender, attr)
                

    def _chooseColor(self, frame, attr):
        ''' (QFrame, str) -> NoneType

        Saves the current color as 'old_color', then launch the color dialog.
        Changes on the dialog are reflected immediately on the GxArgLabel.
        If the dialog is cancelled, restores 'old_color'.
        '''
        palette, sa = frame.palette(), VGS['styles']['block_arg_label']
        old_color = palette.background().color()
        color_dialog = QColorDialog(old_color)

        color_dialog.currentColorChanged[QColor].connect(
            lambda: self._updateStyle(sa, attr,
                    str(color_dialog.currentColor().name())))

        answer = color_dialog.exec_()
        if answer == 1:
            new_color = color_dialog.currentColor()
            palette.setColor(QPalette.Background, new_color)
            frame.setPalette(palette)
            self._updateStyle(sa, attr, str(new_color.name()))
        else:
            self._updateStyle(sa, attr, str(old_color.name()))

        
    def _updateStyle(self, style, attr, value):
        style[attr] = value
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

