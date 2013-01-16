# -*- coding: utf-8 -*-
"""
@project: VISUINO (http://cta.if.ufrgs.br/projects/visuino)
@author: Nelso G. Jost (nelsojost@gmail.com)
"""
from __future__ import division
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *
from glued_items import *

class FieldInfo(object):
    VALID_TYPES = ['int', 'float', 'char', 'const']    
    
    def __init__(self, name, type_, range_, widget, description=''):
        """
        :name: str.
        :type_: str in ['int', 'float', 'char', 'const'].
        :range_: str. Range of the valid values, which depends on the type.            
        :widget: str in ['edit', 'combobox', 'spinbox'], followed (or not)
            by ',' (one or more) which delimitates parameters.
        :description: str.

        Valid strings for range_ param:
         * For any type:
          - 'x,y,...,z' where x, y, ... and z are the acceptable values.
            This is MANDATORY for type 'const', which must define a list
            of constants as just strings.
         * For numerical types (int/float):
          - 'min|max|step', which tells that allowed values are in the 
            interval from min to max (including both) by increments of step. 
            If max or min is empty, then it goes up to infinity on that 
            direction. Default step is 1.
            Examples (for type 'int'): 
                '5|21|2' allow values 5, 7, 9, ... up to 21 (including).
                '0|' says 'only positives and zero are allowed'.
                '|-5' says 'only negatives up to (and including) -5'.
          
        BEWARE: Some field constraints imposed by 'range_' are only valid
        depending on the chosen widget.
            * 'combobox': REQUIRES a declared range of format 'x,y,...,z'
                or a range of format 'min|max|step' with BOTH min and max
                values (i.e., do not accept infinite intervals).
            * 'spinbox': Do not accept negative values and negative step.
            * 'edit': step value has no use.
        
        Examples:
            FieldInfo('pin', 'int', '0|13', 'spinbox')
            FieldInfo('mode', 'const', 'INPUT,OUTPUT', 'combobox')
            FieldInfo('milliseconds', 'int', '>= 0', 'textedit')
        """
        self.name = str(name)
        if type_ not in self.VALID_TYPES:
            raise ValueError(
                '\'%s\' is an invalid \'type_\' parameter.' % str(type_))
        self.type = str(type_).lower()
        self.range = str(range_)
        self.widget = str(widget).lower()
        self.description = str(description)
    
    def _validateRange(self, r):
        """
        Validates some range string in the format: 'min|max|step', where
        'step' is optional (default: 1), returning a tuple with those
        values, in the following order: (min, max, step), with None values
        in 'min' or 'max' if ommited.
        If any invalid syntax, raise an proper error.
        
        :r: str. Range string format.
        """
        if not r.count('|'): return (None, None, 1)
        
        sp = r.split('|')
        min_, max_, step = sp[0].strip(), sp[1].strip(), ''
        
        if len(sp) > 2:
            step = sp[2].strip()
    
        if self.type == 'int':
            try:
                if min_:
                    min_ = int(min_)
                else:
                    min_ = None
            except:
                raise ValueError(
                    'Invalid integer \'%s\' for range minimum.' \
                    % sp[0].strip())                    
            try:
                if max_:
                    max_ = int(max_)
                else:
                    max_ = None
            except:
                raise ValueError(
                    'Invalid integer \'%s\' for range maximum.'\
                    % sp[1].strip())            
            try:
                if step:
                    step = int(step)
                else:
                    step = 1
            except:
                raise ValueError(
                    'Invalid integer \'%s\' for range step.'\
                    % sp[2].strip())  
                
            return (min_, max_, step)
            
    def _getComboBox(self, rg, params, parent):
        """
        Returns a QComboBox().
        """
        combobox = QComboBox(parent)
        if rg:
            if rg.count(','):
                combobox.addItems([x.strip() for x in rg.split(',')])
            elif rg.count('|'):
                
                min_, max_, step = self._validateRange(rg)
            
                if self.type == 'int':
                    
                    if isinstance(min_, int) and isinstance(max_, int):
                    
                        combobox.addItems([str(x) for x in range(min_,
                                           max_+1, step)])
                    else:
                        raise ValueError(
                            'The \'combobox\' widget requires an minimum'+\
                            ' AND maximum value for the range spec.' +\
                            ' Was given \'%s\'.' % rg)
            else:
                combobox.addItem(rg.strip())
        return combobox
        
    def _getSpinBox(self, rg, params, parent):
        """
        Returns a QSpinBox().
        """
        spinbox = QSpinBox(parent)
        
        if rg:
            if rg.count('|'):
                min_, max_, step = self._validateRange(rg)
                
                if isinstance(min_, int):
                    spinbox.setMinimum(min_)
                if isinstance(max_, int):
                    spinbox.setMaximum(max_)
                if isinstance(step, int):
                    spinbox.setSingleStep(step)
            else:
                raise ValueError(
                    'Invalid range format for \'spinbox\' widget.')  
                    
        if params and isinstance(params, (list, tuple)):
            try:
                width = int(params[0].strip())
            except:
                raise ValueError(
                    'Invalid widget \'spinbox\' width \'%s\'.' \
                    % params[0].strip())
            spinbox.setFixedWidth(width)                    
        
        return spinbox
        
    def _getLineEdit(self, rg, params, parent):
        """
        Returns a QLineEdit().
        """
        edit = QLineEdit(parent)            
        if rg:
            if rg.count('|'):
                
                min_, max_, step = self._validateRange(rg)
                
                if self.type == 'int':
    
                    int_val = QIntValidator()
                    if isinstance(min_, int):
                        int_val.setBottom(min_)
                    if isinstance(max_, int):
                        int_val.setTop(max_)
                        edit.setMaxLength(len(str(max_)))
                    edit.setValidator(int_val)
            else:
                raise ValueError(
                    'Invalid range format for \'edit\' widget.') 
        
        if params and isinstance(params, (list, tuple)):
            try:
                width = int(params[0].strip())
            except:
                raise ValueError(
                    'Invalid widget \'edit\' width \'%s\'.' \
                    % params[0].strip())
            edit.setFixedWidth(width)
        
        return edit        
    
    def getWidget(self, parent=None):
        """
        Returns the proper widget for what is configured in self.widget
        attribute. The default widget is QLineEdit().
        
        :parent: QWidget() <None>.
        """
        wid_sp = self.widget.split(',')
        widget = wid_sp[0]
        
        widget_params = []
        if len(wid_sp) > 1:
            widget_params = wid_sp[1:]
        
        if widget == 'combobox':
            return self._getComboBox(self.range, widget_params, parent)
        elif widget == 'spinbox':
            return self._getSpinBox(self.range, widget_params, parent)            
        else:
            return self._getLineEdit(self.range, widget_params, parent)


