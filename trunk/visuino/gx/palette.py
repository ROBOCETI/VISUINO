#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements a palette for blocks drag and drop.
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
    sys.path.append('../../')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from visuino.gx.bases import *
from visuino.gx.blocks import *
from visuino.gx.styles import *
from visuino.resources import *

from visuino.core.sketch import SketchBlocks
from visuino.core.lib_defs import LibraryDefinitions

from pprint import pprint

__all__ = ['GxPaletteLibrary', 'GxViewPalette']

class GxPaletteSection(QGraphicsItem):
    
    SPACING_SECTION = 2
    
    def __init__(self, scene, start_pos, title, definitions, palette):
        ''' (QGraphisScene, QPointF, str, list of dict, GxPaletteLibrary)
        '''
        QGraphicsItem.__init__(self, None, scene)
        
        self._title = title
        self._defs = definitions
        self._palette_lib = palette
        
        self._width, self._height = 250, 30
        self._background_color = 'black'
        self._font_color = 'white'
        self._font = QFont('Verdana', 9)
        self._spacing = 15
        self._total_height = self._height + self._spacing
        
        self.setPos(start_pos)
                
        self._blocks = []
        for definition in self._defs:
            new_block = GxBlockFunctionCall(definition, self.scene())
            new_block.setPos(5 if definition['return_type'] else 15, 0)
            new_block.setCacheMode(QGraphicsItem.DeviceCoordinateCache)                
            self._blocks.append(new_block)
            self._total_height += new_block.getHeight() + self._spacing

        self._updateBlocksPosition() 
        self._collapsed = True
        self.collapse()
        
        self.setAcceptHoverEvents(True)
        
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        
    @property
    def title(self):
        return self._title
        
    @property
    def bottom(self):
        return self.y() + self.getTotalHeight()        
        
    def getTotalHeight(self):
        if self._collapsed:
            return self._height + self.SPACING_SECTION
        else:
            return self._total_height + self.SPACING_SECTION
                        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, widget=None, option=None):
        painter.fillRect(self.boundingRect(), 
                         QColor(self._background_color))
        painter.setPen(QPen(QColor(self._font_color)))
        painter.setFont(self._font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter,
                         self._title)                         
                         
    def mousePressEvent(self, event):
        super(GxPaletteSection, self).mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:            
            if self._collapsed:
                self.expand()
            else:
                self.collapse()
                
    def expand(self):       
        for block in self._blocks:                      
            block.show()
        self._collapsed = False 
        self._palette_lib.updateSectionsBelow(self)

    def collapse(self):
        for block in self._blocks:
            block.hide()
        self._collapsed = True
        self._palette_lib.updateSectionsBelow(self)
        
    def _updateBlocksPosition(self):
        y_blocks = self.y() + self._height + self._spacing
        for block in self._blocks:                      
            block.setPos(block.x(), y_blocks)
            y_blocks += block.getHeight() + self._spacing
        
    def updatePosY(self, y):
        self.setPos(self.x(), y)
        self._updateBlocksPosition()
            
        
class GxPaletteResizer(QGraphicsItem):
    def __init__(self, palette, scene, parent=None):
        QGraphicsItem.__init__(self, parent, scene)
        self._palette = palette
        self._width, self._height = 10, self.scene().sceneRect().height()
        self._color = 'black'
        self.setPos(palette.x() + palette.boundingRect().width(), 0)
        self.setCursor(Qt.SizeHorCursor)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsScenePositionChanges)
        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), QColor(self._color))
        
    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemPositionChange and self.scene()):
            # value contains the new position
            new_pos = value
            new_pos.setY(self._palette.y()) 
            if self._palette.updateResize(new_pos):
                return new_pos
            else:
                return self.pos()
        else:
            return QGraphicsItem.itemChange(self, change, value)  
        

