# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 15:10:14 2013

@author: Nelso
"""

__all__ = ['getv_kw']

def getv_kw(kwargs, key, default, expected_types):
    """
    Get an valid keyword argument by doing type checking.
    Raises type error if any problems.
    
    :kwargs: dict from kewyord arguments.
    :key: any valid dict key.
    :default: value to assume if key is not found.
    :expected_types: single or tuple of types or classes (for use 
        in isinstance() built-in).
    """
    value = kwargs.get(key, default)
    exp = expected_types
    if not isinstance(value, exp):
        
        types_str = ''
        if isinstance(exp, tuple):
            if len(exp) > 1:
                for x in exp:
                    xs = "%s" % x
                    if xs[1] == 't':
                        xs = xs[xs.find("'") + 1 : -2]
                    elif xs[1] == 'c':
                        xs = xs[xs.find(".") + 1 : -2]
                    types_str += "'%s' or " % xs
                types_str = types_str[:-4]
            else:
                types_str = "%s" % exp[0]
        else:
            types_str = "%s" % exp
            
        vc = "%s" % value.__class__
                    
        message = ("Expected type %s for the '%s' keyword argument." + \
            " Was given type '%s'.") % (types_str, str(key), 
            vc[vc.find("'") + 1 : -2])
            
        raise TypeError(message)

