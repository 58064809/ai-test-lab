# coding=utf-8
# 2024/4/9 15:19
from util.enum import Domain
from util.log_handle import log
from requests import adapters
from util.config_handle import ConfigHandle
from typing import *

import requests


class RequestControl:
    _instance = None

    def __init__(self, domain: str):
        if domain.upper() in Domain.__members__:
            requests.adapters.DEFAULT_RETRIES = 100  # 增加重连次数
            self.session = requests.session()
            self.session.keep_alive = False  # 关闭多余连接
            env = ConfigHandle().get_domain(domain)
            protocol = env['protocol']
            host = env['host']
            port = env['port']
            self.verify = None if env['protocol'] == 'http://' else False
            self.base_url = protocol + host + ':' + port
        else:
            raise ValueError('请输入正确的域名')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
            timeout: int = 10,**kwargs) -> requests.Response:
        """发送GET请求"""
        try:
            res = self.session.get(self.base_url + url, params=params, headers=headers, verify=self.verify,
                                   timeout=timeout,**kwargs)
            res.raise_for_status()  # 检查响应状态码
            return res
        except requests.RequestException as e:
            log.error(f"GET请求错误: {e}")
            raise

    def post_json(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, files: Optional[Dict[str, Any]] = None, timeout: int = 10,**kwargs) -> requests.Response:
        """发送JSON类型的POST请求"""
        try:
            res = self.session.post(self.base_url + url, json=data, headers=headers, files=files, verify=self.verify, timeout=timeout,**kwargs)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            log.error(f"JSON类型POST请求错误: {e}")
            raise

    def post_form(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, files: Optional[Dict[str, Any]] = None, timeout: int = 10,**kwargs) -> requests.Response:
        """发送表单类型的POST请求"""
        try:
            res = self.session.post(self.base_url + url, data=data, headers=headers, files=files, verify=self.verify, timeout=timeout,**kwargs)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            log.error(f"表单类型POST请求错误: {e}")
            raise

    def request_method(self, url: str,method: str,type:str = 'json', data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None, files: Optional[Dict[str, Any]] = None,
                       timeout: int = 10,**kwargs) -> requests.Response:
        """根据指定的HTTP方法发送请求"""
        try:
            if method.upper() == 'GET':
                result = self.get(url, params=data, headers=headers, timeout=timeout,**kwargs)
            elif method.upper() == 'POST' and type.lower() in ['json','form']:
                result = self.post_json(url, data=data, headers=headers, files=files, timeout=timeout,**kwargs) if type.lower() == 'json' else self.post_form(url, data=data, headers=headers, files=files, timeout=timeout,**kwargs)
            else:
                log.warning(f'请求method错误: {method}')
                raise Exception(f"请求method错误: {method}")
            return result
        except requests.RequestException as e:
            log.error(f"HTTP请求错误: {e}")
            raise

    def request_log(self, url, method, type=None,data=None,headers=None, files=None,**kwargs):
        log.info("接口请求地址 ==>> {}".format(url))
        log.info("接口请求方式 ==>> {}".format(method))
        log.info("接口请求头 ==>> {}".format(headers))
        log.info("接口请求参数类型 ==>> {}".format(type))
        log.info("接口请求参数 ==>> {}".format(data))
        log.info("接口上传附件 files 参数 ==>> {}".format(files))
        log.info("自定义参数参数 ==>> {}".format(kwargs))


if __name__ == '__main__':
    request = RequestControl('OA')
