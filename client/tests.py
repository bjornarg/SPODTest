"""Runs doctests on spodtest modules.

"""
import doctest

import testers.base

doctest.testmod(testers.base)
