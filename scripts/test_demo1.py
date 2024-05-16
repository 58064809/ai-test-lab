# coding=utf-8
# 2024/4/8 16:24


from util.log_handle import log

from util.case_handle import CaseHandle



import pytest,allure

cases = CaseHandle('moss_v3.yaml')

@allure.epic(cases.get_allureEpic)
@allure.feature(cases.get_allureFeature)
class TestDemo1:
    @pytest.mark.skipif(cases.case_common['skip'],reason=cases.case_common['skip_reason'])
    @pytest.mark.parametrize('case',cases.get_cases)
    def test_case1(self,case):
        cases.case_run(case)






