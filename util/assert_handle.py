# coding=utf-8
# 2024/5/21 下午2:05
from typing import Dict, Any
from requests import Response
from util.enum import AssertEnum, ComparisonOperatorEnum, AssertTypeEnum
from util.log_handle import log
from util.model import CaseModel
import jmespath, re


class AssertHandle:

    def _is_valid_assertion(self, item: Dict[str, Any]) -> bool:
        """验证断言格式是否正确"""
        keys = [AssertTypeEnum.JSON.value, AssertTypeEnum.RE.value]
        for key in keys:
            if key in item and isinstance(item[key], list) and len(item[key]) == 3:
                return True
        return False

    def _compare_values(self, actual: Any, operator: str, expected: Any) -> None:
        """比较实际值与预期值"""
        comparison_func = {
            ComparisonOperatorEnum.EQUAL.value: lambda x, y: x == y,
            ComparisonOperatorEnum.NOT_EQUAL.value: lambda x, y: x != y,
            ComparisonOperatorEnum.GREATER_THAN.value: lambda x, y: x > y,
            ComparisonOperatorEnum.LESS_THAN.value: lambda x, y: x < y,
            ComparisonOperatorEnum.GREATER_EQUAL.value: lambda x, y: x >= y,
            ComparisonOperatorEnum.LESS_EQUAL.value: lambda x, y: x <= y,
            ComparisonOperatorEnum.IN.value: lambda x, y: x in y,
            ComparisonOperatorEnum.NOT_IN.value: lambda x, y: x not in y
            # ...其他比较逻辑
        }.get(operator)

        if comparison_func is None:
            raise ValueError("未知的比较操作符")

        if not comparison_func(actual, expected):
            raise AssertionError(f"比较失败: 实际值 {actual} {operator} 预期值 {expected}")

    def _get_json_result(self, path: str, response_json: Dict[str, Any]) -> Any:
        """使用 JMESPath 获取结果"""
        return jmespath.search(path, response_json)

    def _get_regex_result(self, pattern: str, text: str,index:int=0) -> str:
        """执行正则表达式匹配并返回第一个匹配项"""
        return re.compile(pattern).findall(text)[index]

    def assert_handle(self, case: CaseModel, response: Response,index:int=0):
        for item in case.valid:
            if not self._is_valid_assertion(item):
                raise ValueError("断言配置错误")

            assertion_type = next((k for k in [AssertTypeEnum.JSON.value, AssertTypeEnum.RE.value] if k in item), None)
            if assertion_type == AssertTypeEnum.JSON.value:
                result = self._get_json_result(item[assertion_type][AssertEnum.RESULT.value], response.json())
                self._compare_values(result, item[assertion_type][AssertEnum.COMPARISON.value], item[assertion_type][AssertEnum.EXPECTED.value])
            elif assertion_type == AssertTypeEnum.RE.value:
                result = self._get_regex_result(item[assertion_type][AssertEnum.RESULT.value], response.text,index=index)
                self._compare_values(result, item[assertion_type][AssertEnum.COMPARISON.value], item[assertion_type][AssertEnum.EXPECTED.value])
            else:
                raise ValueError("不支持的断言类型")

            log.info(f"断言成功: 实际值 【{result}】 {item[assertion_type][AssertEnum.COMPARISON.value]} 预期值 【{item[assertion_type][AssertEnum.EXPECTED.value]}】")
