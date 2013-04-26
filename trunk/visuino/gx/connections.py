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
    _OUTLINE_COLOR = Qt.transparent

    def __init__(self, kind, gender, start_point, scene=None, parent=None):
        ''' ('M'/'F', QSizeF, QPointF, QGraphicsScene,
             QGraphicsItem) -> NoneType
        '''
        self._kind = str(kind).upper()
        self._pen = QPen(QColor(self._OUTLINE_COLOR))

        iow, ioh = io_notch_size.width(), io_notch_size.height()

        if self.isFemale():
            W, H = 1.3*iow, ioh/2
        else:
            W, H = 6, 4*ioh/5

        path = QPainterPath()
        path.addRect(0, 0, W, H)

        QGraphicsPathItem.__init__(self, path, parent, scene)

        self.setPos(io_notch_start.x() - W/2,
                    io_notch_start.y() + ioh/2 - H/2)

    def isMale(self):
        ''' () -> bool
        '''
        return self._kind.upper() == 'M'

    def isFemale(self):
        ''' () -> bool
        '''
        return self._kind.upper() == 'F'

    def paint(self, painter, option=None, widget=None):
        ''' QGraphicsItem.paint(QPainter, QStyleOptionGrpahicsItem,
                                QWidget) -> NoneType
        '''
        painter.setPen(self._pen)
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

    def update(self):
        for x in self.NOTCHES:
            self._setupUpdateNotch(x)

    def _setupUpdateNotch(self, notch):
        ''' (str)
        '''
        notch_start = getattr(self, notch + '_start', None)

        if notch_start is not None:
            colli_path = getattr(self, notch + '_colli_path', None)
            if colli_path:
                colli_path.update() #TODO
            else:
                setattr(self, notch + '_colli_path',
                        GxColliPath(notch[:2], notch[3].upper(),
                                    notch_start, self.scene, parent=self))
                self.scene().io_colli_paths.add(getattr(self, notch +
                                                        '_colli_path'))

    def testCollide(self):
        if self.io_male_colli_path:
            for x in self.scene().io_colli_paths:
                if x.isFemale() and self.io_male_colli_path.collideWith(x):
                    self._startInsertionEffect('io', 'M')
                    break

    def _startInsertionEffect(self, notch_type, notch_gender):
        pass

    def _endInsertionEffect(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
