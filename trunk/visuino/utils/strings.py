#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Some strings utilities.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['str_dedent']

import textwrap

def str_dedent(long_string, span_operator='&'):
    ''' (str, str) -> str
    
    Appends one functionality for the textwrap.dedent() function: allows
    to span long lines by using the defined 'span_operator'. This way, 
    you can keep you code properly indented and also have nice good looking
    multiline strings. Use backslash to scape the 'span_operator'.
    
    Returns de dedented/spanned resulting string.
    '''
    x = textwrap.dedent(long_string)
    start = 0
    
    while True:
        pos = x.find(span_operator, start)
        
        if pos == 0 or (pos > 0 and x[pos-1] != '\\'):            
            x = x[:pos] + x[pos+len(span_operator):].lstrip()
            start = pos + 2            
        elif pos < 0:
            break
        else:
            start = pos + 2
            continue

    return x.replace('\%s' % span_operator, span_operator)