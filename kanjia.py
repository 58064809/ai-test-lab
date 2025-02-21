# coding=utf-8
# 2025/2/19 13:35


import requests, time

token_list = [
    'o8LSF6xD1VD5bsURvWy1XRcTW0nE',
    'o8LSF65zpv2ghLSPkqQ6PjQcku_o',
    'o8LSF62Z-QJEeH_fPtC4qU6-Uwuw',
    'o8LSF61FwTyP8RIZAXMMSyQTopyo',
    'o8LSF68mKdSpPQScO4gCrdtNePJs',
    'oFQ5Z7DF8OW1kcXQ9AJDb1vRcSEQ',
    'oFQ5Z7DgRJaFfFxlmuosUEMEYTUQ',
    'oFQ5Z7MOcC4XdpmDHStvRw487IRc',
    'oFQ5Z7Lgd9Ysf - 5TA7wmwEafTqnE',
    'oFQ5Z7HMpTDIkHlc8 - w_9ynMzzz8',
    'oFQ5Z7LWPUi_vbyVY8rmX4sKT1s8',
    'WL8dce49d78f9df11d09e8a9311586',
    'ocG0OwOWoaVXgTNnMNvL5wuv8Gk4',
    'oC2gP6C1Z7eKEyHsh3GnNBsjDcIE',
    'oC2gP6NKmQzu9k0t_4O2G8v11111',
    'WL9bd78711ca7a73f270c150b52d97',
    'WL327708dd10d68b1361ad3addbaca',
    'WL8982bdc05395c01f87199588e06e',
    'WL8e4b04b37c4cf6dcb56857808589',
    'WL31c49b512f199bc6f8734034a87d',
    'WL265e5f95d04550eb5b53ab39f486',
    'WL6d70cb65d15211726dcce4c0e971',
    'WL02bf1a8bb2a792e32a8b9d57c293',
    'WL02a32ad2669e6fe298e607fe7cc0',
    'WL1b4219720cc03460e2e65140f5ba',
    'LLdd1b70364ad3aec3nrYckFGPIG',
    'LL30f7d12b57d6c3e1yrHQuZ3C9W',
    'LL744145bf276900ecem3niFsMcE',
    'LL9bbd060dada113a4KfVtGQHl2s',
    'oC2gP6LrriCDv8OTf_wIWrjUHEg4',
    'WL4cfbfb28ee66aceab7be17065ebd',
    'LL09f8a904289a0dd3lqKzv7aAhk',
    'LLc416cf4a683d9dceTJNYp1f2up',
    'oC2gP6Kj3a - eY1tj4dM4tzoBhvQg',
    'oC2gP6PEZdpVCJ3Fc09iIYT7vNdU',
    'LLfaf1e179d6e51694QhwfNjfgfJ',
    'oC2gP6HWBkhDXe4tyna6cJ9ejXY4',
    'WLd921c3c762b1522c475ac8fc0811',
    'oC2gP6J6WFgC1yazMGEun6Bt - XP4',
    'LL4af04a95a1c6d8e3IXVyPnwqur',
    'WLed1c1607401e06c70d9e92918ddd',
    'LL841164ab224d8e83MBgDJNU2aD',
    'LL1198ea710b5e4832AWJhS1lUIw',
    'LLa3a70be9df60f1fecsIXYFTDOn',
    'WLa6a95a9dc083cc3218868b33c9b7',
    'LLb25f56774d85d3a3tcKqpgwbPa',
    'LL7060ef1a866849bdDE1dK2pJQ3',
    'LL08a81f73aab4c68dNugq11fgIm',
    'LL819283db480def92uA68d4UWV8',
    'LL550d05f73ea248d5CHBn3ZyQKl',
    'LL778c6a23653560e22sgHeYM96Q',
    'LLf9436a061f360743KfffAf5RTF',
    'LLf0c1c931312a92d8ya0e5J3jcR',
    'LL4621ea8beeb3a0bbRuGHo5X079',
    'LLf0d5c8ac80803038woYbsrqpLk',
    'LLb7a03b38508428fb1KjxEoGpBV',
    'LLb2070f3f394088b1rpcKpd6CS2',
    'LL06a2b6be3b73fd96AzcAT66nRM',
    'LLc5d8a69f31f7956ccvnJaZmoHC',
    'LLb9d3bd1df3524f71usnoHAtPO9',
    'LL2469249ec6cfec785c3V2IQHjX',
    'LL91d14883016611d5bhlKbK4pRX',
    'LL0387fe6c6d54e939pFZT97tnJ6',
    'LLb54d155c3149798b0XOjdMzxYP',
    'LL079f01c546459a8cMz1FyMmXvL',
    'oC2gP6NbPjdTKnaBTyohl2IGYmms',
    'WLed21b54c417d6d8638aef8efc652',
    'WLec5ec3ab3ae96eb7f5981a59ab48',
    'WL251ea3991fd165bfd231aa53cd43',
    'WL5c10d595f3dfb3c6605a34f0c1a4',
    'WLf19a4a205b6fc44fcf0af19e44d7',
    'oC2gP6BB5LVSWJIOymzQ2yhKhjA0',
    'oC2gP6NKtDY14CaARFMVqv - YgIvo',
    'oC2gP6OeKE_T - cWmzstCh0ZwE2Ks',
    'oC2gP6Een4LE210blW_LZ47L9MaY',
    'oC2gP6LYv95hD0G_ULb0jL7sh3Fc',
    'oC2gP6JTcUYDjRBiZb2oGiXJdrsk',
    'oC2gP6AAeAj2Dn9JOPKG418u8f3I',
    'oC2gP6EvcoSpQ_nPyvJrjr8u2OwQ',
    'oC2gP6GUnDG4VE242v9nrXwDISB0',
    'oC2gP6PDpGe1UXFvFENHgMrtU73U',
    'oC2gP6EVePY5Ol6hQZ5eMfYIrr0Q',
    'WLa70a6499f486af3fcc04698aa3f2',
    'oC2gP6LxKiEA6YPG9j8sRhw0iSeU',
    'oC2gP6OxnqYKsbORL8cnqo_HZcBM',
    'oC2gP6AW0munuYiTaBNK1BLuioas',
    'ocG0OwPwvqk_twa_7Ju - E996O3qA',
    'oC2gP6PMnPjZnHR6MVSPCnHsioFY',
    'WLfbe486dc4c014eb61a0c91e34cc6',
    'oC2gP6JBGy7_53XZT8HxYEIGtJsI',
    'oC2gP6Hmw6jpsHjf7FR2LafnJ - g0',
    'oC2gP6C1Z7eKEyHsh3GnNBsjDcIE',
    'oC2gP6CrSaHlmdzfdXTXdfA73ook',
    'oC2gP6AjPBhwRwrIPpr0PR0aYtks',
    'WL9f6baa1a206155de9806efc35da9',
    'WL6d8fa950c459e372f77ea0a54a54',
    'oC2gP6NCjGDelSXegR9rTJt6qDEo',
    'LLca7dc602d6024c35yBYbHlr4hR',
    'oC2gP6I4ygxvVS6oZyJxaFOCuLhI',
    'LLd3d6d5520d3ca07cCLq3FbKEHX'
]


