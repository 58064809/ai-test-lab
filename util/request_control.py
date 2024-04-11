# coding=utf-8
# 2024/4/9 15:19

from util.log_handle import log
from util.decorator import SingletonDecorator
from requests import adapters
from util.yaml_handle import YamlHandle
import requests


@SingletonDecorator
class RequestControl:
    def __init__(self,domain : int):
        requests.adapters.DEFAULT_RETRIES = 100  # 增加重连次数
        self.session = requests.session()
        self.session.keep_alive = False  # 关闭多余连接
        self.env = YamlHandle().get_session
        self.domain = domain
        self.protocol = self.env[self.domain]['protocol']

        self.host = self.env[self.domain]['host']
        self.port = str(self.env[self.domain]['port'])
        self.verify = None if self.env[self.domain]['protocol'] == 'http://' else False
        self.base_url = self.protocol + self.host + ':' + self.port

    def get(self, url, params=None, headers=None, timeout=10):
        res = self.session.get(self.base_url + url, params=params, headers=headers, verify=self.verify, timeout=timeout)
        return res

    def post(self, url, data=None, headers=None, files=None, timeout=10):
        res = self.session.post(self.base_url + url, data=data, headers=headers, files=files, verify=self.verify,
                            timeout=timeout)
        return res

    def post_json(self, url, json=None, headers=None, files=None, timeout=10):
        res = self.session.post(self.base_url + url, json=json, headers=headers, files=files, verify=self.verify,
                            timeout=timeout)
        return res

    def request_method(self, url, method, headers=None, param=None, files=None, timeout=10):
        if method.upper() == 'GET':
            result = self.get(url, headers=headers, params=param, timeout=timeout)
        elif method.upper() == 'POST':
            result = self.post(url, data=param, headers=headers, files=files, timeout=timeout)
        elif method.upper() == 'JPOST':
            result = self.post_json(url, json=param, headers=headers, files=files, timeout=timeout)
        else:
            log.warning('请求method错误')
            raise Exception("请求method错误")
        return result
