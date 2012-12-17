#-------------------------------------------------------------------------------
# Name:        glued_items.py (PyQt4 sample)
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Purpose:     Allows QGraphicsItem objects to be able to vertically glue
#              onto each in the scene by mouse drag and drop events.
#              The moving item can be glued after or before some target
#              glueable item - which then will become its parent.
#
# Description: Introduces these two new classes:
#                - AbstractGlueableScene: extends BaseScene.
#                     Basically, holds the insertion marker, and also its
#                     manipulations. Then the most significant: has the
#                     glueItems() method.
#                - AbstractGlueableItem: extends QGraphicsItem.
#                     Redefines mouse events press, move and release to
#                     admit the "glue" effect.
#
#               Those are abstract classes, meaning that you should not
#               instantiate them directly. Use inheritance along with
#               QGraphicsScene and QGraphicsItem (or its derivatives),
#               respectively.
#
# Dependencies: bases.py - for BaseScene and BaseView.
#               BEWARE: BaseScene is required!! Altough it will work with
#               any QGraphicsView.
#
# Tests:       (OK) Win7 + Python 2.7.3 + PyQt 4.9 (x86)
#              (  ) Linux KDE + Python 2.7.3 + PyQt 4.9 (x86)
#              (  ) Linux Gnome + Python 2.7.3 + PyQt 4.9 (x86)
#              (  ) Mac OS + Python 2.7.3 + PyQt 4.9 (x86)
#
# ##TODO: Tests for Python 3.x and x64.
#
# Licence:     GNU FDL / Creative Commons SA
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *

class GxGlueableScene(BaseScene):
    """
    Uses bringToFront() from BaseScene.
    """

    GLUED_ITEMS_PADD = 5

    def __init__(self, **kwargs):
        """
        kwargs:
        - insertion_marker: QGraphicsItem() <self.DefaultInsertionMaker()>
        - collision_effect: QGraphicsEffect() <QGraphicsOpacityEffect()>.
        - parent: QWidget() <None>.
        """
        BaseScene.__init__(self, kwargs.get('parent', None))
        # the insertion marker is an item on the scene
        self.insert_marker = kwargs.get('insertion_maker',
            self.DefaultInsertionMarker())
        self.insert_marker.setVisible(False)
        self.addItem(self.insert_marker)

        # displacements to correct the insert marker position
        self.insert_marker_dx = -15
        self.insert_marker_dy = self.insert_marker.boundingRect().height() / 2

        #self.setClickToFront(True)

    def _clickToFront(self, event):
        """
        This class DO NOT use the standard "click to front" operation, so
        don't botter calling setClickToFront(True).
        """
        pass

    def collidesWithGlueable(self, item):
        """
        Return the top-most colliding GxGlueableItem(), if there is one,
        or else None.

        item: GxGlueableItem().
        """
        collided = [x for x in self.collidingItems(item) \
            if isinstance(x, AbstractGlueableItem)]
        if collided:
            return collided[-1]
        return None

    def showInsertionMarker(self, target, place):
        """
        Shows the marker in the right place of insertion.

        item: GxGlueableItem().
        place: string in ("after", "before").
        """
        # set the marker position to the target's position on the scene
        if target.parentItem():
            self.insert_marker.setPos(target.parentItem().mapToScene(
                target.pos()))
        else:
            self.insert_marker.setPos(target.pos())

        # correct the right place of the marker according to "place"
        if place == "after":
            self.insert_marker.moveBy(self.insert_marker_dx,
                target.boundingRect().height() - self.insert_marker_dy)
        else:
            self.insert_marker.moveBy(self.insert_marker_dx,
                - self.insert_marker_dy)

        self.insert_marker.setVisible(True)

    def hideInsertionMarker(self):
        self.insert_marker.setVisible(False)

    def setDefaultInsertionMarkerColor(self, color):
        """
        color: QColor().
        """
        if isinstance(self.insert_marker, self.DefaultInsertionMarker):
            self.insert_marker.COLOR = color

    def glueItems(self, source, target, place):
        """
        Glue the source (moving item) to the target (top-most colliding
        "glueable" item), in the right place (after or before).

        - source: AbstractGlueableItem().
        - target: AbstractGlueableItem().
        - place: string in ("after", "before")
        """

        if place == "before":

            bottom_child = source.getBottomChildGlueable()

            source.setPos(target.pos())
            source.moveBy(0, - source.getTotalHeight() \
                - self.GLUED_ITEMS_PADD)
            target.setParentItem(bottom_child)
            target.setPos(0, bottom_child.boundingRect().height() \
                + self.GLUED_ITEMS_PADD)
            self.bringToFront(source)

        elif place == "after":

            target_child = target.getChildGlueable()
            if target_child:
                self.glueItems(target_child,
                    source.getBottomChildGlueable(), "after")

            source.setParentItem(target)
            source.setPos(0, target.boundingRect().height()
                + self.GLUED_ITEMS_PADD)
            self.bringToFront(target)

    class DefaultInsertionMarker(QGraphicsItem):
        """
        Simple rectangle to act like a maker on the insertion effect.
        """
        COLOR = QColor(70, 70, 70)

        def boundingRect(self):
            return QRectF(0, 0, 400, 15)

        def paint(self, painter, option, widget=None):
            painter.fillRect(self.boundingRect(), self.COLOR)


