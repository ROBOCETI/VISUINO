#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Nelso
#
# Created:     13/04/2013
# Copyright:   (c) Nelso 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from PyQt4.QtGui import *
from PyQt4.QtCore import *

__all__ = ['PluggableBlock']

class GxInsertionMarker(QGraphicsPathItem):
    '''
    Insertion marker meant to be shown when of the collision male/female
    IO notches.
    '''
    def __init__(self, color, notch_size, notch_shape, scene):
        ''' (QColor, QSize, str in NotchIOPath.VALID_SHAPES,
             QGraphicsScene) -> NoneType
        '''
        self._pen = QPen(QColor(color), 8, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin)

        pw = self._pen.width()
        iow, ioh = notch_size
        DY = ioh/2

        path = GxPainterPath(QPointF(iow + pw, pw))
        path.lineToInc(dy = DY)
        self.io_notch_start_y = path.currentPosition().y()
        path.connectPath(NotchPath(path.currentPosition(), QSizeF(iow, ioh),
                         notch_shape, '+j', facing='left'))
        path.lineToInc(dy = DY)

        QGraphicsPathItem.__init__(self, path, None, scene)

        self._width = iow + 2*pw
        self._height = 2*DY + 2*pw + ioh

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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


class GxColliPath(QGraphicsPathItem):
    '''
    Path used for detecting IO notch collisions.

    Can be of the kind male ('M') or female ('F)', according with the type
    of notch associated with it. The intersection of a moving male with a
    female is collision-detected an then the insertion marker can be activated.
    '''
    _OUTLINE_COLOR = Qt.black

    def __init__(self, kind, gender, start_point, style_notch,
                 scene=None, parent=None):
        ''' ('io'/'vf', 'M'/'F', QPointF, StyleNotch, QGraphicsScene,
             QGraphicsItem)
        '''
        self._kind, self._gender = kind, gender
        sp = start_point

        iow, ioh = style_notch.io_notch_width, style_notch.io_notch_height
        vfw, vfh = style_notch.vf_notch_width, style_notch.vf_notch_height

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

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.setPen(QPen(QColor(self._OUTLINE_COLOR)))
        painter.setBrush(Qt.transparent)
        painter.drawPath(self.path())


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

    def updateConnectors(self):
        self.clean()
        for x in self.NOTCHES:
            self._updateNotch(x)

    def _updateNotch(self, notch):
        ''' (str)
        '''
        notch_start = getattr(self, notch + '_start', None)
        kind, gender = notch[:2], notch[3].upper()

        if notch_start is not None:

            new_colli_path = GxColliPath(kind, gender, notch_start,
                                         self._style_notch, self.scene(),
                                         parent=self)

            setattr(self, notch + '_colli_path', new_colli_path)

            if kind == 'io' and gender == 'F':
                self.scene().io_colli_paths.add(new_colli_path)
            elif kind == 'vf':
                self.scene().vf_colli_paths.add(new_colli_path)


    def collideNotches(self):
        io_male, io_female = self.io_male_colli_path, self.io_female_colli_path
        vf_male, vf_female = self.vf_male_colli_path, self.vf_female_colli_path

        if io_male:
            for x in self.scene().io_colli_paths:
                if io_male.collidesWithItem(x):
                    self._startInsertionEffect('io', 'M')
                    break

        if vf_male:
            for x in self.scene().vf_colli_paths:
                if x is not vf_male and x.isFemale() and \
                   vf_male.collidesWithItem(x):
                    print('VF male->female collision detected!')

        if vf_female:
            for x in self.scene().vf_colli_paths:
                if x is not vf_female and x.isMale() and \
                   vf_female.collidesWithItem(x):
                    print('VF female->male collision detected!')

    def clean(self):
##        print('Cleaning PluggableBlock attributes...')
        for x in self.NOTCHES:
            colli = getattr(self, x + '_colli_path', 'baka')
##            print('Trying to remove ', x + '_colli_path', colli)
            if isinstance(colli, GxColliPath):
                try:
                    self.scene().io_colli_paths.remove(colli)
                    self.scene().vf_colli_paths.remove(colli)
                except:
                    pass
##                print('Removed ', x + '_colli_path')
                self.scene().removeItem(colli)

    def _startInsertionEffect(self, notch_type, notch_gender):
        print('IO Collision detected!')

    def _endInsertionEffect(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
