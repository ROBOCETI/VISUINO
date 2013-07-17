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
from visuino.gx.connections import *
from visuino.gx.blocks.arg_label import GxArgLabel

from visuino.settings import VGS

__all__ = ['GxBlockFunctionCall']

class GxBlockFunctionCall(GxPluggableBlock):
    '''
    Block that represents the function call syntax on imperative languages.
    For instance, a funcion call in C or even in Python given by:

        function_name(arg1, arg2, ..., argN)

    On this block, each argument is given by an GxArgLabel object and the 
    function return (optional) is indicated signaled by a male IO connector 
    on the left side.

    Attributes:
        _def: FunctionDefiniton. Saves all information about the function.

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

    def __init__(self, definition, scene):
        ''' (dict, GxSceneBlocks, QGraphicsItem)
        '''
        GxPluggableBlock.__init__(self, scene)
        
        self._def = definition

        self._element = {'block': 'function_call', 
             'name': definition['name'],
             'library': definition['library'],
             'args': None if definition['args'] is None else
                          [None for x in definition['args']]}

        self._name_rect = self.boundingRect()        
        self._args_labels = []  # list of GxArgLabel
        self._args_height = 0

        self.setupArgLabels()
        self.updateMetrics()

        for arg in self._args_labels:
            arg.update_parent = True
            
    def __repr__(self):
        return "<GxBlockFunctionCall '%s'>" % str(self._def['name'])
    
    @property
    def args_labels(self):
        return self._args_labels
        
    @property
    def definition(self):
        return self._def        
        
    def getBorderWidth(self):
        ''' () -> int
        '''
        return VGS['styles']['block_function_call']['border_width']
            
    def cloneMe(self, scene):
        ''' (GxSceneBlocks) -> GxBlockFunctionCall
        '''
        return GxBlockFunctionCall(self._def, scene)                                   

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGraphicsItem,
                                QWidget widget=None) -> NoneType
        '''
        sfc = VGS['styles']['block_function_call']

        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(
            QBrush(QColor(sfc['border_color'])), sfc['border_width'],
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(sfc['background_color']))
        painter.drawPath(self._border_path)

        painter.setFont(self._name_font)
        painter.setPen(QPen(QColor(sfc['name_font_color'])))
        painter.drawText(self._name_rect, Qt.AlignVCenter | Qt.AlignLeft, 
                         self._def['name'])

        if self.isSelected():
            painter.setPen(Qt.DashLine)
            painter.setBrush(Qt.transparent)
            painter.drawRect(self.boundingRect())

    def setupArgLabels(self):
        ''' () -> NoneType

        Should be called whenever self._args changes.
        '''
        if self._def['args'] is None:
            return
        sa, sn = VGS['styles']['block_arg_label'], VGS['styles']['notch']

        for arg in self._args_labels:
            arg.removeFromScene()
        self._args_labels = []

        max_width = 0
        self._args_height = 0
        for i, arg_info in enumerate(self._def['args']):

            new_label = GxArgLabel(arg_info, self.scene(), parent=self,
                                   update_parent=False)
            new_label.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
            new_label.setPos(0, i*50)
##                new_label.setVisible(False)
            w = new_label.getWidth()

            max_width = w if w > max_width else max_width
            self._args_labels.append(new_label)

        for arg in self._args_labels:
            arg.setFixedWidth(max_width)
            arg.update_parent = True
    

    def updateMetrics(self):
        ''' () -> NoneType
        '''
        self.prepareGeometryChange()
        self.old_size = self.boundingRect().size()

        style_fc = VGS['styles']['block_function_call']
        style_notch = VGS['styles']['notch']
        npadd, c_size = style_fc['name_padding'], style_fc['corner_size']

        # half of the border width, for use as correction
        bw = style_fc['border_width']/2

        self._name_font = QFont(style_fc['name_font_family'],
                                style_fc['name_font_size'])
        name_metrics = QFontMetricsF(self._name_font)

        # setting up nice short names for all the metrics
        nw, nh = name_metrics.width(self._def['name']), name_metrics.height()
        fvc = style_fc['name_vcorrection']
        hp, vp = npadd['horizontal'], npadd['vertical']
