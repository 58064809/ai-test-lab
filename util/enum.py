# coding=utf-8
# 2024/4/9 17:00
from enum import Enum,IntEnum,unique


@unique
class ENV(IntEnum):
    TEST = 0
    DEV = 1
    PRO = 2


@unique
class Domain(str,Enum):
    OA = 'oa'
    YSB = 'ysb'

@unique
class HttpMethod(str,Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


if __name__ == '__main__':
    # if "test".upper() in ENV._member_names_:
    #     print('cacac')
    # else:
    #     print('cacac212')
    # for _,b in TempletEnum.__members__.items():
    #     print(b.key,b.bool)
    # print(dict(TempletEnum.__members__.items()))
    # print(TempletEnum._value2member_map_)

    for item in ENV.__members__.items():
        print(item[1].value)
