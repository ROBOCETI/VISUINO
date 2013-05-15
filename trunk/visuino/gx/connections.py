#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Provides all the block connection mechanism through the class
#              GxPluggableBlock.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free. Also, remember to keep the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from visuino.gx.bases import GxBlock
from visuino.gx.shapes import *
from visuino.gx.utils import *

__all__ = ['GxPluggableBlock']

class GxColliPath(QGraphicsPathItem):
    '''
    Path used for detecting IO notch collisions.

    Can be of the kind male ('M') or female ('F)', according with the type
    of notch associated with it. The intersection of a moving male with a
    female is collision-detected an then the insertion marker can be activated.
    '''
    def __init__(self, kind, gender, start_point, scene, parent=None):
        ''' ('io'/'vf', 'M'/'F', QPointF, GxSceneBlocks, QGraphicsItem)
        '''
        self._kind, self._gender = kind.lower(), gender.upper()
        sp = self._start_point = start_point
        sn = scene.style.notch

        iow, ioh = sn.io_notch_width, sn.io_notch_height
        vfw, vfh = sn.vf_notch_width, sn.vf_notch_height

        if kind.lower() == 'io':
            W, H = iow, 2/3 * ioh
            pos = QPointF(sp.x() - iow, sp.y() + (ioh - H)/2)
        else:
            W, H = 2*vfw, 4*vfh
            pos = QPointF(start_point.x() - (W - vfw)/2,
                          start_point.y() - (H - vfh)/2)

        path = QPainterPath()
        path.addRect(0, 0, W, H)
        QGraphicsPathItem.__init__(self, path, parent, scene)
        self.setPos(pos)
        self.setVisible(False)

        # inserts itself on the correct set of colli paths (on the scene)
        colli_set = self.kind + '_' + self.gender_ext + '_colli_paths'
        if hasattr(self.scene(), colli_set):
            getattr(self.scene(), colli_set).add(self)
#            print('Created colli path on self.scene.', colli_set, sep='')

    def isMale(self):
        ''' () -> bool
        '''
        return self._gender == 'M'

    def isFemale(self):
        ''' () -> bool
        '''
        return self._gender == 'F'

    def getStartPoint(self):
        ''' () -> QPointF
        '''
        return self.parentItem().mapToScene(self._start_point)

    @property
    def kind(self):
        return self._kind.lower()

    @property
    def gender(self):
        return self._gender.upper()

    @property
    def gender_ext(self):
        return 'male' if self._gender == 'M' else 'female'

    def removeFromScene(self):
        ''' () -> NoneType

        Remove this colli path objectf from the scene, by also taking care
        of its reference on whatever set of colli path it is in.
        '''
        scene = self.scene()
        colli_set = self.kind + '_' + self.gender_ext + '_colli_paths'
        if hasattr(scene, colli_set) and self in getattr(scene, colli_set):
            getattr(scene, colli_set).remove(self)
#            print('Removed ', self, ' from ', colli_set, sep='')        
        scene.removeItem(self)


class GxInsertionMarker(QGraphicsPathItem):
    '''
    Insertion marker meant to be shown when of the collision male/female
    IO notches.
    '''
    def __init__(self, kind, start_point, scene):
        ''' ('io'/'vf', QPointF, GxSceneBlocks)
        '''
        sn = scene.style.notch
        x0, y0 = start_point.x(), start_point.y()
        self._pen = QPen(QColor(sn.insertion_marker_color),
                         sn.insertion_marker_width,
                         Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        pw = self._pen.width()

        if kind == 'io':
            iow, ioh = sn.getIoNotchSize()
            DY = ioh/2

            path = GxPainterPath(QPointF(iow + pw, pw))
            path.lineToInc(dy = DY)
            NotchPath.connect(path, QSizeF(iow, ioh), sn.io_notch_shape,
                              '+j', 'left')
            path.lineToInc(dy = DY)

            W, H = iow + 2*pw, 2*DY + ioh + 2*pw
            pos = QPointF(x0 - iow - pw, y0 - ((H - ioh)/2))
        else:
            vfw, vfh = sn.getVfNotchSize()
            DX = vfw/2

            path = GxPainterPath(QPointF(pw, vfh + pw))
            path.lineToInc(dx = DX)
            NotchPath.connect(path, QSizeF(vfw, vfh), sn.vf_notch_shape + '/0.85',
                              '+i', 'down')
            path.lineToInc(dx = DX)

            W, H = 2*DX + vfw + 2*pw, vfh + 2*pw
            pos = QPointF(x0 - ((W - vfw)/2), y0 - vfh - pw)

        self._width, self._height = W, H

        QGraphicsPathItem.__init__(self, path, None, scene)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        scene.bringToFront(self)
        self.setPos(pos)

    def boundingRect(self):
        ''' QGraphicsItem.boundingRect() -> QRectF
        '''
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(self._pen)
        painter.setBrush(Qt.transparent)
        painter.drawPath(self.path())

##        painter.setPen(QPen(Qt.black))
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self.boundingRect())


