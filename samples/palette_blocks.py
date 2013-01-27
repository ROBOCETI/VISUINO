# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 21:44:12 2013

@author: Nelso
"""

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *

__all__ = ['GxPalette']

MY_BLOCKS = \
"""<?xml version="1.0"?>
   <blocks font_family="Verdana" font_size="10">
     <block name="digitalWrite" bk_color="blue" font_color="white"/>
     <block name="digitalRead" bk_color="lightgreen" font_color="black"/>
   </blocks>
"""

class GxBlock(QGraphicsItem):
    _V_PADD = 10
    _H_PADD = 10
    _ADJUST_RECT = 10
    
    def __init__(self, name, color, font, font_color, scene=None, parent=None):
        QGraphicsItem.__init__(self, parent, scene)
        
        self._name = name
        self._color = color
        self._font = font
        self._font_color = font_color
            
        self._last_colli = None            
            
        self._width, self._height = 100, 50
        self.updateMetrics()
        
        self.setFlags(QGraphicsItem.ItemIsMovable)
    
    def updateMetrics(self):
        
        metrics = QFontMetrics(self._font)
        self._width = 2*self._H_PADD + metrics.width(self._name)
        self._height = 2*self._V_PADD + metrics.height()
        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option=None, widget=None):
        
        painter.fillRect(self.boundingRect(), QColor(self._color))
        painter.setFont(self._font)
        painter.setPen(QPen(QColor(self._font_color)))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self._name)
        
    def getPixmap(self):
        
        pix = QPixmap(self.boundingRect().size().toSize())
        pix.fill(QColor(self._color))
        
        painter = QPainter(pix)        
        self.paint(painter)
    
        return pix
        
    def mouseMoveEvent(self, event):
        QGraphicsItem.mouseMoveEvent(self, event)
        
        colli = [x for x in self.scene().collidingItems(self)
                   if isinstance(x, GxBlock)]
        if colli and colli[0] is not self._last_colli:
            print "Collided with \'%s\' (%d)." % (colli[0]._name, id(colli[0]))
            self._last_colli = colli[0]
        
    def mouseReleaseEvent(self, event):
        QGraphicsItem.mouseReleaseEvent(self, event)
        
        mouse_grabber = self.scene().mouseGrabberItem()
        if mouse_grabber and mouse_grabber is self:
            self.ungrabMouse()        
        
        colli_palette = [x for x in self.scene().collidingItems(self)
                           if isinstance(x, GxPalette)]
        if colli_palette:
            self.scene().removeItem(self)
        
        self._last_colli = None
            
                
class GxPalette(QGraphicsProxyWidget):
    
    _H_PADD = 10
    _START_V_PADD = 20    
    _ITEM_PADD = 10
    
    def __init__(self, parent_scene, xml_blocks, parent=None):
        """
        :parent_scene: QGraphicsScene
        :xml_blocks: QString. Well formed XML with block attributes.
        """
        QGraphicsProxyWidget.__init__(self)

        self.parent_scene = parent_scene        
        
        self._palette_scene = QGraphicsScene()
        self._palette_scene.setSceneRect(0, 0, 400, 1000)
        
        self._palette_view = QGraphicsView(self._palette_scene, parent=None)
        self._palette_view.setGeometry(0, 0, 200, 600)
        self._palette_view.centerOn(0, 0)
        self.setWidget(self._palette_view)
        
        self.parent_scene.addItem(self)
        self._parseBlocks(xml_blocks)
        
    def _parseBlocks(self, xml_string):
        
        blocks, font_blocks = [], {"family": "Consolas", "size": 12}
        
        xml = QXmlStreamReader(xml_string)
        xml.readNext()  # start document
    
        while not xml.atEnd():
            
            if xml.isStartElement() and xml.name() == "blocks":
                attr = xml.attributes()
                if attr.hasAttribute("font_family"):
                    font_blocks["family"] = attr.value("font_family").toString()
                if attr.hasAttribute("font_size"):
                    font_blocks["size"] = attr.value("font_size").toString()
            
            if xml.isStartElement() and xml.name() == "block":
                attr = xml.attributes()
                
                blocks.append({
                    "name": attr.value("name").toString(),
                    "bk_color": attr.value("bk_color").toString(),
                    "font_color": attr.value("font_color").toString()})
        
            xml.readNextStartElement()            
            
        pos_y = self._START_V_PADD                
        font = QFont(font_blocks["family"], int(font_blocks["size"]))
        
        for x in blocks:
            new_block = GxBlock(x["name"], x["bk_color"], font, 
                                x["font_color"], self._palette_scene)                                
            new_block.setPos(self._H_PADD, pos_y)
            new_block.setFlag(QGraphicsItem.ItemIsMovable, False)
            
            pos_y += new_block.boundingRect().height() + self._ITEM_PADD
            
            
    def mousePressEvent(self, event):
        QGraphicsProxyWidget.mousePressEvent(self, event)
        
        block_icon = self._palette_view.itemAt(event.pos().toPoint())
        if not block_icon:
            return
                    
        new_block = GxBlock(block_icon._name, block_icon._color, 
                            block_icon._font, block_icon._font_color,
                            self.parent_scene)
        new_block.setPos(block_icon.pos().x() + 1, block_icon.pos().y() + 1)        
        new_block.grabMouse()
        
        print "Created new block..."
    
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(100, 100, 1000, 600)
    
    scene = BaseScene()
    scene.setSceneRect(0, 0, 1000, 1000)
    scene.setBackgroundBrush(Qt.white)
    scene.setClickToFront(True)
    
    palette = GxPalette(scene, MY_BLOCKS)
        
    view = BaseView(scene, parent=win, wheel_zoom=False)
    view.centerOn(0, 0)    
    
    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())
