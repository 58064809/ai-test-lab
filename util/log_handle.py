# coding=utf-8
# 2024/4/12 17:13

from loguru import logger
import sys,pathlib,pendulum
from config.settings import LOG_PATH


class Logging:
    _instance = None

    def __init__(self):
        self.logger_handler()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_log_path(self):
        return LOG_PATH.joinpath(pendulum.now().format("YYYY-MM-DD at HH-mm-ss") + ".log")

    def clean_logs(self):
        """清理日志文件，保留最近10个"""
        logs = list(LOG_PATH.iterdir())
        if len(logs) >= 10:
            for log in logs[:-9]:
                pathlib.Path(log).unlink()

    def logger_handler(self):
        try:
            LOG_PATH.mkdir(parents=True, exist_ok=True)
            self.clean_logs()

            logger.remove()
            logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD at HH:mm:ss.SSS}</green> | "
                                          # "{process.name} | "
                                          # "{thread.name} | "
                                          "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                                          ":<cyan>{line}</cyan> | "
                                          "<level>{level}</level>: "
                                          "<level>{message}</level>", enqueue=True,  # 日志内容
                       backtrace=True, diagnose=True, catch=True)
            logger.add(self.get_log_path(),
                       format="<green>{time:YYYY-MM-DD at HH:mm:ss.SSS}</green> | "
                              # "{process.name} | "
                              # "{thread.name} | "
                              "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                              ":<cyan>{line}</cyan> | "
                              "<level>{level}</level>: "
                              "<level>{message}</level>",  # 日志内容
                       rotation="1024MB", retention='3 days', encoding="utf-8", enqueue=True,
                       backtrace=True, diagnose=True, catch=True)
        except Exception as e:
            print(f"日志配置失败: {e}")

    @property
    def get_logger(self):
        return logger


'''
实例化日志类
'''
log = Logging().get_logger

if __name__ == '__main__':
    log.debug('调试代码')
    log.info('输出信息')
    log.success('输出成功')
    log.warning('错误警告')
    log.error('代码错误')
    log.critical('崩溃输出')