class GxPluggableBlock(GxBlock):
    '''
    Attributes:
        - io_male_start: QPointF <None>
        - io_male_colli_path: GxColliPath <None>
        - io_female_start: QPointF <None>
        - io_female_colli_path: GxColliPath <None>

        - vf_male_start: QPointF <None>
        - vf_male_colli_path: GxColliPath <None>
        - vf_female_start: QPointF <None>
        - vf_female_colli_path: GxColliPath <None>
    '''
    NOTCHES = ('io_male', 'io_female', 'vf_male', 'vf_female')

    def __init__(self, scene, parent=None, mouse_active=True):
        ''' (GxScene)
        '''
        GxBlock.__init__(self, scene, parent, mouse_active)
        
        for x in self.NOTCHES:
            setattr(self, x + '_start', None)
            setattr(self, x + '_colli_path', None)

        self.io_male_insertion_marker = None
        self.io_male_colliding = None
        self.vf_male_insertion_marker = None
        self.vf_male_colliding = None
        self.vf_female_insertion_marker = None
        self.vf_female_colliding = None

        self.parent_io = None
        self.parent_vf = None
        self.child_io = None
        self.child_vf = None
        
        self.bottom_child_vf = None

    def _updateNotch(self, notch):
        ''' (str in self.NOTCHES)
        '''
        kind, gender = notch[:2], notch[3].upper()
        notch_start = getattr(self, notch + '_start', None)

        if notch_start is not None:        

            new_colli_path = GxColliPath(kind, gender, notch_start,
                                         self.scene(), parent=self)
            setattr(self, notch + '_colli_path', new_colli_path)

    def _checkNotchCollisions(self):
        ''' () -> NoneType

        Checks for possible collisions on all the notches, except for the
        IO female. Therefore, connections by dragging IO female to some IO
        male have no effect.
        '''
        if self.io_male_colli_path and not self.parent_io:
            colli = self.io_male_colliding
            if not colli:
                # checks for collision with FEMALE IO colli paths
                for x in self.scene().io_female_colli_paths:
                    if self.io_male_colli_path.collidesWithItem(x):
#                        print('IO Collision detected!')
                        self._startInsertionEffect('io', 'M', x)
                        break
            elif not self.io_male_colli_path.collidesWithItem(colli):
                self._endInsertionEffect('io', 'M')
                
        if self.vf_female_colli_path and not self.parent_vf:
            colli = self.vf_female_colliding
            if not colli:
                # checks for collision with MALE VF colli paths
                for x in self.scene().vf_male_colli_paths:
                    if self.vf_female_colli_path.collidesWithItem(x):
#                        print('VF female->male collision detected!')
                        self._startInsertionEffect('vf', 'F', x)
                        break
            elif not self.vf_female_colli_path.collidesWithItem(colli):
                self._endInsertionEffect('vf', 'F')                

