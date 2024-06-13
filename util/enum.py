# coding=utf-8
# 2024/4/9 17:00
from enum import Enum,IntEnum,unique
import allure


@unique
class ENV(IntEnum):
    TEST = 0
    DEV = 1
    PRO = 2


@unique
class Domain(str,Enum):
    OA = 'oa'
    YSB = 'ysb'
    PARTNER = 'partner'

@unique
class HttpMethod(str,Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"

@unique
class FileEnum(IntEnum):
    FILEPATH = 0
    FILENAME = 1
    FILETYPE = 2


@unique
class AssertTypeEnum(str,Enum):
    JSON = 'json'
    RE = 're'


@unique
class AssertEnum(IntEnum):
    RESULT = 0
    COMPARISON = 1
    EXPECTED = 2
@unique
class ComparisonOperatorEnum(str,Enum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    GREATER_THAN = '>'
    LESS_THAN = '<'
    GREATER_EQUAL = '>='
    LESS_EQUAL = "<="
    IN = 'in'
    NOT_IN = 'not in'

class AllureFileClean(Enum):
    TEXT = allure.attachment_type.TEXT
    CSV = allure.attachment_type.CSV
    TSV = allure.attachment_type.TSV
    URI_LIST = allure.attachment_type.URI_LIST
    HTML = allure.attachment_type.HTML
    XML = allure.attachment_type.XML
    JSON = allure.attachment_type.JSON
    YAML = allure.attachment_type.YAML
    PCAP = allure.attachment_type.PCAP
    PNG = allure.attachment_type.PNG
    JPG = allure.attachment_type.JPG
    SVG = allure.attachment_type.SVG
    GIF = allure.attachment_type.GIF
    BMP = allure.attachment_type.BMP
    TIFF = allure.attachment_type.TIFF
    MP4 = allure.attachment_type.MP4
    OGG = allure.attachment_type.OGG
    WEBM = allure.attachment_type.WEBM
    PDF = allure.attachment_type.PDF






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
