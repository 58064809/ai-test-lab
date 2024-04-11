# coding=utf-8
# 2022/8/1 11:27

from util.log_handle import log
from util.request_control import RequestControl
from util.yaml_handle import YamlHandle
from util.enum import *
import pytest,time
import urllib3,requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pytest_addoption(parser):
    parser.addini("env", help="choose env: test,dev,prod", type=None, default="test")


@pytest.fixture(scope="session",autouse=True)
def set_env(request):
    env = request.config.getini("env").upper()
    conf = YamlHandle().get_activation()
    if not hasattr(ENV,env):
        conf[ENV.Active.value]['activation'] = '环境名错误，可选环境名:TEST,DEV,PRO'
        YamlHandle().update_activation(conf)
        raise Exception("环境名错误，可选环境名:TEST,DEV,PRO")
    else:
        if env is None or env == '':
            conf[ENV.Active.value]['activation'] = 'test'
        else:
            conf[ENV.Active.value]['activation'] = env.upper()
        YamlHandle().update_activation(conf)
        log.info("运行环境：%s" % conf[ENV.Active.value]['activation'].upper())


@pytest.fixture(scope="session",name="oa")
def get_oa_token(request):
    session = YamlHandle().get_session
    resp = RequestControl(Domain.OA.value).request_method("/common/open/login/loginByPassword", "JPOST", param={
        "phoneNumber":session[Domain.OA.value]['username'],
        "password": session[Domain.OA.value]['password']
    }).json()
    conf = YamlHandle().get_activation()
    env = request.config.getini("env").upper()
    env_name = list(conf[getattr(ENV, env).value].keys())[0]
    conf[getattr(ENV, env).value][env_name]['session'][Domain.OA.value]['headers']['Authorization'] = resp['data']['token']
    YamlHandle().update_activation(conf)
    return resp['data']['token']
@pytest.fixture(scope="session")
def login_ysb_get_pubEncrypt():
    session = requests.session()
    sess = YamlHandle().get_session
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
        'encStr': '{"type":1,"account":"%s","password":"%s","reqTime":%s}etype:rsa2'%(sess[Domain.YSB.value]['username'],sess[Domain.YSB.value]['password'],int(time.time() * 1000)),
        'etype': 'rsa2'}
    resp = session.post(url, data,verify=False).json()
    return resp['data']

@pytest.fixture(scope="session",name="ysb")
def get_ysb_token(request,login_ysb_get_pubEncrypt):
    resp = RequestControl(Domain.YSB.value).request_method("/app/business/user/login", "JPOST", param={
            "clientPublicKey":"",
            "encryptedData": login_ysb_get_pubEncrypt
                }).json()
    conf = YamlHandle().get_activation()
    env = request.config.getini("env").upper()
    env_name = list(conf[getattr(ENV, env).value].keys())[0]
    conf[getattr(ENV, env).value][env_name]['session'][Domain.YSB.value]['headers']['Authorization'] = resp['data']['token']
    YamlHandle().update_activation(conf)
    return resp['data']['token']



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