class AbstractGlueableItem:
    """
    This graphics item has the ability to be "glued" on others of the same
    kind, meaning that
    """
    DY_GLUEABLE = 25    # spacing distance needed to unglue
    DX_GLUEABLE = 50

    def __init__(self, gb_scene=None, insertion_effect=None):

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)

        if isinstance(gb_scene, GxGlueableScene):
            gb_scene.addItem(self)

        # set up the insertion effect, which starts disabled and is only
        # enabled when a valid collision occours
        if isinstance(insertion_effect, QGraphicsEffect):
            self.insertion_effect = insertion_effect
        else:
            self.insertion_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.insertion_effect)
        self.insertion_effect.setEnabled(False)

        # data about the possible new glueable target item
        # target: AbstractGlueableItem
        # place: string in ("after", "before")
        self._glue_onto = {"target": None, "place": None}

        # data about the parent item in which its used to be glued on
        # item: AbstractGlueableItem
        # pos: QPointF
        # apart: boolean. Indicates if the moving item is far enoght
        # z: float. From self.zValue().
        self._old_glued = {"item": None, "pos": None,
            "apart": True, "z": None}

    def _updateOldGlued(self):

        if self._old_glued["item"]:

            # vertical displacement of the old parent
            dy = abs(self.pos().y() - self._old_glued["pos"].y())
            dx = abs(self.pos().x() - self._old_glued["pos"].x())

            if dy < self.DY_GLUEABLE and dx < self.DX_GLUEABLE:
                self.scene().showInsertionMarker(self._old_glued["item"],
                    "after")
                self._old_glued["apart"] = False
            else:
                # pulled away too much apart, lost the parent
                self.scene().hideInsertionMarker()
                self._old_glued["item"] = None
                self._old_glued["pos"] = None
                self._old_glued["apart"] = True

    def _updateChildRect(self):
        """
        Schedules a drawing update for the rect that includes itself and
        its child. This fixes the bug on QGraphicsEffect propagation to
        the childs.
        """
        child = self.getChildGlueable()
        if child:
            self.update(QRectF(self.pos(), QSizeF(
                self.boundingRect().width(),
                self.boundingRect().height() + \
                    child.boundingRect().height() + \
                    self.scene().GLUED_ITEMS_PADD)))


    def bringToFront(self):
        self.scene().bringToFront(self)


    def getCollided(self):
        # searches for the top-most collided item
        colli_top = self.scene().collidesWithGlueable(self)
        colli_bottom = self.scene().collidesWithGlueable(
            self.getBottomChildGlueable())

        if not colli_top and colli_bottom:
            colli = colli_bottom
        else:
            colli = colli_top

        return colli


    def getChildGlueable(self):
        """
        Return: AbstractGlueableItem. The first glueable child.
        """
        childs = [x for x in self.childItems() \
            if isinstance(x, AbstractGlueableItem)]
        if childs:
            return childs[0]
        else:
            return None


    def getBottomChildGlueable(self):
        """
        Return: AbstractGlueableItem. The bottom-most glueable child.
        """
        child, bottom_child = True, self

        while child:
            child = bottom_child.getChildGlueable()
            if child:
                bottom_child = child

        return bottom_child

    def getTotalHeight(self):
        """
        Return: float. Height of all the chain of glued items, from itself
            to its bottom-most child.
        """
        height = self.boundingRect().height()
        child = self

        while child:
            child = child.getChildGlueable()
            if child:
                height += self.scene().GLUED_ITEMS_PADD + \
                    child.boundingRect().height()

        return height

    def enableInsertion(self):
        if self.graphicsEffect():
            self.graphicsEffect().setEnabled(True)


    def disableInsertion(self):
        self.scene().hideInsertionMarker()
        self._glue_onto = {"target": None, "place": None}

        if self.graphicsEffect():
            self.graphicsEffect().setEnabled(False)


    def mousePressEvent(self, event):
        """
        On the left button press:
            - brings the insertion marker and itself to the front of the scene;
            - if it has a parent item, save its informantion and disables it;
            The consequence is the item to be free in the scene.
        """
        QGraphicsItem.mousePressEvent(self, event)

        if event.button() == 1:

            self.setFlags(QGraphicsItem.ItemIsMovable)

            self.scene().bringToFront(self.scene().insert_marker)

            if self.parentItem():
                # the parent will be save and disabled
                self._old_glued["pos"] = \
                    self.parentItem().mapToScene(self.pos())
                self._old_glued["z"] = self.zValue()
                self._old_glued["item"] = self.parentItem()
                self.setParentItem(None)
                self.setPos(self._old_glued["pos"])
                self._old_glued["apart"] = False

            self.bringToFront()

        if event.button() == 4:

            parent = self.parentItem()
            child = self.getChildGlueable()

            if parent or child:

                if child and parent:
                    child.setParentItem(None)
                    self.scene().glueItems(child, parent, "after")
                elif child:
                    child_pos = self.mapToScene(child.pos())
                    child.setParentItem(None)
                    child.setPos(child_pos)

                if parent:
                    my_pos = parent.mapToScene(self.pos())
                else:
                    my_pos = self.pos()

                self.setParentItem(None)
                self.setPos(my_pos)
                self.moveBy(100, -self.boundingRect().height()/2)

                self.bringToFront()
                self.setSelected(True)


    def mouseMoveEvent(self, event):
        """
        Checks for collision with others glueable items. If positive, then
        activates the insertion effect and set self._glue_onto attribute
        properly.

        RE-IMPLEMENTED from QGraphicsItem.
        """
        QGraphicsItem.mouseMoveEvent(self, event)

        self._updateOldGlued()

        # has collided with some glueable item?
        colli = self.getCollided()
        if colli:

            self.enableInsertion()

            colli_height = float(colli.boundingRect().height())

            # is the mouse cursor in the lower half of colli?
            if event.scenePos().y() > colli.pos().y() + colli_height/2:

                self.scene().showInsertionMarker(colli, "after")
                self._glue_onto = {"target": colli, "place": "after"}

            else:

                self.scene().showInsertionMarker(colli, "before")
                self._glue_onto = {"target": colli, "place": "before"}

        elif self._old_glued["apart"]:

            self.disableInsertion()

        self._updateChildRect()


    def mouseReleaseEvent(self, event):
        """
        If there is any glueable item to be glued, here is where it happens.
        """
        QGraphicsItem.mouseReleaseEvent(self, event)

        if event.button() in (1, 4):

            self.setFlags(QGraphicsItem.ItemIsSelectable |
                          QGraphicsItem.ItemIsMovable)

            # it has an new item to be glued onto?
            if self._glue_onto["target"]:

                self.scene().glueItems(self, self._glue_onto["target"],
                                             self._glue_onto["place"])

            # has no new target to glue, but has old parent?
            elif self._old_glued["item"]:

                if not self._old_glued["apart"]:
                    self.scene().glueItems(self,
                        self._old_glued["item"], "after")
                    self.setZValue(self._old_glued["z"])

            self.disableInsertion()
            self._old_glued = {"item": None, "pos": None,
                "apart": True, "z": None}


