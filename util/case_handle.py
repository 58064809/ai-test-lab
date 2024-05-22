# coding=utf-8
# 2024/4/12 17:13
from util.yaml_handle import YamlHandle
from config.settings import SOURCE_DATA_PATH
from util.log_handle import log
from requests import Response
from util.request_control import RequestControl
from config.settings import Settings
from util.model import CaseModel
from util.depend_handle import DependentCase
from util.assert_handle import AssertHandle
from typing import *


class CaseHandle:
    _instance = None

    def __init__(self, filename: str):
        self.case = YamlHandle(SOURCE_DATA_PATH.joinpath(filename)).read_yaml()
        self.case_common = self.get_case_common()['case_common']
        self.case_global = self.get_case_common()['global']
        self.dependentcase = DependentCase()
        self.asserthandle = AssertHandle()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def get_case_common(self) -> Dict:
        """获取公共参数"""
        return self.case.pop(0)

    def get_case_global(self) -> Dict:
        """获取全局参数"""
        return self.case.pop(0)

    def set_global_params(self):
        """设置全局参数"""
        Settings.global_params.update(self.case_global)

    @property
    def get_allureEpic(self) -> str:
        """获取Epic"""
        return self.case_common['allureEpic']

    @property
    def get_allureFeature(self) -> str:
        """获取Feature"""
        return self.case_common['allureFeature']

    @property
    def get_allureStory(self) -> str:
        """获取Story"""
        return self.case_common['allureStory']

    @property
    def get_cases(self) -> List[Any]:
        """获取用例"""
        return [item for item in self.case if item['skip'] is None or item['skip'] in ['y', 'Y', 'true', 'True']]

    def prepare_headers(self, data: CaseModel) -> Optional[Dict[str, Any]]:
        """准备并更新请求头"""
        domain = data.request.domain.upper()
        try:
            token = Settings.global_params[domain]
        except KeyError:
            raise ValueError(f"域名{domain}在Settings.global_dict中未找到")
        return {**token, **data.request.headers} if data.request.headers else token



    def case_run(self, data: Dict, **kwargs) -> Response:
        """获取用例请求数据"""
        case_mode = CaseModel(**data)
        log.success('=========开始执行=========')
        log.info(f'Request:{case_mode.title}')
        headers = self.prepare_headers(case_mode)
        self.set_global_params()
        case_mode = self.dependentcase.replace_data(case_mode)
        case_mode = self.dependentcase.replace_dependencies(case_mode)
        RequestControl(case_mode.request.domain).request_log(case_mode.request.url, case_mode.request.method,
                                                             case_mode.request.request_type, case_mode.request.data,
                                                             headers,
                                                             case_mode.request.files, **kwargs)
        # try:
        resp = RequestControl(case_mode.request.domain).request_method(
            case_mode.request.url,
            case_mode.request.method,
            type=case_mode.request.request_type,
            data=case_mode.request.data,
            headers=headers,
            files=case_mode.request.files,
            **kwargs
        )
        log.info(f"Response:{case_mode.title}")
        log.info(f"响应==>>{resp.json()}")
        self.dependentcase.get_extract(case_mode, resp)
        self.asserthandle.assert_handle(case_mode,resp)
        log.success("接口响应时长: {} ms".format(round(resp.elapsed.total_seconds() * 1000, 2)))


        return resp
        # except Exception as e:
        #     log.error(f"请求过程中发生错误: {e}")
        # finally:
        #     log.success('=========结束执行=========\n')


if __name__ == '__main__':
    case = CaseHandle('moss_v3.yaml')
    print(case.case_common)
    print(case.get_cases)
