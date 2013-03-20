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
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['FieldInfo']

from PyQt4.QtGui import *

class FieldInfo(object):
    """
    Attributes:
        :name: str. Used for text label in arguments.
        :type: str. Used for validation of inputs.
        :range: str. Imposes limits for values of input.
        :widget: str. Set the

    __init__
    """
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
