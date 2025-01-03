# coding=utf-8
# 2024/9/18 15:02

from openpyxl import load_workbook
import requests


class ChengDai:
    def __init__(self):
        self.session = requests.session()
        self.host = 'https://partner-api.lianlian.net.cn'
        self.token = {
            "x-access-token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MjY2NzE5NjIsInVzZXJuYW1lIjoianNfYWRtaW4ifQ.NiCjbFD5EYzLU14Bx695weiMRhwQf-QGEz_111GOw6A"}
        self.filename = r"D:\TestHome\Demo\城代账号.xlsx"
        self.workbook = load_workbook(self.filename)
        self.sheet = self.workbook['Sheet1']

    def get_location(self):
        url = 'https://oas.lianlianlvyou.com/common/open/location/visible/'
        resp = self.session.get(url=url, headers=self.token).json()
        location = resp['data']
        return location


    def get_area(self):
        url = self.host + '/locaion/area?_t=1726642910&pid=100000'
        resp = self.session.get(url=url, headers=self.token).json()
        return resp['result']

    def get_city(self,id):
        url = self.host + '/locaion/area?_t=1726642910&pid=%s'%id
        resp = self.session.get(url=url, headers=self.token).json()
        return resp['result']

    def partner_save_info(self):
        url = self.host + '/partner/save/info'
        locations = self.get_location()
        count = 0
        for item in self.sheet.rows:
            for location in locations:
                if location['locationName'] == item[4].value:
                    for area in self.get_area():
                        if area['name'] in item[2].value or item[2].value in area['name']:
                            for city in self.get_city(area['id']):
                                if city['name'] in item[3].value or item[3].value in city['name']:
                                    data = {"productAuditType": 1, "city": item[3].value, "cityCode": city['id'], "province": item[2].value,
                                            "provinceCode": area['id'], "district": "", "districtCode": "", "partnerName": item[0].value, "locationId": location['locationId'],
                                            "locationName": item[4].value, "phone": item[1].value, "status": 1, "userType": 3, "settleCycles": 0,
                                            "subjectType": 1, "userCommissionRate": 0}
                                    count += 1
                                    resp = self.session.post(url=url, headers=self.token, json=data).json()
                                    print(resp)
        print(count)

if __name__ == '__main__':
    cd = ChengDai()
    cd.partner_save_info()
