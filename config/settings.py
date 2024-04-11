# coding=utf-8
# 2024/3/28 11:51


from pathlib import Path

# ROOT
BASE_PATH = Path(__file__).parent.parent.resolve()
# 配置
CONFIG_PATH = BASE_PATH.joinpath('config').resolve()
# driver
CHROME_EXECUTABLE_PATH = BASE_PATH.joinpath('driver_tools','chromedriver.exe').resolve()
# 数据源
SOURCE_DATA_PATH = BASE_PATH.joinpath('data').resolve()
# 报告
REPORT_PATH = BASE_PATH.joinpath('report').resolve()
REPORT_RESULT_PATH = REPORT_PATH.joinpath('report_result').resolve()
REPORT_HTML_PATH = REPORT_PATH.joinpath('report_html').resolve()
# 截图
CAPTURE_SCREEN_PATH =  REPORT_PATH.joinpath('image').resolve()
# 日志路径
LOG_PATH = BASE_PATH.joinpath('log').resolve()
# 图像识别断言
EXISTS_PNG = BASE_PATH.joinpath('exists_png').resolve()

