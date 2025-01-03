# import requests
# for i in range(3):
#     resp = requests.session().post(url="http://10.10.100.195/gen_pdf", json={
#         "htmlUrl": "https://cd-nt.lianlianlvyou.com/v2/index.html?#/pages/home/detail?id=1029864",
#         "uploadId": "566", "md5": "478b44ba930debf128d49079acd47844", "fileName": "test17.pdf"})
#
#     print(resp.json())



# 账单生成
import requests
resp = requests.session().get(url="https://partner.llzby.top/account/month_bill/gen", headers={
    "x-access-token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MzM4NTE5NzcsInVzZXJuYW1lIjoiYWRtaW4ifQ.pOAB8cPX8cJjt1Y_hUl6lFO2bWRHMQzUpC3DGM911lc"}).json()
print(resp)
