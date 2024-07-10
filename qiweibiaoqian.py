# coding=utf-8
# 2024/7/2 下午4:59
import time

from dbutils.pooled_db import PooledDB
from pymysql.cursors import SSDictCursor
from util.log_handle import log
from requests import adapters
from aiolimiter import AsyncLimiter
import requests, pendulum, pathlib, pymysql
import asyncio,aiohttp


rate_limit = AsyncLimiter(140000, 3600)

class Connection:
    db = None
    session = None
    @classmethod
    def get_session(cls):
        if cls.session is None:
            requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
            cls.session = requests.session()
            cls.session.keep_alive = False  # 关闭多余连接
        return cls.session
    @classmethod
    def get_db_connect(cls):
        if cls.db is None:
            cls.pool = PooledDB(
                creator=pymysql,
                maxconnections=None,  # 连接池允许的最大连接数,0和None表示没有限制
                mincached=3,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                blocking=True,  # False表示不等待然后报错
                host="10.10.100.195",
                port=3306,
                user="root",
                password="123456",
                database="douyin",
            )
            cls.conn = cls.pool.connection()
            cls.cursor = cls.conn.cursor(SSDictCursor)
            cls.db = True
        return cls.conn, cls.cursor

    @classmethod
    def db_close(cls):
        con, cur = cls.get_db_connect()
        cur.close()
        con.close()


class WeiXin:

    def __init__(self):
        self.corpid = "ww2c0040069d754cc0"
        self.corpsecret = "u2tn3-Klcezmkuyxud5zA9YzDuBxsg-cDt9qCKYKIkg"
        self.path = pathlib.Path('./qywx_token.txt')
        self.session = Connection.get_session()
        self.token = self.get_access_token()
        self.connect, self.cursor = Connection.get_db_connect()

    def date_diff(self, keywork='seconds', d1=pendulum.now(), d2=pendulum.now()):
        '''两个时间直接的运算'''
        if keywork == 'years':
            return d1.diff(d2).in_years()
        elif keywork == 'months':
            return d1.diff(d2).in_months()
        elif keywork == 'days':
            return d1.diff(d2).in_days()
        elif keywork == 'hours':
            return d1.diff(d2).in_hours()
        elif keywork == 'minutes':
            return d1.diff(d2).in_minutes()
        else:
            return d1.diff(d2).in_seconds()

    def get_access_token(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            access_token_info = f.read().split(',')
            old_time = pendulum.parser.parse(access_token_info[0])
            expiration_time = access_token_info[1]
            old_token = access_token_info[2]
            if self.date_diff(keywork='secrets', d1=pendulum.now(), d2=old_time) >= int(expiration_time):
                url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
                resp = self.session.get(url).json()
                if resp['errcode'] == 0:
                    with open(self.path, 'w', encoding='utf-8') as f:
                        f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
                    return resp['access_token']
                else:
                    log.error('获取access_token失败')
            else:
                return old_token

    def get_corp_tag_list(self):
        '''查询'''
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={self.token}'
        data = {
            "tag_id": [],
            "group_id": []
        }
        resp = self.session.post(url, json=data).json()
        print(resp)


    def user_del_corp_tag(self):
        '''手动删除标签组'''
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={self.token}'
        data = {
            "group_id": ["etlUx7DQAASvvhGNLwJs9HQgUkj_nxeA","etlUx7DQAARoWo9On0t82PZCxuJ0jXYA"]
        }
        resp = self.session.post(url, json=data).json()
        if resp['errcode'] == 0:
            print('删除标签组成功')
        else:
            print('删除标签组失败')

    def del_corp_tag(self):
        '''删除标签组'''
        sql = 'select `group_id` from `douyin`.`ads_wework_item`'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={self.token}'
        data = {
            "group_id": list({item['group_id'] for item in result})
        }
        resp = self.session.post(url, json=data).json()
        if resp['errcode'] == 0:
            print('删除标签组成功')
            try:
                sql = 'truncate table `douyin`.`ads_wework_item`'
                self.cursor.execute(sql)
                self.connect.commit()
                print('清空表ads_wework_delete_group_id成功')
            except Exception as e:
                log.error(e)
                self.connect.rollback()
        else:
            log.error('删除标签组失败')


    def add_corp_tag(self):
        '''创建组、标签'''
        sql = 'select * from `douyin`.`ads_wework_lable_d`'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for item in result:
            group_name = item['lable_name'].split(':')[0].replace("'", '')
            tag_name = item['lable_name'].split(':')[1].replace("'", '')
            if tag_name:
                url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?access_token={self.token}'
                data = {
                    "group_name": group_name,
                    "tag": [
                        {
                            "name": tag_name
                        }
                    ]
                }
                resp = self.session.post(url, json=data).json()
                if resp['errcode'] == 0:
                    print(f'添加标签组【{group_name}】,【{tag_name}】成功')
                    sql = 'insert into `douyin`.`ads_wework_item`(`group_name`,`group_id`,`tag_name`,`tag_id`) values(%s,%s,%s,%s)'
                    self.cursor.execute(sql, (group_name, resp['tag_group']['group_id'], tag_name, resp['tag_group']['tag'][0]['id']))
                    self.connect.commit()
                else:
                    log.error(f'添加标签组【{group_name}】,【{tag_name}】失败,{resp}')
            time.sleep(0.1)

    def get_all_user(self):
        sql = 'select * from `douyin`.`ads_wework_user_lable_d`'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return list(reversed(result))


    async def mark_tag(self,client,item):
        '''打标'''
        async with rate_limit:
            tag_list = item['lable_name_list'].replace("{", '').replace("}", '').replace("'",'').strip().split(',')
            new_tag_list = []
            for tag in tag_list:
                group_name = tag.split(':')[0]
                tag_name = tag.split(':')[1]
                sql = 'select * from `douyin`.`ads_wework_item` where `group_name`=%s and `tag_name`=%s'
                self.cursor.execute(sql, (group_name, tag_name))
                item_result = self.cursor.fetchall()
                if item_result:
                    new_tag_list.append(item_result[0]['tag_id'])
            url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/mark_tag?access_token={self.token}'
            data = {
                "userid": item['userid'],
                "external_userid": item['unionid'],
                "add_tag": new_tag_list,
            }
            async with client.post(url,json=data) as resp:
                result = await resp.json()
                if result['errcode'] == 0:
                    print(f'给{item["userid"]}打标成功')
                else:
                    print(result)
                    log.error(f'给{item["userid"]}打标失败')


    async def main(self,total):
        timeout = aiohttp.ClientTimeout(total=None)
        connector = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as client:
            tasks = [asyncio.ensure_future(self.mark_tag(client,item)) for item in total]
            await asyncio.wait(tasks)


if __name__ == '__main__':
    wx = WeiXin()
    wx.del_corp_tag()
    wx.add_corp_tag()
    total = wx.get_all_user()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wx.main(total))
    # wx.get_corp_tag_list()
    # wx.user_del_corp_tag()



