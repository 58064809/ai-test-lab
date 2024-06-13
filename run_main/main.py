# -*- coding: utf-8 -*-
# date = 2021/7/1
from config.settings import REPORT_RESULT_PATH, REPORT_HTML_PATH
import os


class RunMain:
    @staticmethod
    def run_main():
        try:
            os.system('pytest')
            # 生产静态报告
            os.system('allure generate %s -o %s --clean' % (REPORT_RESULT_PATH, REPORT_HTML_PATH))
            # 也可以打开web服务供其他人查看
            # os.system('allure open %s'%REPORT_HTML_PATH)

            # 服务的方式
            # os.system('allure serve %s'%REPORT_RESULT_PATH)
            # os.system('allure open %s'%REPORT_HTML_PATH)

        except Exception as e:
            # 如有异常，相关异常发送邮件
            # send_email = SendEmail(AllureFileClean.get_case_count())
            # send_email.error_mail(e)
            raise e


if __name__ == '__main__':
    RunMain.run_main()
