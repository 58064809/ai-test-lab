# coding=utf-8
# 2024/3/28 11:51


from pathlib import Path


# ROOT
BASE_PATH = Path(__file__).parent.parent.resolve()
# 配置
CONFIG_PATH = BASE_PATH.joinpath('config', 'config.yaml').resolve()
PYTEST_INI_PATH = BASE_PATH.joinpath('run_main', 'pytest.ini').resolve()
# driver
CHROME_EXECUTABLE_PATH = BASE_PATH.joinpath('driver_tools', 'chromedriver.exe').resolve()
# 数据源
SOURCE_DATA_PATH = BASE_PATH.joinpath('data')
# 压缩文件目录
ZIP_PATH = BASE_PATH.joinpath('zip')
# 报告
REPORT_PATH = BASE_PATH.joinpath('report').resolve()
REPORT_RESULT_PATH = REPORT_PATH.joinpath('report_result').resolve()
REPORT_HTML_PATH = REPORT_PATH.joinpath('report_html').resolve()
# 截图
CAPTURE_SCREEN_PATH = REPORT_PATH.joinpath('image').resolve()
# 日志路径
LOG_PATH = BASE_PATH.joinpath('log').resolve()
# 图像识别断言
EXISTS_PNG = BASE_PATH.joinpath('exists_png').resolve()
# 邮件配置
email = {
    "switch": False,
    "tester":"路昭凡",
    "user": "58064809@qq.com",  # 发件人邮箱
    "password": "zivwcrpvqmhvbjeh",  # 发件人邮箱授权码
    "host": "smtp.qq.com",
    "to": ["130069417@qq.com", "58064809@qq.com"],  # 收件人邮箱
    # "attachments":[ZIP_PATH.joinpath('report.zip').resolve()]
    "attachments":[]
}


class Settings:
    _instance = None
    global_params = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def ENV_DATA(self):
        test_environment = {
            "test_environment": {
                "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": "443",
                             'username': '13550087714',
                             'password': '1'
                             },
                            {"domain": "ysb", "protocol": "https://",
                             "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": "443", 'username': '13550087714',
                             'password': '123456'
                             }, {"domain": "partner", "protocol": "https://",
                                 "host": "partner.llzby.top",
                                 "port": "443", 'username': '13550088888',
                                 'password': '123456'
                                 }],
                "DBConnection": {"host": "10.14.2.245", "port": "3306", "user": "root", "password": "123456",
                                 "database": "api_report", "charset": "utf8"}
            }}

        dev_environment = {
            "dev_environment": {
                "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": "443",
                             'username': '13550087714',
                             'password': '1'
                             },
                            {"domain": "ysb", "protocol": "https://",
                             "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": "443",
                             'username': '13550087714',
                             'password': '123456'
                             }, {"domain": "partner", "protocol": "https://",
                                 "host": "partner.llzby.top",
                                 "port": "443", 'username': '13550088888',
                                 'password': '123456'
                                 }],
                "DBConnection": {"host": "pc-2ze8c757mjh350kql-public.rwlb.rds.aliyuncs.com", "port": "3306",
                                 "user": "lldb_dev", "password": "LLdev#2022zby",
                                 "database": "nearby_travel", "charset": "utf8"}
            }}

        pro_environment = {
            "pro_environment": {
                "session": [{"domain": "oa", "protocol": "https://", "host": "oasd.lianlianlvyou.com", "port": "443",
                             'username': '13550087714',
                             'password': '1'
                             },
                            {"domain": "ysb", "protocol": "https://",
                             "host": "pre-server-app-business.lianlianlvyou.com",
                             "port": "443",
                             'username': '13550087714',
                             'password': '123456'
                             }, {"domain": "partner", "protocol": "https://",
                                 "host": "partner.llzby.top",
                                 "port": "443", 'username': '13550088888',
                                 'password': '123456'
                                 }],
                "DBConnection": {"host": "pc-2ze8c757mjh350kql-public.rwlb.rds.aliyuncs.com", "port": "3306",
                                 "user": "lldb_dev", "password": "LLdev#2022zby",
                                 "database": "nearby_travel", "charset": "utf8"}
            }}

        return [test_environment, dev_environment, pro_environment]





if __name__ == '__main__':
    s = Settings()
    print(s.email())