class GxPaletteLibrary(GxView):
    
    def __init__(self, lib_name, gx_palette, opengl):
        ''' (str, dict, GxPalette, bool)
        '''                
        self.lib_name = lib_name
        self.gx_palette = gx_palette
                
        self._scene = GxSceneBlocks(background_grid=False)
        self._scene.style = self.gx_palette.scene().style
        self._scene.setBackgroundBrush(QBrush(QColor(208, 214, 219)))
        self._scene.setSceneRect(0, 0, 500, 2000)
        
        GxView.__init__(self, self._scene, None, opengl)

        self.setDragMode(QGraphicsView.NoDrag)
        self.setFrameStyle(QFrame.NoFrame)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
            
        self._sections = []
        
        y_section = 0
        for sec_name, sec_defs in self.gx_palette.libs[self.lib_name]\
            ['palette_sections'].items():
            new_section = GxPaletteSection(self._scene, QPointF(0, y_section), 
                                           sec_name, sec_defs, self)
            y_section += new_section.getTotalHeight()
            self._sections.append(new_section)
        
        menu = QMenu()
        menu.addAction("Expand all", self.expandAll)
        menu.addAction("Collapse all", self.collapseAll)
        self.menu_expand_collapse_all = menu    
        
#        self.scale(0.85, 0.85)   
    
    def expandAll(self):
        for sec in self._sections:
            sec.expand()
        self.gx_palette.update(self.gx_palette.boundingRect())
            
    def collapseAll(self):
        for sec in self._sections:
            sec.collapse()
        self.centerOn(0, 0)
        self.gx_palette.update(self.gx_palette.boundingRect()) 
    
    def updateSectionsBelow(self, section):
        ''' (GxPaletteSection)
        '''
        found = False
        for i in range(0, len(self._sections)):
            if found:
                self._sections[i].updatePosY(self._sections[i-1].bottom)
            if self._sections[i] is section:
                found = True            
            
        return False
                     
    def mousePressEvent(self, event):
        ''' QGraphicsProxyWidget.mousePressEvent(
                QGraphicsSceneMouseEvent) -> None
        '''
        super(GxPaletteLibrary, self).mousePressEvent(event) 
        
        self.gx_palette.update(self.gx_palette.boundingRect()) 
        item_at = self.itemAt(event.pos())                
        
        if (isinstance(item_at, GxBlock) and 
              event.button() == Qt.LeftButton):
                  
            block_icon = item_at
            if item_at.parentItem():
                block_icon = item_at.parentItem()
    
            new_block = block_icon.cloneMe(self.gx_palette.scene())
            new_block.sketch = self.gx_palette.sketch
            self.gx_palette.sketch.addSnippet(new_block)
                        
            new_block.setFlags(QGraphicsItem.ItemIsMovable)
            new_block.setCacheMode(QGraphicsItem.ItemCoordinateCache)
            new_block.setCursor(Qt.OpenHandCursor)
            
            new_block.palette_blocks = self.gx_palette
            new_block.new_block = True
            
#            my_pos = self.mapTo(self.gx_palette.widget(), self.pos())                        
            icon_mapped_pos = self.mapFromScene(block_icon.pos())
            new_block.setPos(QPointF(
                self.gx_palette.pos().x() + icon_mapped_pos.x() + 2,
                self.gx_palette.pos().y() + icon_mapped_pos.y() + 2))
            
            self.gx_palette.scene().bringToFront(new_block)
            
            new_block.grabMouse()
            
    def mouseReleaseEvent(self, event):
        ''' QGraphicsProxyWidget.mouseReleaseEvent(
                QGraphicsSceneMouseEvent) -> None
        '''
        super(GxPaletteLibrary, self).mouseReleaseEvent(event)
        self.gx_palette.update(self.gx_palette.boundingRect())         
        
        
