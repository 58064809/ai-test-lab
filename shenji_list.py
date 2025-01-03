# coding=utf-8
# 2024/10/15 10:11


from openpyxl import load_workbook
import warnings
import requests,re,datetime

warnings.filterwarnings("ignore")
class SJ:
    def __init__(self):
        self.session = requests.session()
        self.id = 3084140
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'teamType=1_1_0; clientId=d79b9d63-d972-425e-8bad-03b8c48df093; XSRF-TOKEN=816079c7-40ee-4724-9011-fdb78c8d4599; cf=287d2fb88a4f25bf7ab3bb552055cb06; SameSite=Lax; exp=89cd78c2; c=auth-by-wechat%3Dtrue%2Cproject-permission-management%3Dtrue%2Centerprise-permission-management%3Dtrue%2C5c58505d; code=artifact-reforge%3Dfalse%2Casync-blocked%3Dtrue%2Cauth-by-wechat%3Dtrue%2Cci-qci%3Dfalse%2Cci-team-step%3Dfalse%2Cci-team-templates%3Dfalse%2Ccoding-flow%3Dfalse%2Ccoding-ocd-java%3Dfalse%2Ccoding-ocd-pages%3Dtrue%2Centerprise-permission-management%3Dtrue%2Cmobile-layout-test%3Dfalse%2Cproject-permission-management%3Dtrue%2Cservice-exception-tips%3Dfalse%2Ctencent-cloud-object-storage%3Dtrue%2C5b585a51; login=58c5052a-3dd9-4368-b4ac-0c8f379383b7; ac=b3ebc4c4-65c5-4393-9271-9ec6436e1cd4; eid=737ebe20-7c70-46db-98ee-4a0572560646; enterprise_domain=llgroup; coding_demo_visited=1',
            'Priority': 'u=1, i',
            'Referer': 'https://llgroup.coding.net/p/ops-cicd/ci/job?id=%s'%self.id,
            'Sec-CH-UA': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-XSRF-TOKEN': '816079c7-40ee-4724-9011-fdb78c8d4599'
        }
        self.filename = r"C:\Users\ll07\Desktop\23年需求整理.xlsx"
        self.workbook = load_workbook(self.filename)
        self.sheet = self.workbook['ll-server-contract']

    def get_list(self):
        for j in range(1,3):
            url = "https://llgroup.coding.net/api/user/llgroup/project/ops-cicd/ci/job/{}/builds?page={}&pageSize=100&isMine=false&ref=".format(self.id,j)
            resp = self.session.get(url, headers=self.headers).json()
            for item in self.sheet.rows:
                if item[1].value is not None and item[1].value.startswith("#"):

                    for a in resp['data']['list']:
                        first_match = re.search(r'\d+', item[1].value)
                        if int(a['number']) == int(first_match.group()):
                            dt_object = datetime.datetime.fromtimestamp(a['created_at']/1000)
                            formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                            print(formatted_time+'\n')
                            # print(a['commitPath']+'\n')


if __name__ == '__main__':
    sj = SJ()
    sj.get_list()


