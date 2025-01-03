# coding=utf-8
# 2024/4/8 16:24


from util.case_handle import CaseHandle
import pytest,allure

cases = CaseHandle('partner.yaml')


@allure.epic(cases.get_allureEpic)
@allure.feature(cases.get_allureFeature)
class TestPartner:

    @pytest.mark.skipif(cases.case_common['skip'],reason=cases.get_allureEpic if not cases.case_common['skip'] else cases.case_common['skip_reason'])
    @pytest.mark.parametrize('case',cases.get_cases)
    def test_case1(self,case):
        allure.dynamic.story(cases.get_allureStory)
        allure.dynamic.title(case['title'])
        cases.case_run(case)