#        bp = style_fc['bottom_padd']
        cw, ch = c_size['width'], c_size['height']
        malp = style_fc['arg_min_left_padd']
        asp = style_fc['arg_spacing']
        iow, ioh = style_notch['io_size']['width'], style_notch['io_size']['height']
        vfw, vfh = style_notch['vf_size']['width'], style_notch['vf_size']['height']
        vfs = bw + style_notch['vf_x0']

        corner_shape = style_fc['corner_shape']
        corner_size = QSizeF(cw, ch)
        io_shape = style_notch['io_shape'] + '/' + str(style_notch['io_basis'])
        io_size = QSizeF(iow, ioh)
        vf_shape = style_notch['vf_shape'] + '/' + str(style_notch['vf_basis'])
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

        if self._args_labels:
            self._args_height += (len(self._args_labels) - 1) * \
                style_fc['arg_spacing']

        if self._def['return_type']:
            # height from the top up to the args y0
            args_y0 = max(vp, ch) + nh + vp
            name_y0 = args_y0 - vp - nh

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
            H = args_y0 + self._args_height + ch + vfh

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

#        print('Updating connectors GxBlockFunctionCall ', self._name)
        self.updateConnections()
        self.update(self.boundingRect())

        if isinstance(self.parentItem(), GxBlock):
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

    def updateDefinition(self, **kwargs):
        ''' (kwargs) -> NoneType

        Set its arguments information, and also update the graphics.
        '''
        for x in ('name', 'return_type', 'args'):
            if x in kwargs:
                self._def[x] = kwargs[x]
                if x == 'args':
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

        self.scene = GxSceneBlocks()
        
        self.block_function_call = GxBlockFunctionCall(
            {'name': 'digitalWrite', 'return_type': None, 'library': 'Arduino.h',
             'args': [{'name': 'pin', 'type': 'int'},
                      {'name': 'value', 'type': 'int'}]}, self.scene)

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
            lambda: self.block_function_call.updateDefinition(name=
                    self.ui.edit_fc_name.text()))
                    
        self.ui.checkbox_fc_return.stateChanged[int].connect(
            lambda: self.block_function_call.updateDefinition(return_type=
                    'int' if self.ui.checkbox_fc_return.isChecked() else None))
            
        self.ui.edit_fc_args.textChanged[str].connect(
            lambda: self._updateFunctionArgs(self.ui.edit_fc_args.text()))
            
        # UI name convention:
        #   widget kind + '_' + tab identifier + '_' + style attribute        

        sfc = VGS['styles']['block_function_call']
        sa = VGS['styles']['block_arg_label']
        sn = VGS['styles']['notch']        

        s_tabs = {'fc': sfc, 'arg': sa, 'nch': sn, 'fcnp': sfc['name_padding'],
                  'fccs': sfc['corner_size'], 'argpd': sa['padding'],
                  'argcs': sa['corner_size'], 'vfsz': sn['vf_size'],
                  'iosz': sn['io_size']}
                  
        for name, wg in self.ui.__dict__.items():
            suffix = name[name.find('_')+1:]
            tab_prefix = suffix[:suffix.find('_')]
            attr = suffix[suffix.find('_')+1:]
            
            if isinstance(wg, (QSpinBox, QComboBox, QSlider)):
                self._setupSignal(wg, s_tabs[tab_prefix], attr)
            elif isinstance(wg, QFrame) and not isinstance(wg, QLabel):
                # those QFrame are for color selection
                self._setupFrameClick(wg, s_tabs[tab_prefix], attr)                  

    def _updateFunctionArgs(self, text):
        self.args, text = [], str(text)
        if len(text.strip()) != 0:
            for x in [x.strip() for x in text.split(',')]:
                self.args.append({'name': x, 'type': 'int', 'restriction': None})
        self.block_function_call.updateDefinition(args=self.args)

    def _updateStyle(self, style, attr, value):
        style[attr] = value
        self.block_function_call.setupArgLabels()
        self.block_function_call.updateMetrics()

    def _setupSignal(self, sender, style, attr):
        ''' (QSpinBox/QComboBox/QSlider, str) -> NoneType

        Configures on the sender widget the current value of 'attr' in 'style',
        and also setup its suitable signal to customization changes.
        '''
        if attr not in style:
            return
            
        if isinstance(sender, QSpinBox):
            sender.setValue(style.get(attr, 0))
            sender.valueChanged[int].connect(
                lambda: self._updateStyle(style, attr, sender.value()))

        elif isinstance(sender, QComboBox):
            sender.setCurrentIndex(sender.findText(style.get(attr, '')))
            sender.currentIndexChanged[int].connect(
                lambda: self._updateStyle(style, attr,
                                           str(sender.currentText())))

        elif isinstance(sender, QSlider):
            if attr == 'vf_x0':
                sender.setValue(style.get(attr, 0))
                sender.valueChanged[int].connect(
                    lambda: self._updateStyle(style, attr,
                                              float(sender.value())))
            else:
                sender.setValue(style.get(attr, 0)*100)
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
        current_color = QColor(style.get(attr, 'white'))
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
