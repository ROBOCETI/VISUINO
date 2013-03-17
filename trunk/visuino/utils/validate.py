#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Although Python emphasizes the no-validation pratice due its
#              dynamic nature, this module offers a function for quick
#              sanity check on arguments, which can help debugging.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------

__all__ = ['validate_arg']

def validate_arg(arg_name, value, type_, restricted=None, range_=None):
    if not isinstance(value, type_):
        if isinstance(type_, (tuple, list)):
            types_str = "<class '%s'>" % type_[0].__name__
            for i in range(1, len(type_)):
                types_str += " or <class '%s'>" % type_[i].__name__
        else:
            types_str = "<class '%s'>" % type_.__name__

        raise TypeError(("Argument '%s' must be of type %s. Was "+\
            " given %s.") % (arg_name, types_str, value.__class__))

    if isinstance(restricted, (tuple, list)):
        if value not in restricted:
            raise ValueError(("Argument '%s' requires one of the following" + \
                " values: %s. Was given '%s'.") % (arg_name,
                str(list(restricted)), str(value)))

    if isinstance(range_, str) and range_.count('|'):
        sp = range_.split('|')
        try:
            min_ = type_(sp[0]) if sp[0].strip() != '' else None
            max_ = type_(sp[1]) if sp[1].strip() != '' else None
        except:
            raise ValueError("Invalid range format!")

        if (min_ is not None and value < min_) or \
           (max_ is not None and value > max_):
            raise ValueError(("Argument '%s' requires a value on the " + \
                "range %s, %s. Was given %s.") % (arg_name,
                '[' + str(min_) if min_ is not None else '(...',
                str(max_) + ']' if max_ is not None else '...)', str(value)))

        return type_(value)

    return value

if __name__ == '__main__':

    validate_arg('name', -1.5, float, range_='0.0|')
    print('Passed on the validation!')
