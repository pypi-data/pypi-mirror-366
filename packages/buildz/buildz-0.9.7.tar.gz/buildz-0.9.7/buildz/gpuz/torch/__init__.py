#coding=utf-8

__version__="0.0.1"

__author__ = "Zzz, emails: 1174534295@qq.com, 1309458652@qq.com"
# 小号多

from .middle_cache import MiddleCache

# 下面的dict_middle也弃了，上面的MiddleCache写的更合理
from .dict_middle import DictCache, Fcs
#from .dict_middle import *
Dict = DictCache