#        if self.vf_male_colli_path:
#            colli = self.vf_male_colliding
#            if not colli:
#                # checks for collision with FEMALE VF colli paths
#                for x in self.scene().vf_female_colli_paths:
#                    if self.vf_male_colli_path.collidesWithItem(x):
#                        print('VF male->female collision detected!')
#                        self._startInsertionEffect('vf', 'M', x)
#                        break
#            elif not self.vf_male_colli_path.collidesWithItem(colli):
#                self._endInsertionEffect('vf', 'M')
   

    def _startInsertionEffect(self, kind, source_gender, target):
        ''' ('io'/'vf', 'male'/'female', GxColliPath)
        '''
        gender = 'male' if source_gender == 'M' else 'female'
        if not getattr(self, kind + '_' + gender + '_insertion_marker'):
#            print('Creating insertion maker...')        
            setattr(self, kind + '_' + gender + '_colliding', target)      
            setattr(self, kind + '_' + gender + '_insertion_marker',
                GxInsertionMarker(kind, target.getStartPoint(), self.scene()))

    def _endInsertionEffect(self, kind, source_gender):
        ''' ('io'/'vf', 'F'/'M')
        '''
        gender = 'male' if source_gender == 'M' else 'female'
        i_mark = getattr(self, kind + '_' + gender + '_insertion_marker')
        if i_mark:
#            print('Removing ', kind, ' ', source_gender, ' insertion marker...' , sep='')
            self.scene().removeItem(i_mark)
            setattr(self, kind + '_' + gender + '_insertion_marker', None)
            setattr(self, kind + '_' + gender + '_colliding', None)

    def _cleanColliPaths(self):
        ''' () -> NoneType
        '''
        for notch in self.NOTCHES:
            kind, gender = notch[:2], notch[3].upper()
            colli = getattr(self, notch + '_colli_path')
            if isinstance(colli, GxColliPath):
                colli.removeFromScene()
                setattr(self, notch + '_colli_path', None)
                
    def _cleanInsertionMarkers(self):
        for notch in ('io_male', 'vf_male', 'vf_female'):
            im = getattr(self, notch + '_insertion_marker')
            if im is not None:
                self.scene().removeItem(im)
            setattr(self, notch + '_insertion_marker', None)

    def plugIo(self, target):
        '''
        '''
#        print('Plugging IO...')
        self.setParentItem(target)
        x, y = target.io_female_start.x(), target.io_female_start.y()
        x -= self.scene().style.notch.io_notch_width + self.getBorderWidth()/2
        y += 2*target.getBorderWidth()
        y -= self.io_male_start.y()
        self.setPos(x, y)

        self.parent_io = target
        target.child_io = self

        if hasattr(target, 'updateMetrics'):
            target.updateMetrics()

    def unplugIo(self):
        if self.parent_io:
#            print("I am no longer your son!")

            pos = self.parent_io.mapToScene(self.pos())
            self.setParentItem(None)
            self.setPos(pos)

            self.parent_io.child_io = None
            self.parent_io.updateMetrics()
            self.parent_io = None
            self.io_male_colliding = None

            self.scene().addItem(self)

    def plugVfFemale(self, target):
#        print('Plugging VF...')
        if target.child_vf is None:

            self.parent_vf = target
            target.child_vf = self
    
            self.setParentItem(target)
            self._updateChildVfPosition(target)
            
        else:
            my_bottom_child = self.getBottomChildVf()
            new_child = target.child_vf
            new_child.parent_vf = my_bottom_child
            my_bottom_child.child_vf = new_child
            
            target.child_vf = self
            self.parent_vf = target

            self.setParentItem(target)
            self._updateChildVfPosition(target)            
            new_child.setParentItem(my_bottom_child)
            self._updateChildVfPosition(my_bottom_child)

    def plugVfMale(self, target):
        self.child_vf = target
        target.parent_vf = self

        target_pos = target.pos()
        
        self.setPos(target_pos.x(), target_pos.y() - self.getHeight() + 
            self.scene().style.notch.vf_notch_height)
        
        target.setParentItem(self)
        target.setPos(self.mapFromScene(target_pos))

    def unplugVf(self):
        if self.parent_vf:

            pos = self.parent_vf.mapToScene(self.pos())
            self.setParentItem(None)
            self.setPos(pos)

            self.parent_vf.child_vf = None
            self.parent_vf = None

            self.scene().addItem(self)        
            
    def getBottomChildVf(self):
        if not self.child_vf:
            return self
        else:
            next_child = self.child_vf
            while True:            
                if next_child.child_vf is None:
                    return next_child
                else:
                    next_child = next_child.child_vf
                    
    def getFirstNonSelectedBottomChildVf(self):
        item = self
        while True:
            if item.isSelected():
                if item.child_vf:
                    item = item.child_vf
                    continue
                else:
                    break
            else:
                break
        return item
            
    def _updateChildVfPosition(self, parent):
        if parent and parent.child_vf:
