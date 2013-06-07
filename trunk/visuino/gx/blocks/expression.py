#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function
import sys
if __name__ == '__main__':
    sys.path.append('../../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from visuino.gx.bases import *
from visuino.gx.connections import *
from visuino.gx.utils import *
from visuino.gx.shapes import *

from visuino.settings import VGS

__all__ = ['GxExpression']

'''
expression:
    - {'tag': 'field'}
    - {'tag': 'operator', 'kind': '+'}
    - {'tag': 'variable', 'value': 'led_pin'}
    - {'tas': }
'''

class GxBlockExpression(GxPluggableBlock):
    '''
    '''
    def __init__(self, scene=None, parent=None):
        '''
        :param scene: ``GxSceneBlocks``
        :param parent: ``GxBlock``
        '''
        QGraphicsItem.__init__(self, parent, scene)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        
        self._element = [{'tag': 'field'}]
        
        self.updateMetrics()

    def updateMetrics(self):
        '''
        Recalculate its dimensions based on the current elements.
        '''
        # style expression
        se = VGS['styles']['block_expression']
        h_padd, v_padd = se['padding']['horizontal'], se['padding']['vertical']
        
        self._width, self._height = h_padd, 0
        
        # x coordinate (initial value)
        x = h_padd
        for e in self._element:
            new_element = None
            
            if e['tag'] == 'field':
                new_element = GxField(self.scene(), parent=self)
                
            if new_element:
                new_element.setPos(self._width, v_padd)
                new_element.setParentItem(self)
                
                self._width += new_element.getWidth()
                self._height = max(self._height, new_element.getHeight())

        
        self._width += h_padd

    def paint(self, painter, option, widget=None):
        # style expression
        se = VGS['styles']['block_expression']
        
        painter.fillRect(self.boundingRect(), QColor(se['background_color']))


class GxField(GxPluggableBlock):
    '''
    '''
    def __init__(self, scene, parent):
        '''
        :param scene: ``GxSceneBlocks``
        :param parent: ``GxExpression``
        '''
        GxPluggableBlock.__init__(self, scene, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        
        self._width, self._height = 50, 50
        
    def updateMetrics(self):
        self.prepareGeometryChange()
                
        se, sn = VGS['styles']['block_expression'], VGS['styles']['notch']
        padd = se['field_padd']
        iow, ioh = sn['io_size']['width'], sn['io_size']['height']
        bw = se['border_width']/2
        
        path = GxPainterPath(QPointF(bw + iow, bw))
        path.lineToInc(dy = padd)
        NotchPath.connect(path, QSizeF(iow, ioh), sn['io_shape'], '-j', 'left')
        path.lineToInc(dy = padd)
        path.lineToInc(dx = 2*ioh)
        path.lineTo(path.x, bw)
        path.closeSubpath()
        self._border_path = path
        
        self.update()

    def paint(self, painter, option=None, widget=None):
        '''
        '''
        # style expression
        se = VGS['styles']['block_expression']        
        
        painter.fillRect(self.boundingRect(), Qt.white)
        painter.setBrush(QColor(se['field_color']))
        painter.setPen(QPen(QColor(se['border_color'])))
    

class GxOperatorSymbol(QGraphicsItem):
    """
    Holds the operator symbol as a graphical text object.

    Special graphical item where the text appears vertical centralized
    as respect to some given 'max_height'. The width of the bounding
    rect will be the width of the text.
    """

    _V_PADD_FIX = -5

    def __init__(self, op_symbol, style_scheme, max_height,
                 parent=None, scene=None):
        """
        :op_symbol: str.
        :style_scheme: dict  {'font': QFont(), 'color': QColor()}
        """
        QGraphicsItem.__init__(self, parent, scene)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self._op_symbol = op_symbol
        self._style_scheme = style_scheme
        self._width = QFontMetrics(self._style_scheme['font']) \
                        .width(self._op_symbol)
        self._height = max_height

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)
        painter.setFont(self._style_scheme['font'])
        painter.setPen(QPen(self._style_scheme['color']))
        rect = self.boundingRect()
        rect.setTop(self._V_PADD_FIX)
        painter.drawText(rect, Qt.AlignCenter,
                         self._op_symbol)


class GxProxyInputField(QGraphicsProxyWidget):
    """
    Features added:

        - On mouse click events, brings its "grandpa" GxExpression to the
          front of the GxScene. OBS: Its parent is a GxField.

        - On context menu event, raises some QMenu() as specified on the
          self._context_menu attribute.
    """
    def __init__(self, context_menu=None, parent=None):
        QGraphicsProxyWidget.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self._context_menu = context_menu

    def mousePressEvent(self, event):
        QGraphicsProxyWidget.mousePressEvent(self, event)
        self.scene().bringToFront(self.parentItem().parentItem())

        if event.button() == Qt.MidButton:
            self.parentItem()._removeInputField()

    def contextMenuEvent(self, event):
        self.parentItem()._enableActionsRemove()
        if isinstance(self._context_menu, QMenu):
            self._context_menu.popup(event.screenPos())


class EditInputField(QLineEdit):
    """
    Features added:

        - Variable width, which will always be big enough (and only that
          big) to contain its text. Call updateMetrics() on the field
          parent (GxField) when the width is updated.
    """
    def __init__(self, field_parent, font=None):
        """
        :field_parent: GxField().
        :font: QFont().
        """
        QLineEdit.__init__(self)

        self._field_parent = field_parent
        self._metrics = QFontMetrics(self.font())

        self.connect(self, SIGNAL('textChanged(const QString&)'),
                     self._onTextChanged)

        if isinstance(font, QFont):
            self.setFont(font)
        else:
            self.updateWidth()

        self.setFrame(False)
        self.setAlignment(Qt.AlignCenter)


    def setFont(self, font):
        """
        :font: QFont().
        """
        QLineEdit.setFont(self, font)
        self._metrics = QFontMetrics(font)
        self.updateWidth()

    def updateWidth(self):
        """
        Update its x-dimension and also call updateMetrics() on the
        GxField parent, if any.
        """
        min_width = self._metrics.width('MMi')
        new_width = self._metrics.width(self.text())
        if len(self.text()) > 2:
            self.setFixedWidth(new_width + 10)
        else:
            self.setFixedWidth(min_width)

        if isinstance(self._field_parent, GxField):
            self._field_parent.updateMetrics()

    def _onTextChanged(self):
        """
        Every time that text change, its dimension will be updated to
        comport the new text.
        """
        self.updateWidth()


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(300, 200, 600, 400)
    scene = GxSceneBlocks()

    gx_exp = GxBlockExpression(scene)
    gx_exp.setPos(100, 100)

    view = GxView(scene, parent=win)
    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()