# -*- coding: utf-8 -*-
# @Time    : 2021/8/14 12:21
# @Author  : Flora.Chen
# @File    : yagmail_bot.py
# @Software: PyCharm
# @Desc: 通过第三方模块yagmail发送邮件

# 标准库导入
import os
# 第三方库导入
from util.log_handle import log
import yagmail


class YagEmailServe:
    def __init__(self, host, user, password):
        """
        user(发件人邮箱), password(邮箱授权码), host(发件人使用的邮箱服务 例如：smtp.163.com)
        """
        self.host = host
        self.user = user
        self.password = password

    def send_email(self, info: dict):
        """
        发送邮件
        :param info:包括,contents(内容), to(收件人列表), subject(邮件标题), attachments(附件列表)
        info = {
            "subject": "",
            "contents": "",
            "to": "",
            "files": ""
        }
        :return:
        """
        try:
            msg = f'''
            ======================================================
            -------------Start：发送邮件--------------------
            用户名: {self.user}
            密码: {self.password}
            host: {self.host}
            邮件内容: {info}
            =====================================================
            '''
            log.info(msg)
            yag = yagmail.SMTP(
                user=self.user,
                password=self.password,
                host=self.host)
            # 如果存在附件，则与邮件内容一起发送附件，否则仅发送邮件内容
            if info.get("attachments") and os.path.exists(info['attachments']):
                yag.send(
                    to=info['to'],
                    subject=info['subject'],
                    contents=info['contents'],
                    attachments=info['attachments'])
            else:
                log.warning(f"\n请检查邮件内容info是否存在附件，info中应该存在键值：attachments\n"
                               f"请检查附件地址是否正确 --> info['attachments'] 应该是一个有效的路径\n"
                               f"当前仅发送邮件内容，不发送附件~")
                yag.send(
                    to=info['to'],
                    subject=info['subject'],
                    contents=info['contents'])
            yag.close()
            log.info("\n======================================================\n" \
                        "-------------End：发送邮件--------------------\n"
                        "发送邮件成功\n" \
                        "=====================================================")
        except Exception as e:
            log.error(f"发送邮件失败，错误信息: {e}")
