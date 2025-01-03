# # coding=utf-8
# # 2024/7/2 下午4:59
#
#
# from util.log_handle import log
# from other_settings import Connection
# import  pendulum, pathlib,time
# import asyncio, aiohttp,uvloop
#
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
#
# queue = asyncio.Queue()
#
#
# class RateLimiter:
#     def __init__(self, max_calls, period):
#         self.max_calls = max_calls
#         self.period = period
#         self.calls = []
#
#     def is_allowed(self):
#         current_time = time.time()
#         self.calls = [call for call in self.calls if call > current_time - self.period]
#         if len(self.calls) < self.max_calls:
#             self.calls.append(current_time)
#             return True
#         return False
#
#     async def wait_until_allowed(self):
#         while not self.is_allowed():
#             await asyncio.sleep(1)
#
#
# limiter = RateLimiter(10, 5)
#
#
# class WeiXin:
#
#     def __init__(self):
#         self.corpid = "ww2c0040069d754cc0"
#         self.corpsecret = "u2tn3-Klcezmkuyxud5zA9YzDuBxsg-cDt9qCKYKIkg"
#         self.path = pathlib.Path('tag_token.txt')
#         self.session = Connection.get_session()
#         self.env = 'server'
#         self.connect, self.cursor = Connection.get_db_connect(self.env)
#
#     def date_diff(self, keywork='seconds', d1=pendulum.now(), d2=pendulum.now()):
#         '''两个时间直接的运算'''
#         if keywork == 'years':
#             return d1.diff(d2).in_years()
#         elif keywork == 'months':
#             return d1.diff(d2).in_months()
#         elif keywork == 'days':
#             return d1.diff(d2).in_days()
#         elif keywork == 'hours':
#             return d1.diff(d2).in_hours()
#         elif keywork == 'minutes':
#             return d1.diff(d2).in_minutes()
#         else:
#             return d1.diff(d2).in_seconds()
#
#     def get_access_token(self):
#         with open(self.path, 'r', encoding='utf-8') as f:
#             result = f.read()
#             if result:
#                 access_token_info = f.read().split(',')
#                 old_time = pendulum.parser.parse(access_token_info[0])
#                 expiration_time = access_token_info[1]
#                 old_token = access_token_info[2]
#                 if self.date_diff(keywork='secrets', d1=pendulum.now(), d2=old_time) >= int(expiration_time):
#                     url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
#                     resp = self.session.get(url).json()
#                     if resp['errcode'] == 0:
#                         with open(self.path, 'w', encoding='utf-8') as f:
#                             f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
#                         return resp['access_token']
#                     else:
#                         print('获取access_token失败')
#                 else:
#                     return old_token
#             else:
#                 url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
#                 resp = self.session.get(url).json()
#                 if resp['errcode'] == 0:
#                     with open(self.path, 'w', encoding='utf-8') as f:
#                         f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
#                     return resp['access_token']
#                 else:
#                     log.error('获取access_token失败')
#
#     def del_corp_tag(self):
#         '''删除标签组'''
#         token = self.get_access_token()
#         try:
#             sql = 'truncate table `posttag`.`ads_wework_item`'
#             self.cursor.execute(sql)
#             self.connect.commit()
#             log.success('清空表ads_wework_item成功')
#         except Exception as e:
#             log.error(e)
#             self.connect.rollback()
#         url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={token}'
#         data = {
#             "tag_id": [],
#             "group_id": []
#         }
#         resp = self.session.post(url, json=data).json()
#         # print(resp)
#         sql = 'select * from `posttag`.`ads_wework_lable_d`'
#         self.cursor.execute(sql)
#         result = self.cursor.fetchall()
#         s = set()
#         for item in result:
#             s.add(item['lable_name'].split(':')[0].replace("'", ''))
#         for item in resp['tag_group']:
#             if item['group_name'] in s:
#                 print(item['group_name'], item['group_id'])
#                 url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={token}'
#                 data = {
#                     "group_id": [item['group_id']]
#                 }
#                 resp = self.session.post(url, json=data).json()
#                 log.info(resp)
#
#     async def add_corp_tag(self, client, item, mysqlobj):
#         '''创建组、标签'''
#         group_name = item['lable_name'].split(':')[0].replace("'", '')
#         tag_name = item['lable_name'].split(':')[1].replace("'", '')
#
#         if tag_name:
#             token = self.get_access_token()
#             url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_corp_tag?access_token={token}'
#             data = {
#                 "group_name": group_name,
#                 "tag": [
#                     {
#                         "name": tag_name
#                     }
#                 ]
#             }
#             async with client.post(url, json=data) as resp:
#                 result = await resp.json()
#
#             if result['errcode'] == 0:
#                 log.success(f'添加标签组【{group_name}】,【{tag_name}】成功')
#                 sql = 'insert into `posttag`.`ads_wework_item`(`group_name`,`group_id`,`tag_name`,`tag_id`) values(%s,%s,%s,%s)'
#                 await mysqlobj.async_commit_oper(sql, (group_name, resp['tag_group']['group_id'], tag_name, resp['tag_group']['tag'][0]['id']))
#             else:
#                 log.error(f'添加标签组【{group_name}】,【{tag_name}】失败,{resp}')
#
#
#     async def mark_tag(self, client, mysqlobj):
#         '''打标'''
#
#         while not queue.empty():  # 判断队列的元素是否为空
#             await limiter.wait_until_allowed()
#             try:
#                 item = queue.get_nowait()  # 获取元素
#                 token = self.get_access_token()
#                 tag_list = item['lable_name_list'].replace("{", '').replace("}", '').replace("'", '').strip().split(
#                     '&')
#                 new_tag_list = []
#                 for tag in tag_list:
#                     group_name = tag.split(':')[0]
#                     tag_name = tag.split(':')[1]
#                     sql = 'select * from `posttag`.`ads_wework_item` where `group_name`=%s and `tag_name`=%s'
#                     item_result = await mysqlobj.async_query(sql, args=(group_name, tag_name))
#                     if item_result:
#                         new_tag_list.append(item_result[0]['tag_id'])
#                 url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/mark_tag?access_token={token}'
#                 data = {
#                     "userid": item['userid'],
#                     "external_userid": item['unionid'],
#                     "add_tag": new_tag_list,
#                 }
#                 async with client.post(url, json=data) as resp:
#                     result = await resp.json()
#                     if result['errcode'] == 0:
#                         log.success(f'给{item["unionid"]},{item["userid"]}打标成功')
#                     else:
#                         log.error(result)
#                         log.error(f'给{item["unionid"]},{item["userid"]}打标失败')
#                 await asyncio.sleep(5)
#
#                 queue.task_done()  # 告诉队列该任务处理完。
#             except asyncio.CancelledError:
#                 print('队列异常')
#
#     async def main(self):
#         timeout = aiohttp.ClientTimeout(total=None)
#         connector = aiohttp.TCPConnector(verify_ssl=False)
#         mysqlobj = await Connection.get_async_pool(loop,self.env)
#         async with aiohttp.ClientSession(connector=connector, timeout=timeout) as client:
#             add_tag_sql = 'select * from `posttag`.`ads_wework_lable_d`'
#             add_tag_result = await mysqlobj.async_query(add_tag_sql)
#             add_tag_tasks = [asyncio.ensure_future(self.add_corp_tag(client, item, mysqlobj)) for item in
#                              add_tag_result]
#             await asyncio.wait(add_tag_tasks)
#             mark_tag_sql = 'select * from `posttag`.`ads_wework_user_lable_d`'
#             mark_tag_result = await mysqlobj.async_query(mark_tag_sql)
#             [queue.put_nowait(item) for item in mark_tag_result]
#             await asyncio.ensure_future(self.mark_tag(client, mysqlobj))
#
#     def get_all_tags(self):
#         '''查询标签组'''
#         token = self.get_access_token()
#         url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={token}'
#         data = {
#             "tag_id": ["etlUx7DQAAWUEc5pYHPj68jq7ZvcSc_w"],
#             "group_id": ["etlUx7DQAAmO11fOJIJAOUKqwGFVfa6A"]
#         }
#         resp = self.session.post(url, json=data).json()
#         log.info(resp)
#
#     def manual_del_tag(self):
#         '''手动删除标签组'''
#         token = self.get_access_token()
#         url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/del_corp_tag?access_token={token}'
#         data = {
#             "group_id": ["etlUx7DQAAYMhYcc14thZo2sLwhgEo-A"]
#         }
#         resp = self.session.post(url, json=data).json()
#         if resp['errcode'] == 0:
#             print('删除标签组成功')
#         else:
#             print('删除标签组失败')
#
#     def manual_tag(self):
#         '''手动打标'''
#         token = self.get_access_token()
#         url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/mark_tag?access_token={token}'
#         data = {
#             "userid": "WangYi01",
#             "external_userid": "wmlUx7DQAAFa4flwdUlXKU6F4cec-N-Q",
#             "add_tag": ['etlUx7DQAAWUEc5pYHPj68jq7ZvcSc_w'],
#         }
#         resp = self.session.post(url, json=data).json()
#
#         if resp['errcode'] == 0:
#             log.success(f'给{data["userid"]},{data["external_userid"]}打标成功')
#         else:
#             log.error(resp)
#             log.error(f'给{data["userid"]},{data["external_userid"]}打标失败')
#
#
# if __name__ == '__main__':
#     wx = WeiXin()
#     # wx.del_corp_tag()
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(wx.main())
#     Connection.db_close()
#
#     # wx.get_all_tags()
#     # wx.manual_tag()
#     # wx.manual_del_tag()



