# coding=utf-8
# 2024/7/2 下午4:59

from util.log_handle import log
from other_settings import Connection
from aiolimiter import AsyncLimiter
import  pendulum, pathlib
import asyncio, aiohttp,uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


REQUESTS_PER_SECOND = 5
TIME_PERIOD = 1
MAX_RATE = 5





class TagECommerce:

    def __init__(self):
        self.corpid = "wwa0a08e1fba1d2db1"
        self.corpsecret = "_TfpmSUYgVyQY2NDizxiF5W1Ja0TQSeEaEAFtMu-_jU"
        self.path = pathlib.Path('tag_eCommerce_token.txt')
        self.session = Connection.get_session()
        self.env = 'server'
        self.connect, self.cursor = Connection.get_db_connect(self.env)

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
            result = f.read()
            if result:
                access_token_info = result.split(',')
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
                        print('获取access_token失败')
                else:
                    return old_token
            else:
                url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
                resp = self.session.get(url).json()
                if resp['errcode'] == 0:
                    with open(self.path, 'w', encoding='utf-8') as f:
                        f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
                    return resp['access_token']
                else:
                    log.error('获取access_token失败')

    def del_corp_tag(self):
        '''删除标签组'''
        token = self.get_access_token()
        try:
            sql = 'truncate table `posttag`.`ads_wework_item_ecommerce`'
            self.cursor.execute(sql)
            self.connect.commit()
            log.success('清空表ads_wework_item_ecommerce成功')
        except Exception as e:
            log.error(e)
            self.connect.rollback()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={token}'
        data = {
            "tag_id": [],
            "group_id": []
        }
        resp = self.session.post(url, json=data).json()
        sql = 'select * from `posttag`.`ads_wework_all_lable_d`'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        s = set()
        for item in result:
            s.add(item['lable_name'].split(':')[0].replace("'", ''))
        for item in resp['tag_group']:
            if item['group_name'] in s:
                print(item['group_name'], item['group_id'])
                url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={token}'
                data = {
                    "group_id": [item['group_id']]
                }
                resp = self.session.post(url, json=data).json()
                log.info(resp)


    def add_corp_tag(self):
        '''创建组、标签'''
        sql = 'select * from `posttag`.`ads_wework_all_lable_d`'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        for item in result:
            group_name = item['lable_name'].split(':')[0].replace("'", '')
            tag_name = item['lable_name'].split(':')[1].replace("'", '')

            if tag_name:
                token = self.get_access_token()
                url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?access_token={token}'
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
                    log.success(f'添加标签组【{group_name}】,【{tag_name}】成功')
                    sql = 'insert into `posttag`.`ads_wework_item_ecommerce`(`group_name`,`group_id`,`tag_name`,`tag_id`,`type`) values(%s,%s,%s,%s,%s)'
                    self.cursor.execute(sql, (
                    group_name, resp['tag_group']['group_id'], tag_name, resp['tag_group']['tag'][0]['id'], 1))
                    self.connect.commit()
                else:
                    log.error(f'添加标签组【{group_name}】,【{tag_name}】失败,{result}')


    async def mark_tag(self, client,item, mysqlobj):
        '''打标'''
        token = self.get_access_token()
        tag_list = item['lable_name_list'].replace("{", '').replace("}", '').replace("'", '').strip().split(
            '&')
        new_tag_list = []
        for tag in tag_list:
            group_name = tag.split(':')[0]
            tag_name = tag.split(':')[1]
            sql = 'select * from `posttag`.`ads_wework_item_ecommerce` where `group_name`=%s and `tag_name`=%s'
            item_result = await mysqlobj.async_query(sql, args=(group_name, tag_name))
            if item_result:
                new_tag_list.append(item_result[0]['tag_id'])
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/mark_tag?access_token={token}'
        data = {
            "userid": item['userid'],
            "external_userid": item['unionid'],
            "add_tag": new_tag_list,
        }
        async with client.post(url, json=data) as resp:
            result = await resp.json()
            if result['errcode'] == 0:
                log.success(f'给{item["unionid"]},{item["userid"]}打标成功')
            else:
                log.error(result)
                log.error(f'给{item["unionid"]},{item["userid"]}打标失败')

    async def rate_limited_fetch(self,client,item, mysqlobj,semaphore,limiter):
        async with semaphore: # 控制并发数
            async with limiter:  # 控制每秒请求数
                await self.mark_tag(client,item, mysqlobj)



    async def main(self):
        semaphore = asyncio.Semaphore(REQUESTS_PER_SECOND)   # 并发数
        timeout = aiohttp.ClientTimeout(total=None)
        connector = aiohttp.TCPConnector(verify_ssl=False)
        mysqlobj = await Connection.get_async_pool(loop,self.env)
        limiter = AsyncLimiter(MAX_RATE, TIME_PERIOD)  # 每time_period秒最多max_rate个请求
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as client:
            mark_tag_sql = 'select * from `posttag`.`ads_wework_user_all_lable_list_d`'
            mark_tag_result = await mysqlobj.async_query(mark_tag_sql)
            mark_tag_tasks = [asyncio.ensure_future(self.rate_limited_fetch(client, item, mysqlobj,semaphore,limiter)) for item in mark_tag_result]
            await asyncio.wait(mark_tag_tasks)



    def get_all_tags(self):
        '''查询标签组'''
        token = self.get_access_token()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={token}'
        data = {
            "tag_id": ["etlUx7DQAAWUEc5pYHPj68jq7ZvcSc_w"],
            "group_id": ["etlUx7DQAAmO11fOJIJAOUKqwGFVfa6A"]
        }
        resp = self.session.post(url, json=data).json()
        log.info(resp)

    def manual_del_tag(self):
        '''手动删除标签组'''
        token = self.get_access_token()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={token}'
        data = {
            "group_id": ["etlUx7DQAAYMhYcc14thZo2sLwhgEo-A"]
        }
        resp = self.session.post(url, json=data).json()
        if resp['errcode'] == 0:
            print('删除标签组成功')
        else:
            print('删除标签组失败')

    def manual_tag(self):
        '''手动打标'''
        token = self.get_access_token()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/mark_tag?access_token={token}'
        data = {
            "userid": "WangYi01",
            "external_userid": "wmlUx7DQAAFa4flwdUlXKU6F4cec-N-Q",
            "add_tag": ['etlUx7DQAAWUEc5pYHPj68jq7ZvcSc_w'],
        }
        resp = self.session.post(url, json=data).json()

        if resp['errcode'] == 0:
            log.success(f'给{data["userid"]},{data["external_userid"]}打标成功')
        else:
            log.error(resp)
            log.error(f'给{data["userid"]},{data["external_userid"]}打标失败')


if __name__ == '__main__':
    wx = TagECommerce()
    wx.del_corp_tag()
    wx.add_corp_tag()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wx.main())
    Connection.db_close()

    # wx.get_all_tags()
    # wx.manual_tag()
    # wx.manual_del_tag()
