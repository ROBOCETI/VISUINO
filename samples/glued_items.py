#-------------------------------------------------------------------------------
# Name:        engine.py
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Created:     16/09/2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *

class GlueableScene(BaseScene):

    GLUED_ITEMS_PADD = 5

    def __init__(self, **kwargs):
        """
        insertion_marker: QGraphicsItem() <self.DefaultInsertionMaker()>
        collision_effect: QGraphicsEffect() <QGraphicsOpacityEffect()>.
        parent: QWidget() <None>.
        """
        super(GlueableScene, self).__init__(kwargs.get('parent', None))
        self.click_to_front = True

        # the insertion marker is an item on the scene
        self.insert_marker = kwargs.get('insertion_maker',
            self.DefaultInsertionMarker())
        self.insert_marker.setVisible(False)
        self.addItem(self.insert_marker)

        # displacements to correct the insert marker position
        self.insert_marker_dx = -13
        self.insert_marker_dy = self.insert_marker.boundingRect().height() / 2

    def addGlueableItem(self, item):
        """
        item: GxGlueableItem().
        """
        #item.setGraphicsEffect(self.collision_effect)
        self.addItem(item)

    def collidesWithGlueable(self, item):
        """
        Return the top-most colliding GxGlueableItem(), if there is one,
        or else None.

        item: GxGlueableItem().
        """
        for x in self.collidingItems(item):
            if isinstance(x, item.__class__):
                return x
        return None

    def enableInsert(self, item, place):
        """
        Shows the marker in the right place of insertion.

        item: GxGlueableItem().
        place: string in ("after", "before").
        """
        # setting up the maker position. It starts on the 'item' coordinates,
        # and then is moved accordinly to the insertion place (after/before)
        self.insert_marker.setPos(item.pos())
        if place == "after":
            self.insert_marker.moveBy(self.insert_marker_dx,
                item.boundingRect().height() - self.insert_marker_dy)
        else:
            self.insert_marker.moveBy(self.insert_marker_dx,
                - self.insert_marker_dy)

        # brings the marker on the top of the scene
        ##FIX: create a properly "bringToFront()" method
        self.insert_marker.setZValue(1000)
        self.insert_marker.setVisible(True)

    def disableInsert(self):
        """
        Basically hide the insertion marker.
        """
        self.insert_marker.setVisible(False)

    def glueItems(self, source, target, place):
        """
        Glue the source (moving item) to the target (top-most colliding
        "glueable" item), in the right place (after or before).

        - source: GxGlueableItem().
        - target: GxGlueableItem().
        - place: string in ("after", "before")
        """

        if place == "before":
            target.setParentItem(source)
            source.setPos(0, 0
                - target.boundingRect().height() - self.GLUED_ITEMS_PADD)
            source.addToGroup(target)
        else:
            source.setParentItem(target)
            source.setPos(0, 0
                + target.boundingRect().height() + self.GLUED_ITEMS_PADD)


    class DefaultInsertionMarker(QGraphicsItem):
        """
        Simple rectangle to act like a maker on the insertion effect.
        """
        COLOR = QColor(70, 70, 70)

        def __init__(self, parent=None):
            QGraphicsItem.__init__(self, parent)
            self.setPos(100, 100)

        def boundingRect(self):
            return QRectF(0, 0, 400, 15)

        def paint(self, painter, option, widget=None):
            painter.fillRect(self.boundingRect(), self.COLOR)


