# coding=utf-8
# 2024/5/27 下午3:13
from typing import Union, Dict,Any
from util.enum import AllureFileClean,FileEnum
import allure, json


class AllureHandle:
    def attach_text(self, step: str, body: Union[str, Dict, None], name: str, attachment_type: str) -> None:
        """附加文本类型的附件"""
        try:
            with allure.step(step):
                allure.attach(body, name, AllureFileClean[attachment_type.upper()].value)
        except KeyError:
            print(f"无效的附件类型: {attachment_type}")

    def attach_file(self, step: str, path: str, name: str, attachment_type: str) -> None:
        """附加文件类型的附件"""
        try:
            with allure.step(step):
                allure.attach.file(path, name, AllureFileClean[attachment_type.upper()].value)
        except FileNotFoundError:
            print(f"文件路径错误: {path}")
        except KeyError:
            print(f"无效的附件类型: {attachment_type}")

    def allure_step_pass(self, content: str) -> None:
        """通过的步骤"""
        with allure.step(content):
            pass


    def details_to_allure(self, url: str, method: str, type: Union[str, None] = None, data: Union[Dict, None] = None,
                          headers: Union[Dict, None] = None, files: str = None, response: str = None,
                          **kwargs: Any) -> None:
        """
        将接口请求的详细信息附加到allure报告中
        """
        self.allure_step_pass(f"接口请求地址: {url}")
        self.allure_step_pass(f"接口请求方式: {method}")
        self.allure_step_pass(f"接口请求参数类型: {type}")

        attachments = [
            (
            "接口请求头", json.dumps(headers, ensure_ascii=False, indent=4), "附件信息", "TEXT") if headers else None,
            ("接口请求参数", json.dumps(data, ensure_ascii=False, indent=4), "附件信息","TEXT") if data else None,
            ("接口上传附件", files[FileEnum.FILEPATH.value], "附件信息", files[FileEnum.FILETYPE.value].split('/')[1]) if files else None,
            ("自定义参数", json.dumps(kwargs, ensure_ascii=False, indent=4), "附件信息",
             "TEXT") if kwargs else None,
            ("接口响应结果", response, "附件信息", "TEXT") if response else None
        ]

        for attachment in attachments:
            if attachment is None:
                continue
            if attachment[0] == "接口上传附件":
                self.attach_file(step=attachment[0], path=attachment[1], name=attachment[2], attachment_type=attachment[3])
            else:
                self.attach_text(step=attachment[0], body=attachment[1], name=attachment[2], attachment_type=attachment[3])