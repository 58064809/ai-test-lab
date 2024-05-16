# coding=utf-8
# 2024/4/30 16:22
from config.settings import CONFIG_PATH, Settings, PYTEST_INI_PATH
from util.yaml_handle import YamlHandle
from configparser import ConfigParser
from util.enum import *
from typing import *


class ConfigHandle:
    _instance = None

    # 单例模式

    def __init__(self):
        self.yaml = YamlHandle(CONFIG_PATH)
        self.config = ConfigParser()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            YamlHandle(CONFIG_PATH).write_yaml(Settings().ENV_DATA)
        return cls._instance

    @property
    def get_env(self) -> str:
        self.config.read(PYTEST_INI_PATH)
        env = self.config.get('pytest', 'env').upper()
        return env

    @property
    def read_config(self) -> Dict:
        try:
            return self.yaml.read_yaml()[ENV[self.get_env].value]
        except KeyError:
            raise KeyError('环境名错误，可选环境名:TEST,DEV,PRO')



    @property
    def read_session(self) -> Any:
        return self.read_config['%s_environment' % self.get_env.lower()]['session']

    @property
    def read_db(self) -> Dict:
        return self.read_config['%s_environment' % self.get_env.lower()]['DBConnection']


    def get_domain(self, domain: str) -> Dict:
        domain_dict = {"oa": 0, "ysb": 1}
        return self.read_session[domain_dict[Domain[domain.upper()].value]]


if __name__ == '__main__':
    config = ConfigHandle()
    print(config.read_config)
    # print(config.read_session)
    # print(config.read_db)
