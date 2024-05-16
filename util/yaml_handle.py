# -*- coding: utf-8 -*-
# date = 2021/7/1
from util.log_handle import log
from typing import *


import yaml,pathlib


class YamlHandle:
    def __init__(self,filename:(pathlib.WindowsPath, pathlib.PosixPath)):
        if not filename.exists():
            raise FileNotFoundError(f'{filename}文件不存在')
        self.yaml_path = filename

    def read_yaml(self) -> List:
        try:
            with open(self.yaml_path, 'r', encoding="utf-8") as f:
                self.content = list(yaml.safe_load_all(f))
            return self.content
        except yaml.YAMLError as e:
            log.warning(f"配置文件 {self.yaml_path} 格式错误: {str(e)}")
            raise
    def write_yaml(self,data):
        with open(self.yaml_path, 'w') as f:
            yaml.safe_dump_all(data, f, allow_unicode=True, default_flow_style=False,default_style="'",explicit_start=True,explicit_end=True)

    def add_to_yaml(self,data):
        with open(self.yaml_path, 'a') as f:
            yaml.safe_dump_all(data, f, allow_unicode=True, default_flow_style=False,default_style="'",explicit_start=True,explicit_end=True)


if __name__ == "__main__":
    yaml_handle = YamlHandle('config\config.yaml')

    print(yaml_handle.read_yaml)