#            print('Updating child VF position...')
            x, y = parent.vf_male_start.x(), parent.vf_male_start.y()
            x -= x #+ self.parent_vf.getBorderWidth()/2
            y -= parent.getBorderWidth()/2
            parent.child_vf.setPos(x, y)

    def updateConnections(self):
        ''' () -> NoneType

        Should be called on the updateMetrics() of the GxBlock subclass.
        First, removes the existing colli paths, then update each notch
        consider their current start point attribute. So, if you wanna
        remove a connection on some notch, set its start point to None,
        an than call this method.
        '''
        self._cleanColliPaths()
        for x in self.NOTCHES:
            self._updateNotch(x)

        self._updateChildVfPosition(self)

    def mousePressEvent(self, event):
        ''' GxBlock.mousePressEvent(QGraphicsSceneMouseEvent) -> NoneType
        '''           
        if self.mouse_active and not self.isSelected():
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)    
            self.scene().clearSelection()
    
        GxBlock.mousePressEvent(self, event)
        if not self.mouse_active: return

        if event.button() == Qt.LeftButton:

            self.unplugIo()
            
            if not self.isSelected():
                self.unplugVf()
            else:
                parent = self.parent_vf
                if parent and not parent.isSelected():
                    self.unplugVf()
                last_sel_child = self.getFirstNonSelectedBottomChildVf()
                if last_sel_child and not last_sel_child.isSelected():
                    last_sel_child.unplugVf()
                    if parent:
                        last_sel_child.plugVfFemale(parent)
                self._checkNotchCollisions() 
            
            if self.io_male_start:
                self._checkNotchCollisions()                      
            
    def mouseMoveEvent(self, event):
        ''' GxBlock.mouseMoveEvent(QGraphicsSceneMouseEvent) -> NoneType
        '''
        GxBlock.mouseMoveEvent(self, event)
        if not self.mouse_active: return

        self._checkNotchCollisions()

    def mouseReleaseEvent(self, event):
        ''' GxBlock.mouseReleaseEvent(QGraphicsSceneMouseEvent) -> NoneType
        '''                
        GxBlock.mouseReleaseEvent(self, event)
        if not self.mouse_active or not self.scene(): return
        
        if event.button() == Qt.LeftButton:
        
            self._checkNotchCollisions()
    
            if self.io_male_colliding and not self.parent_io:
                self.plugIo(self.io_male_colliding.parentItem())
                self._endInsertionEffect('io', 'M')
            
            if self.vf_female_colliding and not self.parent_vf:
                self.plugVfFemale(self.vf_female_colliding.parentItem())
                self._endInsertionEffect('vf', 'F')  
                
    #        if self.vf_male_colliding:
    #            self.plugVfMale(self.vf_male_colliding.parentItem())
    #            self._endInsertionEffect('vf', 'M')
    
            if not self.io_male_start:
                self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def removeFromScene(self):
        ''' GxBlock.removeFromScene() -> NoneType

        Before removing itself, take cares of its childs by calling
        removeFromScene() on them too. Eventually, one of those childs
        will gonna be GxColliPath objects, which MUST be assured to be
        deleted from the scene by calling its removeFromScene() method.
        '''
        self._cleanInsertionMarkers()
        for child in self.childItems():
            child.removeFromScene()
        if self.scene():
            self.scene().removeItem(self)