# coding=utf-8
# 2024/7/2 下午4:59


from util.log_handle import log
from other_settings import Connection
from aiolimiter import AsyncLimiter
import  pendulum, pathlib,time
import asyncio, aiohttp,uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

REQUESTS_PER_SECOND = 5
TIME_PERIOD = 1
MAX_RATE = 5

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def is_allowed(self):
        current_time = time.time()
        self.calls = [call for call in self.calls if call > current_time - self.period]
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        return False

    async def wait_until_allowed(self):
        while not self.is_allowed():
            await asyncio.sleep(1)


limiter = RateLimiter(10, 5)


class WeiXin:

    def __init__(self):
        self.corpid = "ww2c0040069d754cc0"
        self.corpsecret = "u2tn3-Klcezmkuyxud5zA9YzDuBxsg-cDt9qCKYKIkg"
        self.path = pathlib.Path('tag_token.txt')
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
                access_token_info = result.strip().split(',')
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
            sql = 'truncate table `posttag`.`ads_wework_item`'
            self.cursor.execute(sql)
            self.connect.commit()
            log.success('清空表ads_wework_item成功')
        except Exception as e:
            log.error(e)
            self.connect.rollback()
        url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_corp_tag_list?access_token={token}'
        data = {
            "tag_id": [],
            "group_id": []
        }
        resp = self.session.post(url, json=data).json()
        # print(resp)
        sql = 'select * from `posttag`.`ads_wework_lable_d`'
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
        sql = 'select * from `posttag`.`ads_wework_lable_d`'
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
                    sql = 'insert into `posttag`.`ads_wework_item`(`group_name`,`group_id`,`tag_name`,`tag_id`) values(%s,%s,%s,%s)'
                    self.cursor.execute(sql, (
                    group_name, resp['tag_group']['group_id'], tag_name, resp['tag_group']['tag'][0]['id']))
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
            sql = 'select * from `posttag`.`ads_wework_item` where `group_name`=%s and `tag_name`=%s'
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
        batch_size = 1000
        mark_tag_sql = 'select * from `posttag`.`ads_wework_user_lable_d`'
        mark_tag_result = await mysqlobj.async_query(mark_tag_sql)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as client:
            for i in range(0, len(mark_tag_result), batch_size):
                batch = mark_tag_result[i:i + batch_size]
                mark_tag_tasks = [asyncio.ensure_future(self.rate_limited_fetch(client, item, mysqlobj,semaphore,limiter)) for item in batch]
                await asyncio.wait(mark_tag_tasks)
                log.info(f"Batch {i // batch_size + 1} processed.")


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
    wx = WeiXin()
    #wx.del_corp_tag()
    #wx.add_corp_tag()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wx.main())
    Connection.db_close()

    # wx.get_all_tags()
    # wx.manual_tag()
    # wx.manual_del_tag()
