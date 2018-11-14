# -*- coding: utf-8 -*-s
from collections import OrderedDict
import re
adict = {
'MSSE2D':1,
'MSSE2G':2,
'MSS2F':3,
'MSSE2E':4,
'MSSE2F':5,
'MSS2C':6,
'TSS2A':7,
'TSC2B':8,
'SGSN2B':9,
'SGSN2C':10,
}

aselect =  (list(map(lambda i:(i,i),sorted(adict, key=adict.__getitem__))))
