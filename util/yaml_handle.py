# # -*- coding: utf-8 -*-
# # date = 2021/7/1

from config.settings import CONFIG_PATH
from util.enum import ENV
from util.log_handle import log
import yaml

class YamlHandle:
    _instance = None  # 保存实例化对象

    def __init__(self):
        self.config_path = CONFIG_PATH.joinpath("config.yaml")

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    # 获取环境变量
    @property
    def env(self):
        env = self.get_activation()[ENV.Active.value]['activation']
        return env

    @property
    def get_config(self):
        self.config = self.get_activation()[getattr(ENV, self.env).value]
        env_name = list(self.config.keys())[0]
        return self.config[env_name]

    @property
    def get_db_connection(self) -> dict:
        return self.get_config['DBConnection']

    @property
    def get_session(self) -> dict:
        return self.get_config['session']

    def get_activation(self):
        with open(self.config_path, "r") as f:
            self.content = list(yaml.safe_load_all(f.read()))
        return self.content

    def update_activation(self,data):
        with open(self.config_path, 'w') as f:
            yaml.safe_dump_all(data, f,allow_unicode=True)




    def write_date_to_yaml(self,activation,test, dev,pro):
        with open(self.config_path, 'a') as f:
            yaml.safe_dump_all([activation,test, dev,pro], f, allow_unicode=True, default_flow_style=False)

if __name__ == "__main__":
    activation = {"activation":"test"}
    a = {
        "test_environment": {
            "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": 443,
                         "headers": {
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                             "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2Jhc2VfaWQiOiI0Mjc0NHwxNzExNTE5OTY1NTEwIn0.XXG9fJxOnoxytK733YRw-TE-bU8SNXz7kxy_zEpvEGw"
                         }
                         }, {"domain": "ysb", "protocol": "https://", "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": 443,
                             "headers": {
                                 "User-Agent": "Mozilla/5.0 (Linux; Android 11; PCHM10 Build/RKQ1.200903.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)",
                                 "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJBUFAiLCJpc3MiOiJsbC1hcHAtYnVzaW5lc3MiLCJ1c2VySWQiOiI0OTA1MzEiLCJpYXQiOjE3MTE2ODEwODV9.tOVbAwbVuIx500WgeinW3p8BEgjBPfZD_t5K4J1zq38"
                             }
                             }],
            "DBConnection": {"host": "10.14.2.245", "port": 3306, "user": "root", "password": "123456",
                             "database": "api_report", "charset": "utf8"}
        }}

    b = {
        "dev_environment": {
            "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": 443,
                         "headers": {
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                             "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2Jhc2VfaWQiOiI0Mjc0NHwxNzExNTE5OTY1NTEwIn0.XXG9fJxOnoxytK733YRw-TE-bU8SNXz7kxy_zEpvEGw"
                         }
                         }, {"domain": "ysb", "protocol": "https://", "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": 443,
                             "headers": {
                                 "User-Agent": "Mozilla/5.0 (Linux; Android 11; PCHM10 Build/RKQ1.200903.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)",
                                 "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJBUFAiLCJpc3MiOiJsbC1hcHAtYnVzaW5lc3MiLCJ1c2VySWQiOiI0OTA1MzEiLCJpYXQiOjE3MTE2ODEwODV9.tOVbAwbVuIx500WgeinW3p8BEgjBPfZD_t5K4J1zq38"
                             }
                             }],
            "DBConnection": {"host": "pc-2ze8c757mjh350kql-public.rwlb.rds.aliyuncs.com", "port": 3306, "user": "lldb_dev", "password": "LLdev#2022zby",
                             "database": "nearby_travel", "charset": "utf8"}
        }}

    c = {
        "pro_environment": {
            "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": 443,
                         "headers": {
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                             "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2Jhc2VfaWQiOiI0Mjc0NHwxNzExNTE5OTY1NTEwIn0.XXG9fJxOnoxytK733YRw-TE-bU8SNXz7kxy_zEpvEGw"
                         }
                         }, {"domain": "ysb", "protocol": "https://", "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": 443,
                             "headers": {
                                 "User-Agent": "Mozilla/5.0 (Linux; Android 11; PCHM10 Build/RKQ1.200903.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)",
                                 "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJBUFAiLCJpc3MiOiJsbC1hcHAtYnVzaW5lc3MiLCJ1c2VySWQiOiI0OTA1MzEiLCJpYXQiOjE3MTE2ODEwODV9.tOVbAwbVuIx500WgeinW3p8BEgjBPfZD_t5K4J1zq38"
                             }
                             }],
            "DBConnection": {"host": "pc-2ze8c757mjh350kql-public.rwlb.rds.aliyuncs.com", "port": 3306, "user": "lldb_dev", "password": "LLdev#2022zby",
                             "database": "nearby_travel", "charset": "utf8"}
        }}

    # YamlHandle().write_date_to_yaml(activation,a, b,c)
