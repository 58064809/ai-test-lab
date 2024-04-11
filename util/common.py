# coding=utf-8
# 2024/3/28 15:13


from util.log_handle import log
import pendulum

class Common:
    def current_time(self, format=None):
        '''
        当前时间  YYYY MM DD HH mm ss
        '''
        if format:
            return pendulum.now().format(format)
        return pendulum.now().to_datetime_string()



if __name__ == '__main__':
    log.debug(Common().current_time())