class AbstractGlueableItem(QGraphicsItem):
    """
    This graphics item has the ability to be "glued" on others of the same
    kind, meaning that
    """
    WIDTH = 300
    HEIGHT = 100

    # data from the target item which the moving one (self)
    # will be glued onto
    _glue_onto = {"item": None, "pos": None}

    insertion_effect = QGraphicsOpacityEffect()

    def __init__(self, gb_scene=None, insertion_effect=None):

        # properly add the item on the scene (has to be the special GBScene)
        if isinstance(gb_scene, GlueableScene):
            gb_scene.addGlueableItem(self)

        if isinstance(insertion_effect, QGraphicsEffect):
            self.insertion_effect = insertion_effect

        self.setGraphicsEffect(self.insertion_effect)
        self.insertion_effect.setEnabled(False)

    def enableInsertionEffect(self):
        if self.graphicsEffect():
            self.graphicsEffect().setEnabled(True)

    def disableInsertionEffect(self):
        if self.graphicsEffect():
            self.graphicsEffect().setEnabled(False)

    def mouseMoveEvent(self, event):
        """
        Checks for collision with others glueable items. If positive, then
        activates the insertion effect and set self._glue_onto attribute
        properly.

        RE-IMPLEMENTED from QGraphicsItem.
        """
        super(AbstractGlueableItem, self).mouseMoveEvent(event)

        if self.parentItem():
            return

        # searches for the top-most collided item
        colli = self.scene().collidesWithGlueable(self)

        # has collided with some glueable item?
        if colli:
            self.enableInsertionEffect()

            colli_height = float(colli.boundingRect().height())

            # is the mouse cursor in the lower half of colli?
            if event.scenePos().y() > colli.pos().y() + colli_height/2:

                self.scene().enableInsert(colli, "after")
                self._glue_onto = {"item": colli, "place": "after"}

            else:

                self.scene().enableInsert(colli, "before")
                self._glue_onto = {"item": colli, "place": "before"}

        else:
            self.scene().disableInsert()
            self.disableInsertionEffect()
            self._glue_onto = {"item": None, "pos": None}


    def mouseReleaseEvent(self, event):
        """
        If there is an valide gluable item configured in self._glue_onto,
        then perform the actual "gluing".
        """
        super(AbstractGlueableItem, self).mouseReleaseEvent(event)

        if isinstance(self._glue_onto["item"], self.__class__):
            self.scene().glueItems(self, self._glue_onto["item"],
                                         self._glue_onto["place"])
            self.scene().disableInsert()
            self.disableInsertionEffect()
            self._glue_onto = {"item": None, "pos": None}


    def mousePressEvent(self, event):
        super(AbstractGlueableItem, self).mousePressEvent(event)

##        print self.boundingRect()
##
##        if self.parentItem():
##            self.parent_delta_pos["dx"] = event.scenePos().x() \
##                - self.parentItem().x()
##            self.parent_delta_pos["dy"] = event.scenePos().y() \
##                - self.parentItem().y()
##
##            print self.parent_delta_pos


class GxGlueableItem(AbstractGlueableItem, QGraphicsItem):

    def __init__(self, gb_scene=None, **kwargs):
        """
        - gb_scene: GluableScene().
        kwargs:
          - color: QColor() <QColor('blue')>.
          - pos: list/tuple of 2 integers <(100, 100)>.
          - effect: QGraphicsEffect() <QGraphicsOpacityEffect()>.
          - parent: QGraphicsItem() <None>.
        """
        QGraphicsItem.__init__(self)
        AbstractGlueableItem.__init__(self, gb_scene)

        # setting up color and position (not necessary for functionality)
        self.color = kwargs.get('color', QColor('blue'))
        pos = kwargs.get('pos', (100, 100))
        if pos and isinstance(pos, (tuple, list)) and len(pos) == 2:
            self.setPos(pos[0], pos[1])

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)

    def boundingRect(self):
        """
        RE-IMPLEMENTED from QGraphicsItem.
        """
        return QRectF(0, 0, self.WIDTH, self.HEIGHT)


    def paint(self, painter, option, widget=None):
        """
        RE-IMPLEMENTED from QGraphicsItem.
        """
        painter.fillRect(self.boundingRect(), self.color)
        if self.isSelected():
            painter.setBrush(QBrush('transparent'))
            painter.setPen(QPen(QBrush(QColor('black')), 3.0, Qt.DotLine))
            painter.drawRect(self.boundingRect())


def main():
    app = QApplication([])

    scene = GlueableScene()

    gb_item_1 = GxGlueableItem(scene, color=QColor('blue'), pos=(50, 50))
    gb_item_2 = GxGlueableItem(scene, color=QColor('red'), pos=(200, 200))
    gb_item_3 = GxGlueableItem(scene, color=QColor('darkgreen'), pos=(350, 350))

    view = BaseView(scene)
    view.show()

    app.exec_()


if __name__ == "__main__":
    main()

