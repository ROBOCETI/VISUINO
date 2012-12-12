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

class GxArgument(QGraphicsWidget):
    DEFAULT_FONT = QFont('Verdana', 10)
    BACKGROUND_COLOR = QColor(207, 226, 243)

    def __init__(self, **kwargs):
        """
        @ name: string.
        @ type: string.
        @ value: Defines the field QWidget(). It can be:
            * list of strings, for discrete values. Ex: ["HIGH", "LOW"]
                -> Field widget: QComboBox()
            * tuple of exact three elements, for numerical interval values.
              Ex: (min, max, incr)
                -> Field widget: QSpinBox() or QDoubleSpinBox()
            * None, for a generic input.
                -> Field widget: QLineEdit()
        @ fonts: {'label': QFont(), 'field': QFont()}
        @ orientation: string in ["H", "V"]
        @ scene: QGraphicsScene().
        @ parent: QGraphicsItem().
        """
        super(GxArgument, self).__init__(kwargs.get('parent', None))
        self.scene = kwargs.get('scene', None)
        self.name = kwargs.get('name', '')
        self.type_ = kwargs.get('type_', '')
        self.value = kwargs.get('value', None)
        self.fonts = kwargs.get('fonts', {'label': self.DEFAULT_FONT,
                                          'field': self.DEFAULT_FONT})
        orientation = kwargs.get('orientation', 'V')
        self.setPos(kwargs.get('pos', QPointF(0, 0)))

        self.label = QLabel(self.name)
        self.fonts['label'].setStyleStrategy(QFont.PreferAntialias)
        self.label.setFont(self.fonts['label'])
        self.label.setStyleSheet("QLabel{background-color: transparent;"+\
            "color : black;}") #TODO: more personalization
        self.label.setAlignment(Qt.AlignHCenter)

        self.field_widget = self._getFieldWidget(self.value)

        p_field_widget = QGraphicsProxyWidget()
        p_field_widget.setWidget(self.field_widget)

        p_label = QGraphicsProxyWidget()
        p_label.setWidget(self.label)

        self.layout = QGraphicsLinearLayout()

        if orientation.upper() == "H":
            self.layout.setOrientation(Qt.Horizontal)
            self.layout.addItem(p_label)
            self.layout.addItem(p_field_widget)
        else:
            self.layout.setOrientation(Qt.Vertical)
            self.layout.addItem(p_field_widget)
            self.layout.addItem(p_label)

        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)

        self.setLayout(self.layout)

        if self.scene: self.scene.addItem(self)

##        self.setFlags(QGraphicsItem.ItemIsSelectable |
##                      QGraphicsItem.ItemIsMovable)

    def _getFieldWidget(self, value):
        """
        Returns an appropiate QWidget() for the field, based on self.value
        attribute.
        """
        line_edit = QLineEdit()
        line_edit.setFont(self.fonts['field'])
        line_edit.setFixedWidth(100)

        if type(value) is list:

            combo = QComboBox()
            combo.addItems([unicode(i) for i in value])
            combo.setCurrentIndex(-1)
            combo.setFont(self.fonts['field'])

            return combo

        elif type(value) is tuple and len(value) == 3:

            if type(value[0]) is int:   #TODO: more consistency

                spin_box = QSpinBox()
                spin_box.setMinimum(value[0])
                spin_box.setMaximum(value[1])
                spin_box.setSingleStep(abs(value[2]))
                spin_box.setFont(self.fonts['field'])

                return spin_box

            elif type(value[0]) is float:

                d_spin_box = QDoubleSpinBox()
                d_spin_box.setMinimum(value[0])
                d_spin_box.setMaximum(value[1])
                d_spin_box.setSingleStep(abs(value[2]))
                d_spin_box.setFont(self.fonts['field'])

                return d_spin_box

            else: return line_edit

        else:

            return line_edit

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.transparent))
        painter.setBrush(QBrush(self.BACKGROUND_COLOR))
        painter.drawRoundedRect(self.layout.geometry(), 5, 5)


