# coding=utf-8
# 2024/5/17 上午9:46
from typing import *
from util.log_handle import log
from util.model import CaseModel
from config.settings import Settings
import jmespath, re, json
from requests import Response


class DependentCase:
    """ 处理依赖相关的业务 """

    def __init__(self):
        # 这里假设初始化时可以提供一个函数名称的白名单。
        self.safe_functions = ['sum']

    def replace_data(self, case: CaseModel) -> Union[CaseModel, None]:
        """
        替换依赖数据
        :param data:
        :return:
        """
        depend_data = case.json(exclude_none=True, ensure_ascii=False)

        # log.info(f"源数据 ==>>:{depend_data}")

        def replacement(match):
            key = match.group(1)
            try:
                value = Settings.global_params[key]
            except KeyError:
                raise KeyError(f"依赖参数 {key} 不存在")
            log.info(f"替换 {match.group()} 为 {value}")
            return str(value)

        res = re.sub(r'\${(?!_)(.*?)}', replacement, depend_data)

        try:
            new_data = json.loads(res)
            if isinstance(new_data, dict):
                return CaseModel(**new_data)
            else:
                log.error("替换后数据不符合CaseModel结构")
                return None
        except json.JSONDecodeError as e:
            log.error(f"JSON解析错误: {e}")
            return None

    def _safe_call(self, func, *args):
        """
        安全调用函数的辅助方法，确保参数按预期传递。
        """
        try:
            return func(*args)
        except KeyError as e:
            raise KeyError(f"内置方法 {func.__name__} 调用失败: {e}")
    def replace_dependencies(self, case: CaseModel) -> Union[CaseModel, None]:
        """
        替换依赖数据
        :param case: CaseModel实例，包含需要处理的数据。
        :return: 替换后的CaseModel实例或None（在解析错误时返回None）。
        """
        depend_data = case.json(exclude_none=True, ensure_ascii=False)

        def replacement(match):
            matched_group = match.group(1)
            func_name, params = matched_group.split("(")[0], matched_group.split("(")[1][:-1]
            if func_name not in self.safe_functions:
                raise ValueError(f"方法 {func_name} 不在安全列表中")
            try:
                params = [p.strip() for p in params.split(",")] if params else []
                result = self._safe_call(getattr(self, func_name), *params)
                log.info(f"替换 {match.group()} 为 {result}")
                return str(result)
            except AttributeError as e:
                raise AttributeError(f"处理匹配项 {matched_group} 时出错: {e}")


        res = re.sub(r'\${__(.*?)}', replacement, depend_data)

        try:
            new_data = json.loads(res)
            if isinstance(new_data, dict):
                return CaseModel(**new_data)
            else:
                log.error("替换后数据不符合CaseModel结构")
                return None
        except json.JSONDecodeError as e:
            log.error(f"JSON解析错误: {e}")
            return None

    def get_extract(self, case: CaseModel, response: Response):
        if case.extract is not None and isinstance(case.extract, dict):
            for key, value in case.extract.items():
                try:
                    if response.headers.get('Content-Type') == 'application/json':
                        result = jmespath.search(value, response.json())
                        if result:
                            Settings.global_params[key] = result
                        else:
                            log.error(f"表达式: {value}，未匹配到结果，当前结果为: {result}")
                    else:
                        result = re.findall(value, response.text)
                        if result:
                            Settings.global_params[key] = result[0]
                        else:
                            log.error(f"表达式: {value}，未匹配到结果，当前结果为: {result}")
                except Exception as e:
                    log.error(f"提取失败: {e}")

    def sum(self,*args: str):
        if not args:
            raise ValueError("参数不能为空")
        return sum(map(int,args))
