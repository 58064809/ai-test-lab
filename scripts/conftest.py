# coding=utf-8
# 2022/8/1 11:27

from util.log_handle import log
from util.yaml_handle import YamlHandle
from util.enum import ENV
import pytest,time


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


# @pytest.fixture(scope="session",name="oa")
# def get_oa_token(get_env):



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