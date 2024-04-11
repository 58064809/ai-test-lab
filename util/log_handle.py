# # -*- coding: utf-8 -*-
# # date = 2021/7/7
import pendulum
from loguru import logger
from config.settings import LOG_PATH
import sys


class Loggings:
    _instance = None

    def __init__(self):
        self.logger_handler()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_log_path(self):
        return LOG_PATH.joinpath(pendulum.now().format("YYYY-MM-DD at HH-mm-ss") + ".log")

    def logger_handler(self):
        LOG_PATH.mkdir(parents=True, exist_ok=True)
        logs_str_list = [path for path in LOG_PATH.iterdir()]
        if len(logs_str_list) > 10:
            for i in range(len(logs_str_list) - 10):
                logs_str_list.pop(0).unlink()

        logger.remove()
        logger.add(sys.stdout, format="<green>{time:YYYYMMDD HH:mm:ss.SSS}</green> | "  # 颜色>时间
                                      "{process.name} | "  # 进程名
                                      "{thread.name} | "  # 进程名
                                      "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                                      ":<cyan>{line}</cyan> | "  # 行号
                                      "<level>{level}</level>: "  # 等级
                                      "<level>{message}</level>", enqueue=True,  # 日志内容
                   backtrace=True, diagnose=True, catch=True)
        logger.add(self.get_log_path(),
                   format="<green>{time:YYYYMMDD HH:mm:ss.SSS}</green> | "  # 颜色>时间
                          "{process.name} | "  # 进程名
                          "{thread.name} | "  # 进程名
                          "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                          ":<cyan>{line}</cyan> | "  # 行号
                          "<level>{level}</level>: "  # 等级
                          "<level>{message}</level>",  # 日志内容
                   rotation="500MB", retention='1 days', encoding="utf-8", enqueue=True,
                   backtrace=True, diagnose=True, catch=True)

    @property
    def get_logger(self):
        return logger


'''
# 实例化日志类
'''
log = Loggings().get_logger

if __name__ == '__main__':
    log.debug('调试代码')
    log.info('输出信息')
    log.success('输出成功')
    log.warning('错误警告')
    log.error('代码错误')
    log.critical('崩溃输出')