class GxFunctionBlock(QGraphicsWidget):
    DEFAULT_FONT = QFont('Verdana', 10)
    BACKGROUND_COLOR = Qt.blue

    def __init__(self, **kwargs):
        """
        @ name: string.
        @ args: list/tuple of GxArgument().
        @ return_: {'name': string, 'type': string}
        @ fonts: {'name': QFont(), 'args_label': QFont(),
            'args_field': QFont(), 'return': QFont()}
        @ orientation: string in ("H", "V"). <None>
        @ parent: QGraphicsItem(). <None>
        @ scene: QGraphicsScene(). <None>
        """
        super(GxFunctionBlock, self).__init__(kwargs.get('parent', None))

        self.name = kwargs.get('name', '')
        self.args = kwargs.get('args', None)
        self.return_ = kwargs.get('return_', {'name': '', 'type': ''})
        self.fonts = kwargs.get('fonts', {'name': self.DEFAULT_FONT,
                                          'args_label': self.DEFAULT_FONT,
                                          'args_field': self.DEFAULT_FONT,
                                          'return': self.DEFAULT_FONT})
        orientation = kwargs.get('orientation', "H")
        scene = kwargs.get('scene', None)
        if scene: scene.addItem(self)

        for a in self.args: a.setParent(self)

        self.setPos(kwargs.get('pos', QPointF(0, 0)))
        self.setCursor(Qt.ArrowCursor)

        self.label_name = QLabel(self.name)
        self.fonts['name'].setStyleStrategy(QFont.PreferAntialias)
        self.label_name.setFont(self.fonts['name'])
        self.label_name.setStyleSheet("QLabel{background-color: transparent;"+\
            "color : white;}") #TODO: more personalization

        if orientation.upper() == "V":
            self.label_name.setAlignment(Qt.AlignHCenter)
        else: self.label_name.setAlignment(Qt.AlignVCenter)

        p_label_name = QGraphicsProxyWidget()
        p_label_name.setWidget(self.label_name)

        self.layout = QGraphicsLinearLayout()
        self.layout.addItem(p_label_name)
        for x in self.args:
            self.layout.addItem(x)

        if orientation.upper() == "V":
            self.layout.setOrientation(Qt.Vertical)
        else: self.layout.setOrientation(Qt.Horizontal)

        self.setLayout(self.layout)

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)

        self.fonts['name'].setBold(True)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(0, 0, 120))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.BACKGROUND_COLOR))

        painter.drawRoundedRect(self.layout.geometry(), 25, 25)


    def mousePressEvent(self, event):
        super(GxFunctionBlock, self).mousePressEvent(event)
        self.scene().bringToFront(self)


    def mouseMoveEvent(self, event):
        super(GxFunctionBlock, self).mouseMoveEvent(event)

        if self.collidesWithTrunk():
            print "Mah oe"

    def collidesWithBlock(self):
        colli = []
        for x in self.scene().collidingItems(self):
            if isinstance(x, GxFunctionBlock):
                colli.append(x)
        return colli

    def collidesWithTrunk(self):
        for x in self.scene().collidingItems(self):
            if isinstance(x, GxTrunk):
                return x
        return None

##    def mouseReleaseEvent(self, event):
##        print self.zValue()


class GxTrunk(QGraphicsItem):

    def __init__(self, **kwargs):
        super(GxTrunk, self).__init__(kwargs.get('parent', None))
        self.scene = kwargs.get('scene', None)
        if self.scene: self.scene.addItem(self)
        self.setCursor(Qt.ArrowCursor)

##        self.setFlags(QGraphicsItem.ItemIsSelectable |
##                      QGraphicsItem.ItemIsMovable)

        self.setPos(100, 0)
        self._items = []

    def boundingRect(self):
        return QRectF(0, 0, 50, 100)


    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(20, 20, 20))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(80, 80, 80)))

        painter.drawRoundedRect(self.boundingRect(), 10, 10)


def main():
    app = QApplication([])

    my_scene = BaseScene()

    fb_pin_mode = GxFunctionBlock(
        name='pinMode',
        args=[GxArgument(name='pin', type_='int', value=(0, 13, 1)),
              GxArgument(name='mode', type_='int', value=["INPUT", "OUTPUT"])],
        pos=QPointF(200, 0),
        scene=my_scene)

    fb_delay = GxFunctionBlock(
        name='delay',
        args=[GxArgument(name='milliseconds', type_='int')],
        pos=QPointF(100, 200),
        orientation="H",
        scene=my_scene)

    fb_digital_write = GxFunctionBlock(
        name='digitalWrite',
        args=[GxArgument(name='pin', type_='int', value=range(14),
                         orientation="V"),
              GxArgument(name='value', type_='int', value=["HIGH", "LOW"],
                         orientation="V")],
        orientation="H",
        pos=QPointF(300, 100),
        scene=my_scene)

    start = GxTrunk(scene=my_scene)

    view = BaseView(scene=my_scene, wheel_zoom=True)
    view.show()

    app.exec_()


if __name__ == "__main__":
    main()
