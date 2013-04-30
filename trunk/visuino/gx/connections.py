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
#              tribute ONLY as 100% free. Also, remember to keep the credits.
#-------------------------------------------------------------------------------
from __future__ import division, print_function

from PyQt4.QtGui import *
from PyQt4.QtCore import *

__all__ = ['GxPluggableBlock']

from visuino.gx.bases import GxBlock
from visuino.gx.shapes import *
from visuino.gx.utils import *

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
            W, H = vfw, vfh
            pos = start_point

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
        GxBlock.__init__(self, scene, parent)

        self.mouse_active = mouse_active

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
        if self.io_male_colli_path:
            colli = self.io_male_colliding
            if not colli:
                # checks for collision with FEMALE IO colli paths
                for x in self.scene().io_female_colli_paths:
                    if self.io_male_colli_path.collidesWithItem(x):
                        print('IO Collision detected!')
                        self._startInsertionEffect('io', 'M', x)
                        break
            elif not self.io_male_colli_path.collidesWithItem(colli):
                self._endInsertionEffect('io', 'M')

        if self.vf_male_colli_path:
            colli = self.vf_male_colliding
            if not colli:
                # checks for collision with FEMALE VF colli paths
                for x in self.scene().vf_female_colli_paths:
                    if self.vf_male_colli_path.collidesWithItem(x):
                        print('VF male->female collision detected!')
                        self._startInsertionEffect('vf', 'M', x)
                        break
            elif not self.vf_male_colli_path.collidesWithItem(colli):
                self._endInsertionEffect('vf', 'M')

        if self.vf_female_colli_path:
            colli = self.vf_female_colliding
            if not colli:
                # checks for collision with MALE VF colli paths
                for x in self.scene().vf_male_colli_paths:
                    if self.vf_female_colli_path.collidesWithItem(x):
                        print('VF female->male collision detected!')
                        self._startInsertionEffect('vf', 'F', x)
                        break
            elif not self.vf_female_colli_path.collidesWithItem(colli):
                self._endInsertionEffect('vf', 'F')

    def _startInsertionEffect(self, kind, source_gender, target):
        ''' ('io'/'vf', 'male'/'female', GxColliPath)
        '''
        gender = 'male' if source_gender == 'M' else 'female'
        if not getattr(self, kind + '_' + gender + '_insertion_marker'):
            print('Creating insertion maker...')
            setattr(self, kind + '_' + gender + '_colliding', target)
            setattr(self, kind + '_' + gender + '_insertion_marker',
                GxInsertionMarker(kind, target.getStartPoint(), self.scene()))

    def _endInsertionEffect(self, kind, source_gender):
        ''' ('io'/'vf', 'F'/'M')
        '''
        gender = 'male' if source_gender == 'M' else 'female'
        i_mark = getattr(self, kind + '_' + gender + '_insertion_marker')
        if i_mark:
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

    def plugIo(self):
        '''
        '''
        print('Plugging IO...')
        target = self.io_male_colliding.parentItem()

        self.setParentItem(target)
        x, y = target.io_female_start.x(), target.io_female_start.y()
        x -= self.scene().style.notch.io_notch_width + 1
        y += 2*self.scene().style.arg_label.border_width + 1
        y -= self.io_male_start.y()
        self.setPos(x, y)

        self.parent_io = target
        target.child_io = self

        if hasattr(target, 'updateMetrics'):
            target.updateMetrics()

    def unplugIo(self):
        if self.parent_io:
            print("I am no longer your son!")

            pos = self.parent_io.mapToScene(self.pos())
            self.setParentItem(None)
            self.setPos(pos)

            self.parent_io.child_io = None
            self.parent_io.updateMetrics()
            self.parent_io = None
            self.io_male_colliding = None

            self.scene().addItem(self)

    def updateConnections(self):
        ''' () -> NoneType

        Should be called on the updateMetrics() of the GxBlock subclass.
        First, removes the existing colli paths, then update each notch
        consider their current start point attribute. So, if you wanna
        remove a connection on some notch, set its start point to None,
        an than call this method.
        '''
        self._cleanColliPaths()
#        print('After clean:\n' + 30*'-')

        for x in self.NOTCHES:
#            print('Updating notch', x, ':', sep='')
            self._updateNotch(x)

    def mousePressEvent(self, event):
        ''' GxBlock.mousePressEvent(QGraphicsSceneMouseEvent) -> NoneType
        '''
        GxBlock.mousePressEvent(self, event)
        if not self.mouse_active: return

        print('IO Female Colli Paths: ',
              len(self.scene().io_female_colli_paths))
        print('VF Female Colli Paths: ',
              len(self.scene().vf_female_colli_paths))
        print('VF Male Colli Paths: ',
              len(self.scene().vf_male_colli_paths))

        self.unplugIo()
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
        if not self.mouse_active: return

        if self.io_male_colliding and not self.parent_io:
            self.plugIo()
            self._endInsertionEffect('io', 'M')

##        if self.vf_male_colliding and not self.parent_vf:
##            self.plugVf()
##            self._endInsertionEffect('vf', 'M')

    def removeFromScene(self):
        ''' GxBlock.removeFromScene() -> NoneType

        Before removing itself, take cares of the childs by calling
        removeFromScene() on them too. Eventually, one of those childs
        will gonna be GxColliPath objects, which MUST be assured to be
        deleted from the scene by calling its removeFromScene() method.
        '''
        for child in self.childItems():
            child.removeFromScene()
        self.scene().removeItem(self)

def main():
    pass

if __name__ == '__main__':
    main()
