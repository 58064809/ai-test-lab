import  requests


url = 'https://thirdd.lianlianlvyou.com/nearby/v/third/service/order/request'
data =[{
    "id":1,
    "codeType": 112,
    "orderId": 100100999,
    "productItemId": 4662579,
    "usingDate": "2022-04-14",
    "amount": 2,
    "bookingCustomerName": "test",
    "bookingCustomerPhoneNumber": "13598464657",
    "memo": "",
    "customerName": "customer",
    "customerPhoneNumber": "13982093975",
    "idCard": "410305199712113016",
    "idCardType": "0",
    "orderOrigin":"dy"
}]


resp = requests.session().post(url,json=data).json()
print(resp)