class GxPalette(QGraphicsProxyWidget):
    MINIMUM_WIDTH = 200
    MAXIMUM_WIDTH = 400
    
    def __init__(self, libs, sketch, scene, opengl):
        ''' (LibraryDefinitions, GxSceneBlocks, bool)
        '''
        QGraphicsProxyWidget.__init__(self)
        
        if isinstance(scene, QGraphicsScene):
            scene.addItem(self)
        
        self.libs = libs
        self.sketch = sketch
        self._opengl = opengl
        
        self.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
        
        self._view = GxPaletteLibrary('Arduino.h', self, opengl)
        self._view.setGeometry(0, 0, 250, 600)
        self.setWidget(self._view)        
            
        self.cursor_collide = QCursor(
            QPixmap(':delete_icon.png').scaled(64, 64))
        self.cursor_add = QCursor(
            QPixmap(':add_icon.png').scaled(64, 64))
            
        self._resizer = GxPaletteResizer(self, self.scene())
        
        self.setAcceptHoverEvents(True)        

    def hoverMoveEvent(self, event):
        item_at = self._view.itemAt(event.pos().toPoint())
        if isinstance(item_at, GxPaletteSection):
            self.setCursor(Qt.PointingHandCursor)
        elif isinstance(item_at, GxBlock):
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        
    def updateHeight(self, new_height):
        self.prepareGeometryChange()
        self.widget().setFixedHeight(new_height)
        self.update(self.boundingRect())
        
    def updateResize(self, resizer_pos):
        new_width = resizer_pos.x() - self.x()
        
        if (new_width > self.MINIMUM_WIDTH and
            new_width < self.MAXIMUM_WIDTH):
                
            self.prepareGeometryChange()
            self.widget().setGeometry(0, 0, new_width, 
                                      self.boundingRect().height())
            self.update(self.boundingRect())
            
            return True
            
    def mousePressEvent(self, event):
        super(GxPalette, self).mousePressEvent(event)
        
        if (isinstance(self._view.itemAt(event.pos().toPoint()), 
                       GxPaletteSection) and 
            event.button() == Qt.RightButton):
            
            self._view.menu_expand_collapse_all.popup(event.screenPos())            
        

class GxViewPalette(GxView):
    def __init__(self, parent=None, opengl=False):
        ''' (QWidget, bool)
        '''
        GxView.__init__(self, GxSceneBlocks(), parent, opengl)
        GxView
        
        self.libs = LibraryDefinitions()
        self.sketch = SketchBlocks(self.libs)

        self.scene().setSceneRect(0, 0, 2000, 4000)
        self.scene().setParent(self)
        self.wheel_zoom = False

        self.palette_blocks = GxPalette(self.libs, self.sketch,
                                        self.scene(), opengl)

    def scrollContentsBy(self, x, y):
        QGraphicsView.scrollContentsBy(self, x, y)
        
        self.palette_blocks.setPos(self.mapToScene(0, 0).x(),
                                   self.mapToScene(0, 0).y())
        if x != 0:
            self.scene().bringToFront(self.palette_blocks)

    def resizeEvent(self, event):
        ''' QGraphicsView.resizeEvent(QResizeEvent) -> NoneType
        '''
        QGraphicsView.resizeEvent(self, event)
        self.palette_blocks.updateHeight(self.height())
        
    def mousePressEvent(self, event):
        ''' GxView.mousePressEvent(event) -> NoneType
        '''
        super(GxViewPalette, self).mousePressEvent(event)
        
        if event.button() == Qt.MiddleButton:
            pprint(self.sketch._root)
            
        if event.button() == Qt.RightButton:
            item_at = self.itemAt(event.pos())

            if isinstance(item_at, GxBlock):
                top_parent = item_at.getTopParentItem()
                if top_parent.snippet_id:
                    print('#'*30)
                    print('Top parent:', top_parent)
                    print('Snippet %d code string:' % top_parent.snippet_id)
                    print('-'*30)
                    print(top_parent.sketch.getSnippetCodeString(
                        top_parent.snippet_id))
                    print('#'*30)


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Plastique'))

    win = QMainWindow()
    win.setGeometry(100, 100, 900, 600)

    gx_palette_view = GxViewPalette(parent=win, opengl=True)

    win.setCentralWidget(gx_palette_view)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()