class GxFunctionBlock(QGraphicsItem):
    
    H_PADD = 10     # horizontal padding
    V_PADD = 10     # vertical padding
    ARG_PADD = 10   # argument input field padding
    
    # dimensions of the bounding rectangle
    _width = 200
    _height = 100

    def __init__(self, name, args, return_field, font_scheme, 
                 bk_color, pos, scene, parent=None):
        """
        :name: str. Function name.
        :args: list of FieldInfo(). Arguments fields, in the appearence 
               ordering. Can be an empty list.
        :return_field: FieldInfo(). Return field of the function.
        :font_scheme: dict. Defines the fonts to be used in the elements
                      of the block. Must be in the following format:
                      {'name': {'font': QFont(), 'color': QColor()},
                       'input_field': {'font': QFont(), 'color': QColor()}}
        :bk_color: QColor().
        :pos: tuple/list of 2 int.
        :scene: BaseScene() (for .bringToFront());
        :parent: QGraphicsItem() <None>.
        """
        QGraphicsItem.__init__(self, parent, scene)
        
        self._name = str(name)
        self._return = return_field
        self._font_scheme = font_scheme
        
        self._args_proxys = []          # proxys for every field in args
        self._setupArgsProxys(args)     # creates args input fields
        
        self.BK_COLOR = bk_color    # argument for QColor()
        
        self._font_scheme['name']['font'].setStyleStrategy(
            QFont.PreferAntialias)        
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setPos(pos[0], pos[1])
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsFocusable)
        
        self._updateMetrics()
        self._plantFields()
        
        
    def _setupArgsProxys(self, args):
        """
        Generates a list of GxProxyToFront for every FieldInfo() item in 
        'args' parameter. This list is stored in self._args_proxys.
        
        :args: list of FieldInfo().
        """
        for x in args:
            if isinstance(x, FieldInfo):
                new_proxy = self.GxProxyToFront(self)
                x_wid = x.getWidget()
                x_wid.setFont(self._font_scheme['input_field']['font'])
                new_proxy.setWidget(x_wid)
                self._args_proxys.append(new_proxy)
            

    def _updateMetrics(self):
        """
        Updates its dimensions (self._width and self._height) by computing 
        the size of each element on the block, including the function name, 
        arguments and return fields.
        """
        name_metrics = QFontMetrics(self._font_scheme['name']['font'])
        self._name_width = name_metrics.boundingRect(self._name).width()
        self._name_height = name_metrics.boundingRect(self._name).height()
        
        args_width, max_height = 0, self._name_height
        
        for x in self._args_proxys:
            x_rect = x.boundingRect()
            x_width, x_height = x_rect.width(), x_rect.height()
            args_width += x_width
            if x_height > max_height:
                max_height = x_height
        
        self._width = 2 * self.H_PADD + self._name_width + args_width \
            + (len(self._args_proxys) - 1) * self.ARG_PADD
            
        if self._args_proxys:   # add one more H_PADD if any args
            self._width += self.H_PADD
        
        self._height = 2 * self.V_PADD + max_height
        
        
    def _plantFields(self):
        """
        Figures out the correct position for each argument and return fields, 
        positioning their widgets on the right place.
        """
        # marks 
        args_width = self.H_PADD + self._name_width       
        for x in self._args_proxys:
            x.setPos(args_width + self.ARG_PADD, 
                     self._height/2 - x.boundingRect().height()/2)
            args_width += self.ARG_PADD + x.boundingRect().width()
                

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), self.BK_COLOR)
        painter.setFont(self._font_scheme['name']['font'])
        painter.setPen(QPen(self._font_scheme['name']['color']))
        painter.drawText(QRectF(self.H_PADD, 0, self._name_width, self._height), 
                         Qt.AlignCenter, self._name)

    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        self.scene().bringToFront(self)
        
    class GxProxyToFront(QGraphicsProxyWidget):
        """
        New feature added: when clicked, brings its parent on the top
        of the scene.
        """
        def mousePressEvent(self, event):
            QGraphicsProxyWidget.mousePressEvent(self, event)
            self.scene().bringToFront(self.parentItem())          
    
def main():
    app = QApplication([])
    
    scene = GxGlueableScene()
    
    font_block_scheme = {'name': {'font': QFont('Verdana', 16),
                                  'color': QColor('white')},
                         'input_field': {'font': QFont('Verdana', 12),
                                         'color': QColor('black')}}

    block_dg_write = GxFunctionBlock('digitalWrite', 
        [FieldInfo('pin', 'int', '0|13', 'combobox'),
         FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
        None, font_block_scheme, QColor('blue'), (0, 0), scene)
        
    block_delay = GxFunctionBlock('delay', 
        [FieldInfo('milliseconds', 'int', '0|999999', 'edit,130')],
        None, font_block_scheme, QColor('purple'), (200, 100), scene)
        
    block_dg_read = GxFunctionBlock('digitalRead', 
        [FieldInfo('pin', 'int', '0|13', 'spinbox,50')],
        None, font_block_scheme, QColor('green'), (100, 300), scene)        

    view = BaseView(scene)
    view.centerOn(0, 0)
    view.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()