class LLK:
    def __init__(self):
        self.productId = "62714765"
        self.itemsId = "4662795"
        self.session = requests.session()

    def kj(self):
        url = 'https://apid.lianlianlvyou.com/llk/bargain/doBargain'
        salePrice = 10000
        for index, item in enumerate(token_list):
            item = item.replace(' ', '')
            headers = {
                'Authorization': item,
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'signType': 'MD5'
            }
            data = {"token": item, "timestamp": int(time.time() * 1000), "productId": self.productId,
                    "itemsId": self.itemsId}
            resp = self.session.post(url, json=data, headers=headers).json()
            if resp.get("data"):
                bl = resp['data'] / salePrice * 100
                salePrice = salePrice - resp['data']
                print("第%s刀砍了%s元，剩余%s元,比例为%s" % (index + 1, resp['data'] / 100, salePrice / 100, bl) + "%")
            else:
                print("第%s刀失败" % (index + 1))
                print(resp)

    def create_order(self):
        url = "https://apid.lianlianlvyou.com/llk/sale_order/create"
        data = {"token": "o8LSF62Z-QJEeH_fPtC4qU6-Uwuw", "timestamp": int(time.time() * 1000), "payAmount": 100,
                "orderAmount": 100, "count": 1, "productItemId": 4662797, "customerName": "13550087714",
                "customerPhoneNumber": "13550087714", "shareUserId": ""}
        headers = {
            'Authorization': "o8LSF62Z-QJEeH_fPtC4qU6-Uwuw",
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'signType': 'MD5'
        }
        resp = self.session.post(url, json=data, headers=headers).json()
        print(resp)


if __name__ == '__main__':
    llk = LLK()
    # llk.kj()
    llk.create_order()