# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 01:55:27 2013

@author: Nelso
"""

from __future__ import division
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *
from field_info import *

class GxInputField(QGraphicsItem):
    H_PADD = 10
    V_PADD = 10
    
    def __init__(self, field_info, height, style_scheme, scene, parent=None):
        QGraphicsItem.__init__(self, parent, scene)
        
        self._style_scheme = style_scheme
        
        if not isinstance(field_info, FieldInfo):
            raise ValueError("Parameter 'field_info' must be of type" + \
                "FieldInfo. Was given %s." % field_info.__class__.__name__)
                
        self._field_info = field_info        
        self._proxy_widget = self.GxProxyToFront(self)
        self._widget = field_info.getWidget()
        self._widget.setFont(self._style_scheme['font'])
        self._proxy_widget.setWidget(self._widget)
        
        
        self._width = 2 * self.H_PADD
        self._height = 200, int(height)
        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def _updateMetrics(self):
        self._width = 2 * self.H_PADD + self._name_width + self._DX_NOTCH

    def paint(self, painter, option, widget=None):

        padd_width = self.LINE_WIDTH        
        
        
    class GxProxyToFront(QGraphicsProxyWidget):
        """
        New feature added: when clicked, brings its parent on the top
        of the scene.
        """
        def mousePressEvent(self, event):
            QGraphicsProxyWidget.mousePressEvent(self, event)
            self.scene().bringToFront(self.parentItem())        
        
        
        
        

class GxArgLabel(QGraphicsItem):
    H_PADD = 10       # horizontal padding

    LINE_WIDTH = 2

    def __init__(self, name, style_scheme, height, dx_notch,
                 scene=None, parent=None):
        QGraphicsItem.__init__(self, parent, scene)

        self._name = str(name)
        self._style_scheme = style_scheme

        # setting up dimensions
        self._width, self._height = 200, height
        self._DX_NOTCH = dx_notch

        self.setBoundingRegionGranularity(1)

        self._updateMetrics()

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def _updateMetrics(self):

        name_metrics = QFontMetrics(self._style_scheme['font'])
        self._name_width = name_metrics.boundingRect(self._name).width()

        self._width = 2 * self.H_PADD + self._name_width + self._DX_NOTCH

    def paint(self, painter, option, widget=None):

        padd_width = self.LINE_WIDTH

        painter.fillRect(self.boundingRect(), Qt.transparent)

        pen = QPen(self._style_scheme['border_color'], self.LINE_WIDTH,
                   cap=Qt.RoundCap, join=Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self._style_scheme['backg_color'])

        path = QPainterPath(QPointF(padd_width, padd_width))
        path.lineTo(padd_width, self._height - padd_width)
        path.lineTo(self._width - padd_width,
                    self._height - padd_width)
        path.lineTo(self._width - self._DX_NOTCH, self._height/2)
        path.lineTo(self._width - padd_width, padd_width)
        path.lineTo(padd_width, padd_width)

        painter.drawPath(path)
        
        painter.setFont(self._style_scheme['font'])
        painter.setPen(QPen(self._style_scheme['text_color']))
        painter.drawText(QRect(0, 0,
                               self._width - self._DX_NOTCH, self._height),
                         Qt.AlignCenter, self._name)            


class GxFunctionCall(QGraphicsItem):

    H_PADD = 10         # horizontal padding
    V_PADD = 10         # vertical padding
    ARG_VPADD = 0       # argument vertical padding

    DX_NOTCH = 20       # horizontal size of the notch
    DY_PIPE = 15

    LINE_WIDTH = 2

    def __init__(self, name, args, style_scheme, scene=None, parent=None):
        QGraphicsItem.__init__(self, parent, scene)

        self._name = str(name)
        self._style_scheme = style_scheme
        self._args = []
        for i, a in enumerate(args):
            if not isinstance(a, FieldInfo):
                raise ValueError(
                    'Argument %d is not instance of FieldInfo.' % i + \
                    ' Givem %s instead.' % a.__class__.__name__)
            self._args.append({'info': a})

        self.setFlags(QGraphicsItem.ItemIsFocusable |
                      QGraphicsItem.ItemIsMovable)

        self.setBoundingRegionGranularity(1)
        
        # setting up dimensions
        self._width, self._height = 200, 100
        self._draw_pipe = False

        self._updateMetrics()
        self._setupArgLabels()
        
    def _setupArgLabels(self):
        
        x, y = self._width , 0
        
        if self._draw_pipe:
            x += 3 * self.DY_PIPE - self.LINE_WIDTH - 5    
        
        for a in self._args:
            a['label'] = GxArgLabel(a['info'].name, 
                self._style_scheme['input_field'], self._height, 
                self.DX_NOTCH, self.scene(), self)
            a['label'].setPos(x, y)
            y += self._height + self.ARG_VPADD
            

    def _updateMetrics(self):

        name_metrics = QFontMetrics(self._style_scheme['name']['font'])
        self._name_width = name_metrics.boundingRect(self._name).width()
        self._name_height = name_metrics.boundingRect(self._name).height()

        self._width = 2 * self.H_PADD + self._name_width + self.DX_NOTCH
        self._height = 2 * self.V_PADD + self._name_height

    def boundingRect(self):
        return QRectF(-5, -5, self._width + 5, self._height + 5)

    def paint(self, painter, option, widget=None):

        padd_width = self.LINE_WIDTH

        painter.fillRect(self.boundingRect(), Qt.transparent)
        
#        self._drawPipe(painter)

        pen = QPen(self._style_scheme['name']['border_color'], 
                   self.LINE_WIDTH, cap=Qt.RoundCap, join=Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self._style_scheme['name']['backg_color'])

        path = QPainterPath(QPointF(self.DX_NOTCH, padd_width))
        path.lineTo(padd_width, self._height/2)
        path.lineTo(self.DX_NOTCH, self._height-padd_width)
        path.lineTo(self._width - padd_width, self._height-padd_width)
        path.lineTo(self._width - padd_width, padd_width)
        path.lineTo(self.DX_NOTCH, padd_width)

        painter.drawPath(path)

        painter.setPen(QPen(self._style_scheme['name']['text_color']))
        painter.setFont(self._style_scheme['name']['font'])
        painter.drawText(QRect(self.DX_NOTCH, 0,
                               self._width - self.DX_NOTCH, self._height),
                         Qt.AlignCenter, self._name)
                         
    
    def _drawPipe(self, painter):
        padd_width = self.LINE_WIDTH
        
        pen = QPen(self._style_scheme['name']['border_color'], 
                   self.LINE_WIDTH, cap=Qt.RoundCap, join=Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self._style_scheme['name']['pipe_color'])
    
        arg_pipe_vspace = (self._height/2 - self.DY_PIPE/2)
        p = {'x': self._width - padd_width, 
             'y': self._height/2 - self.DY_PIPE/2}
        p['path'] = QPainterPath(QPointF(p['x'], p['y']))
    
        self._pathLineInc(p, 3*self.DY_PIPE, 0)
        self._pathLineInc(p, 0, self.DY_PIPE)
        self._pathLineInc(p, -self.DY_PIPE, 0)        
        self._pathLineInc(p, 0, 2*arg_pipe_vspace + self.ARG_VPADD)         
        self._pathLineInc(p, self.DY_PIPE, 0)                
        self._pathLineInc(p, 0, self.DY_PIPE) 
        self._pathLineInc(p, -2 * self.DY_PIPE, 0)         
        self._pathLineInc(p, 0, 
            -(self.DY_PIPE + 2*arg_pipe_vspace + self.ARG_VPADD))         
        self._pathLineInc(p, -self.DY_PIPE, 0) 
        
        painter.drawPath(p['path'])        
        
    def _pathLineInc(self, p, inc_x, inc_y):
        p['x'] += inc_x
        p['y'] += inc_y
        p['path'].lineTo(p['x'], p['y'])

def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()

    font_color_scheme = {'name': {'font': QFont('Verdana', 16),
                                  'text_color': QColor('white'),
                                  'backg_color': QColor('blue'),
                                  'border_color': QColor('black'),
                                  'pipe_color': QColor('orange')},
                         'input_field': {'font': QFont('Verdana', 12),
                                         'text_color': QColor('black'),
                                         'backg_color': QColor('yellow'),
                                         'border_color': QColor('black')}}

    block_digital_write = GxFunctionCall('digitalWrite',
        [FieldInfo('pin', 'int', '0|13', 'combobox'),
         FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
        font_color_scheme, scene)
        
    block_digital_write.setPos(100, 100)
    
    block_digital_read = GxFunctionCall('digitalRead',
        [FieldInfo('pin', 'int', '0|13', 'combobox')],
        font_color_scheme, scene)
        
    block_digital_read.setPos(200, 300)
    

    view = GxView(scene, win)

    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()