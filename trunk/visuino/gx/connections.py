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

__all__ = ['PluggableBlock']

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
        ''' ('io'/'vf', 'M'/'F', QPointF, GxSceneBlocks,
             QGraphicsItem)
        '''
        self._kind, self._gender = kind, gender
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
##        self.setVisible(False)

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

    def getGenderE(self):
        return 'male' if self._gender == 'M' else 'female'

    def getKind(self):
        return self._kind.lower()


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
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.boundingRect())

        painter.setPen(self._pen)
        painter.setBrush(Qt.transparent)
        painter.drawPath(self.path())

##        painter.setPen(QPen(Qt.black))
##        painter.setBrush(Qt.transparent)
##        painter.drawRect(self.boundingRect())


class PluggableBlock(object):
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

    def __init__(self):
        ''' (GxScene)
        '''
        for x in self.NOTCHES:
            setattr(self, x + '_start', None)
            setattr(self, x + '_colli_path', None)

        self.io_male_insertion_marker = None
        self.io_male_colliding = None
        self.vf_male_insertion_marker = None
        self.vf_male_colliding = None
        self.vf_female_insertion_marker = None
        self.vf_female_colliding = None

    def updateConnectors(self):
        self.cleanConnections()
        for x in self.NOTCHES:
            self._updateNotch(x)

    def _updateNotch(self, notch):
        ''' (str)
        '''
        kind, gender = notch[:2], notch[3].upper()
        notch_start = getattr(self, notch + '_start', None)
        colli_path = getattr(self, notch + '_colli_path', None)

        if notch_start is not None:

            new_colli_path = GxColliPath(kind, gender, notch_start,
                                         self.scene(), parent=self)
            setattr(self, notch + '_colli_path', new_colli_path)

            if kind == 'io' and gender == 'F':
                self.scene().io_female_colli_paths.add(new_colli_path)
            elif kind == 'vf':
                if gender == 'F':
                    self.scene().vf_female_colli_paths.add(new_colli_path)
                elif gender == 'M':
                    self.scene().vf_male_colli_paths.add(new_colli_path)

    def collideNotches(self):
        io_M, io_F = self.io_male_colli_path, self.io_female_colli_path
        vf_M, vf_F = self.vf_male_colli_path, self.vf_female_colli_path

        if io_M:
            colli = self.io_male_colliding
            if not colli:
                # checks for collision with FEMALE IO colli paths
                for x in self.scene().io_female_colli_paths:
                    if io_M.collidesWithItem(x):
                        print('IO Collision detected!')
                        self._startInsertionEffect('io', 'M', x)
                        break
            elif not io_M.collidesWithItem(colli):
                self._endInsertionEffect('io', 'M')

        if vf_M:
            colli = self.vf_male_colliding
            if not colli:
                # checks for collision with FEMALE VF colli paths
                for x in self.scene().vf_female_colli_paths:
                    if vf_M.collidesWithItem(x):
                        print('VF male->female collision detected!')
                        self._startInsertionEffect('vf', 'M', x)
                        break
            elif not vf_M.collidesWithItem(colli):
                self._endInsertionEffect('vf', 'M')

        if vf_F:
            colli = self.vf_female_colliding
            if not colli:
                # checks for collision with MALE VF colli paths
                for x in self.scene().vf_male_colli_paths:
                    if vf_F.collidesWithItem(x):
                        print('VF female->male collision detected!')
                        self._startInsertionEffect('vf', 'F', x)
                        break
            elif not vf_F.collidesWithItem(colli):
                self._endInsertionEffect('vf', 'F')

    def cleanConnections(self):
##        print('Cleaning PluggableBlock attributes...')
        io_Fcp = self.scene().io_female_colli_paths
        vf_Mcp = self.scene().vf_male_colli_paths
        vf_Fcp = self.scene().vf_female_colli_paths

        for notch in self.NOTCHES:
            kind, gender = notch[:2], notch[3].upper()
            colli = getattr(self, notch + '_colli_path')

##            print('Trying to remove ', notch + '_colli_path', colli)
            if isinstance(colli, GxColliPath):
                if kind == 'io' and gender == 'F' and colli in io_Fcp:
                    io_Fcp.remove(colli)
                elif kind == 'vf':
                    if gender == 'M' and colli in vf_Mcp:
                        vf_Mcp.remove(colli)
                    elif gender == 'F' and colli in vf_Fcp:
                        vf_Fcp.remove(colli)

                setattr(self, notch + '_colli_path', None)
##                print('Removed ', notch + '_colli_path')
                self.scene().removeItem(colli)

    def removeConnections(self):
        print('Removing connetions...')
        self.io_male_start = None
        self.io_female_start = None
        self.vf_male_start = None
        self.vf_female_start = None
        self.cleanConnections()

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


def main():
    pass

if __name__ == '__main__':
    main()
