# coding=utf-8
# 2024/4/9 17:00
from enum import Enum

class ENV(Enum):
    Active = 0
    TEST = 1
    DEV = 2
    PRO = 3

class Domain(Enum):
    OA = 0
    YSB= 1