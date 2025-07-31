# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 09:02:40 2021

@author: lgauthier
"""
import numpy as np
import numbers

def cast_to_float(val: str | numbers.Real) -> float:
    """
    Transform the input to a float. While it can be used on numeric values, it's
    really only interesting to use on strings.

    Parameters
    ----------
    val : numbers.Number
        DESCRIPTION.

    Returns
    -------
    float
        DESCRIPTION.

    """
    try:
        return float(val)
    except:
        return np.nan

def is_numeric_transformable(val: str | numbers.Number) -> bool:
    """
    Check if the input can be coerced as a numeric value. While numbers can be
    checked this way, it's really only interesting to test strings.

    Parameters
    ----------
    val : str | numbers.Number
        The value to test.

    Returns
    -------
    bool
        Whether the value can be coerce as a numeric value.

    """
    try:
        float(val)
        return True
    except:
        return False