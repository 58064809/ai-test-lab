# coding=utf-8
# 2024/6/5 下午4:24

import requests
resp = requests.session().post('https://partner.llzby.top/withdraw/service/test').json()
print(resp)
