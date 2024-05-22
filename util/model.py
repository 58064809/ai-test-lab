# coding=utf-8
# 2024/4/12 14:40
from typing import *
from pydantic import *
from util.enum import *


class EnvModel(BaseModel):
    env:ENV = Field(default=0, description='环境')

class RequestModel(BaseModel):
    domain: Domain = Field(default=..., description='域名')
    method: HttpMethod = Field(default=...,regex='^(GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE)$',description='请求方式')
    url: str = Field(default=..., description='请求地址')
    request_type: str = Field(default=..., description='请求类型')
    data: Optional[Dict] = Field(default=None, description='请求参数')
    headers: Optional[Dict] = Field(default=dict(), description='请求头')
    files: Optional[Dict] = Field(default=None, description='文件')


class CaseModel(BaseModel):
    title: str = Field(default=..., description='用例名称')
    description: Optional[str] = Field(default=None, description='用例描述')
    skip: Optional[bool] = Field(default=None, description='跳过')
    request: RequestModel
    extract: Optional[Dict] = Field(default=None, description='提取')
    valid: Union[List[Dict[str,List]],None] = Field(default=list(), description='断言')





