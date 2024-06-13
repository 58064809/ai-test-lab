# coding=utf-8
# 2024/5/29 上午9:51

import requests, json, re

x = [1011234,
     1010393,
     1010391,
     1010390,
     1010387,
     1010386,
     1010337,
     1007091,
     1010079,
     1009864,
     1009310,
     1009298,
     1010079]

for item in x:
    print(item)
    resp = requests.session().get(
        'https://oas.lianlianlvyou.com/technology/common/tool/product/moss/onlineLocation?productId=%s'%item, headers={
            "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2Jhc2VfaWQiOiIxOTc2MnwxNzE3NDk1NDk5MDc4In0.jgnD5vJXWyqSbN3WhjS9u6mQ84kIceYbpJhPQqzh0dA"}).json()
    for i in resp['data']:
        i['status'] = True

    resp_send = requests.session().post(
        'https://oas.lianlianlvyou.com/product/v3/onLineSite/updateProductSiteStatus',
        json=resp['data'],
        headers={
            "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2Jhc2VfaWQiOiIxOTc2MnwxNzE3NDk1NDk5MDc4In0.jgnD5vJXWyqSbN3WhjS9u6mQ84kIceYbpJhPQqzh0dA"}).json()
    print(resp_send)
    if resp_send['code'] == 200:
        print('成功')
    else:
        print('失败')
