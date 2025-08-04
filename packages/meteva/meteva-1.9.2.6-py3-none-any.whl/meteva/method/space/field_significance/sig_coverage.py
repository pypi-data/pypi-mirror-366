#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 18:29:57 2022

@author: tangbuxing
"""
import numpy as np


def CI_fun(CI_field, est_field, replacement=np.nan):
    test = est_field[0.5 * CI_field < abs(est_field)] = replacement
    return test


def inside(DF):
    # result = CI_fun(DF['Upper'] - DF['Lower'], DF['Estimate'])
    aa = DF['Upper'] - DF['Lower']
    bb = DF['Estimate']
    result = 0.5 * aa < abs(bb)
    return result


def sig_coverage(DF):
    out = {}
    tmp = inside(DF)
    out = sum(tmp[tmp == 1]) / len(tmp) - sum(DF['Estimate'] == None)
    return out