class GxGlueableItem(QGraphicsItem, AbstractGlueableItem):

    WIDTH = 300
    HEIGHT = 100

    def __init__(self, gb_scene=None, **kwargs):
        """
        - gb_scene: GluableScene().
        kwargs:
          - name: string.
          - color: QColor() <QColor('blue')>.
          - pos: list/tuple of 2 integers <(100, 100)>.
          - effect: QGraphicsEffect() <QGraphicsOpacityEffect()>.
          - parent: QGraphicsItem() <None>.
        """
        QGraphicsItem.__init__(self, kwargs.get('parent', None))
        AbstractGlueableItem.__init__(self, gb_scene)

        self.name = kwargs.get('name', '')

        # setting up color and position (not necessary for functionality)
        self.color = kwargs.get('color', QColor('blue'))
        pos = kwargs.get('pos', (100, 100))
        if pos and isinstance(pos, (tuple, list)) and len(pos) == 2:
            self.setPos(pos[0], pos[1])

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
            painter.drawRect(QRect(0, 0, self.WIDTH, self.HEIGHT))


def main():
    app = QApplication([])

    scene = GxGlueableScene()

    gb_item_1 = GxGlueableItem(scene, color=QColor('blue'), pos=(50, 50))
    gb_item_2 = GxGlueableItem(scene, color=QColor('blue'), pos=(200, 200))
    gb_item_3 = GxGlueableItem(scene, color=QColor('green'), pos=(350, 350))
    gb_item_4 = GxGlueableItem(scene, color=QColor('green'), pos=(450, 470))
    gb_item_5 = GxGlueableItem(scene, color=QColor('red'), pos=(300, 500))

    view = BaseView(scene)
    view.setWindowTitle('Sample: glued_items.py')
    view.show()

    app.exec_()


if __name__ == "__main__":
    main()

