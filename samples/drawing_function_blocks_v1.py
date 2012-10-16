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

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *


class View(QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.zoom_level = 0

    def wheelEvent(self, event):
        factor = 1.41 ** (event.delta() / 240.0)
        self.scale(factor, factor)

        if factor < 1: self.zoom_level -= 1
        else: self.zoom_level += 1

        print(self.zoom_level)


class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super(Scene, self).__init__(parent)
        self.setSceneRect(0, 0, 640, 480)
        self.setBackgroundBrush(QBrush(QColor(200, 200, 200)))  ##TODO


class GxArgument(QGraphicsWidget):
    DEFAULT_FONT = QFont('Verdana', 11)
    BACKGROUND_COLOR = QColor(207, 226, 243)

    def __init__(self, **kwargs):
        """
        @ name: string
        @ type: string
        @ value: Defines the field QWidget(). It can be:
            * list of strings, for discrete values. Ex: ["HIGH", "LOW"]
                -> Field widget: QComboBox()
            * tuple of exact three elements, for numerical interval values.
              Ex: (min, max, incr)
                -> Field widget: QSpinBox() or QDoubleSpinBox()
            * None, for a generic input.
                -> Field widget: QLineEdit()
        @ fonts: {'label': QFont(), 'field': QFont()}
        @ scene: QGraphicsScene()
        @ parent: QGraphicsItem()
        """
        super(GxArgument, self).__init__(kwargs.get('parent', None))
        self.scene = kwargs.get('scene', None)
        self.name = kwargs.get('name', '')
        self.type_ = kwargs.get('type_', '')
        self.value = kwargs.get('value', None)
        self.fonts = kwargs.get('fonts', {'label': self.DEFAULT_FONT,
                                          'field': self.DEFAULT_FONT})

        self.setPos(kwargs.get('pos', QPointF(0, 0)))

        self.label = QLabel(self.name)
        self.fonts['label'].setStyleStrategy(QFont.PreferAntialias)
        self.label.setFont(self.fonts['label'])
        self.label.setStyleSheet("QLabel{background-color: transparent;"+\
            "color : black;}") #TODO: more personalization

        self.field_widget = self._getFieldWidget(self.value)

        p_label = QGraphicsProxyWidget()
        p_label.setWidget(self.label)

        p_field_widget = QGraphicsProxyWidget()
        p_field_widget.setWidget(self.field_widget)

        self.layout = QGraphicsLinearLayout()
        self.layout.addItem(p_label)
        self.layout.addItem(p_field_widget)

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
        painter.fillRect(self.layout.geometry(),
            QBrush(self.BACKGROUND_COLOR))


class GxFunctionBlock(QGraphicsWidget):
    DEFAULT_FONT = QFont('Verdana', 11)
    BACKGROUND_COLOR = Qt.blue

    def __init__(self, **kwargs):
        """
        @ name: string.
        @ args: list/tuple of GxArgument().
        @ return_: {'name': string, 'type': string}
        @ fonts: {'name': QFont(), 'args_label': QFont(),
            'args_field': QFont(), 'return': QFont()}
        @ parent: QGraphicsItem().
        @ scene: QGraphicsScene().
        """
        super(GxFunctionBlock, self).__init__(kwargs.get('parent', None))

        self.name = kwargs.get('name', '')
        self.args = kwargs.get('args', None)
        self.return_ = kwargs.get('return_', {'name': '', 'type': ''})
        self.fonts = kwargs.get('fonts', {'name': self.DEFAULT_FONT,
                                          'args_label': self.DEFAULT_FONT,
                                          'args_field': self.DEFAULT_FONT,
                                          'return': self.DEFAULT_FONT})
        self.scene = kwargs.get('scene', None)

        self.setPos(kwargs.get('pos', QPointF(0, 0)))

        self.label_name = QLabel(self.name)
        self.fonts['name'].setStyleStrategy(QFont.PreferAntialias)
        self.label_name.setFont(self.fonts['name'])
        self.label_name.setStyleSheet("QLabel{background-color: transparent;"+\
            "color : white;}") #TODO: more personalization
        self.label_name.setAlignment(Qt.AlignHCenter)

        p_label_name = QGraphicsProxyWidget()
        p_label_name.setWidget(self.label_name)

        self.layout = QGraphicsLinearLayout()
        self.layout.addItem(p_label_name)
        for x in self.args:
            self.layout.addItem(x)
        self.layout.setOrientation(Qt.Vertical)

        self.setLayout(self.layout)

        if self.scene: self.scene.addItem(self)

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)


    def paint(self, painter, option, widget=None):
        painter.fillRect(self.layout.geometry(),
            QBrush(self.BACKGROUND_COLOR))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    scene = Scene()

    fb_pin_mode = GxFunctionBlock(
        name='pinMode',
        args=[GxArgument(name='pin', type_='int', value=(0, 13, 1)),
              GxArgument(name='mode', type_='int', value=["INPUT", "OUTPUT"])],
        scene=scene)

    fb_delay = GxFunctionBlock(
        name='delay',
        args=[GxArgument(name='milliseconds', type_='int')],
        pos=QPointF(100, 200),
        scene=scene)

    fb_digital_write = GxFunctionBlock(
        name='digitalWrite',
        args=[GxArgument(name='pin', type_='int', value=[i for i in range(14)]),
              GxArgument(name='value', type_='int', value=["HIGH", "LOW"])],
        pos=QPointF(400, 100),
        scene=scene)

    view = View(scene)
    view.show()

    sys.exit(app.exec_())

