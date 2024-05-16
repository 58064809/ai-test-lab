# coding=utf-8
# 2022/8/1 11:27

from util.log_handle import log
from util.request_control import RequestControl
from util.config_handle import ConfigHandle
from util.enum import *
from util.model import EnvModel
from config.settings import Settings
from pydantic import ValidationError
import pytest, time
import urllib3, requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def pytest_addoption(parser):
    '''添加pytest.ini  env'''
    parser.addini("env", help="choose env: TEST,DEV,PROD", type=None, default="TEST")


@pytest.fixture(scope="session", autouse=True)
def set_env(request):
    env = request.config.getini("env").upper()
    EnvModel(env=ENV[env].value)
    log.success("运行环境：%s" % env)


@pytest.fixture(scope="session", name="oa", autouse=True)
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


@pytest.fixture(scope="session", name="ysb", autouse=True)
def get_ysb_token(request, login_ysb_get_pubEncrypt):
    '''获取营商宝Token'''
    resp = RequestControl('ysb').request_method("/app/business/user/login", "POST", type='json', data={
        "clientPublicKey": "",
        "encryptedData": login_ysb_get_pubEncrypt
    }).json()
    assert resp['code'] == 200, "获取营商宝token失败"
    token = resp['data']['token']
    Settings.global_params.update({'YSB': {"Authorization": token}})


def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    log.success(f"用例总数: {_TOTAL}")
    log.success(f"通过用例数: {_PASSED}")
    log.error(f"异常用例数: {_ERROR}")
    log.error(f"失败用例数: {_FAILED}")
    log.warning(f"跳过用例数: {_SKIPPED}")
    log.info("用例执行时长: %.2f" % _TIMES + " s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        log.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        log.info("用例成功率: 0.00 %")
