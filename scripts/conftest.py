# coding=utf-8
# 2022/8/1 11:27

from util.log_handle import log
from util.request_control import RequestControl
from util.config_handle import ConfigHandle
from util.enum import *
from util.model import EnvModel
from config.settings import Settings,email,ZIP_PATH,REPORT_HTML_PATH
from pyfiglet import Figlet
import pytest, time
import urllib3, requests,zipfile,yagmail

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

f = Figlet(font='slant')
def pytest_addoption(parser):
    '''添加pytest.ini  env'''
    parser.addini("env", help="choose env: TEST,DEV,PROD", type=None, default="TEST")
    parser.addini("switch", help="[oa,ysb,partner]", type=None, default="")



@pytest.fixture(scope="session", autouse=True)
def set_env(request):
    log.info("\n" + f.renderText('Start Test'))
    env = request.config.getini("env").upper()
    EnvModel(env=ENV[env].value)
    log.success("运行环境：%s" % env)


@pytest.fixture(scope="session", name="oa", autouse=ConfigHandle().switch_domain['oa'])
def get_oa_token(request):
    '''获取OAToken'''
    session = ConfigHandle().get_domain(Domain.OA.value)
    resp = RequestControl('oa').request_method("/common/open/login/loginByPassword", "POST", type='json', data={
        "phoneNumber": session['username'],
        "password": session['password']
    }).json()
    assert resp['code'] == 200, "获取OAtoken失败"
    token = resp['data']['token']
    Settings.global_params.update({'OA': {"Authorization": token}})


@pytest.fixture(scope="session")
def login_ysb_get_pubEncrypt():
    session = requests.session()
    sess = ConfigHandle().get_domain(Domain.YSB.value)
    url = 'https://www.bejson.com/Bejson/Api/Rsa/pubEncrypt'

    publicKey = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuAltXJI4kMQkucWCeLGK4Zyqw7VUp1JYS1GkJb0eJK
CgxqJBzwjl8XpStA1hCv9BEX6SEsm/d2T6SDo+G6ySpfV0RQeZ7v32kE9+Eh0BK1Q8wU91nCa1CM9yfBhKXsQ3D
Kq2am5oLryNWXdKLXZPgoJbuIONG2G4oKakwUMX3aASp3Cj3rNXLea8ilXjFZ+OEp0DuZ4CsasO1MTaBS84mJhn
zRNbuhHq5qyrVI02jw7Fim8siIBsmDDHgBd4l9hj6KAAr0jf9JOHaOp+KxfH76taqqaXI5lZIPG7lCP65iBuNNE
qDSc21abcPhgvgK5K4xj9p5sG+V1FBISCE0dPrQIDAQAB
-----END PUBLIC KEY-----'''
    data = {
        'publicKey': publicKey,
        'encStr': '{"type":1,"account":"%s","password":"%s","reqTime":%s}etype:rsa2' % (
            sess['username'], sess['password'], int(time.time() * 1000)),
        'etype': 'rsa2'}
    resp = session.post(url, data, verify=False).json()
    return resp['data']


@pytest.fixture(scope="session", name="ysb", autouse=ConfigHandle().switch_domain['ysb'])
def get_ysb_token(request, login_ysb_get_pubEncrypt):
    '''获取营商宝Token'''
    resp = RequestControl('ysb').request_method("/app/business/user/login", "POST", type='json', data={
        "clientPublicKey": "",
        "encryptedData": login_ysb_get_pubEncrypt
    }).json()
    assert resp['code'] == 200, "获取营商宝token失败"
    token = resp['data']['token']
    Settings.global_params.update({'YSB': {"Authorization": token}})


@pytest.fixture(scope="session", name="partner", autouse=ConfigHandle().switch_domain['partner'])
def get_partner_token(request):
    '''获取OAToken'''
    session = ConfigHandle().get_domain(Domain.PARTNER.value)
    resp = RequestControl('partner').request_method("/sys/login", "POST", type='json', data={
        "username": session['username'],
        "password": session['password'],
        "captcha": "0000",
        "remember": True,
        "checkKey": int(time.time() / 1000)
    }).json()
    assert resp['code'] == 200, "获取合伙人Token失败"
    token = resp['result']['token']
    Settings.global_params.update({'PARTNER': {"X-Access-Token": token}})


def count_cases(stats, category, exclude_teardown=True):
    """
    统计指定测试结果类别下的用例数，排除teardown阶段的用例。
    """
    return len([i for i in stats.get(category, []) if i.when != 'teardown' if exclude_teardown])

def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    _PASSED = count_cases(terminalreporter.stats, 'passed')
    _ERROR = count_cases(terminalreporter.stats, 'error')
    _FAILED = count_cases(terminalreporter.stats, 'failed')
    _SKIPPED = count_cases(terminalreporter.stats, 'skipped', exclude_teardown=False)  # teardown阶段的跳过用例可能需要特别处理
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime

    if _TOTAL == 0:
        _RATE = 0
    else:
        _RATE = _PASSED / _TOTAL * 100

    log.success(f"用例总数: {_TOTAL}")
    log.success(f"通过用例数: {_PASSED}")
    log.error(f"异常用例数: {_ERROR}")
    log.error(f"失败用例数: {_FAILED}")
    log.warning(f"跳过用例数: {_SKIPPED}")
    log.info(f"用例执行时长: {round(_TIMES, 2)} s")

    log.info(f"用例成功率: {round(_RATE, 2)} %") if _TOTAL != 0 else log.info("用例成功率: 0.00 %")

    log.info("\n" + f.renderText('End'))

    if email.get('switch', False):
        subject = "接口自动化报告"
        sender = email.get('user')
        password = email.get('password')
        host = email.get('host')
        to = email.get('to')
        tester = email.get('tester')
        content = f"""
                   各位同事, 大家好:
                   自动化用例运行时长：<strong>{round(_TIMES, 2)} s</strong>， 目前已执行完成。
                   ---------------------------------------------------------------------------------------------------------------
                   测试人：<strong> {tester} </strong> 
                   ---------------------------------------------------------------------------------------------------------------
                   执行结果如下:
                   &nbsp;&nbsp;用例运行总数:<strong> {_TOTAL} 个</strong>
                   &nbsp;&nbsp;通过用例个数（passed）: <strong><font color="green" >{_PASSED} 个</font></strong>
                   &nbsp;&nbsp;失败用例个数（failed）: <strong><font color="red" >{_FAILED} 个</font></strong>
                   &nbsp;&nbsp;异常用例个数（error）: <strong><font color="orange" >{_ERROR} 个</font></strong>
                   &nbsp;&nbsp;跳过用例个数（skipped）: <strong><font color="grey" >{_SKIPPED} 个</font></strong>
                   &nbsp;&nbsp;成  功   率:<strong><font color="green" >{round(_RATE, 2)}%</font></strong>
                   **********************************
               """

        attachments = email.get('attachments',False)
        if attachments:  # 增加附件配置选项
            with zipfile.ZipFile(attachments[0], "w", zipfile.ZIP_DEFLATED) as z:
                for i in REPORT_HTML_PATH.rglob("*"):
                    z.write(i)

        with yagmail.SMTP(user=sender, password=password, host=host) as yagmail_server:
            yagmail_server.send(to=to, subject=subject, contents=[content], attachments=attachments)