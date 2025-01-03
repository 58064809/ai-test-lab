# coding=utf-8
# 2024/7/2 下午4:59
from pprint import pprint

from util.log_handle import log
from other_settings import Connection
import pendulum, pathlib, time
import asyncio, aiohttp


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


limiter = RateLimiter(2, 1)


class eCommerce:

    def __init__(self):
        self.corpid = "wwa0a08e1fba1d2db1"
        self.eCommerce_customer_token = "_TfpmSUYgVyQY2NDizxiF5W1Ja0TQSeEaEAFtMu-_jU"
        self.eCommerce_contacts_token = "AQA8gU7EwGAPg9o-Za58FvSc7wyPQOZq6blXbIyBCiQ"
        self.eCommerce_contacts_token_path = pathlib.Path('eCommerce_contacts_token.txt')
        self.eCommerce_customer_token_path = pathlib.Path('eCommerce_customer_token.txt')
        self.session = Connection.get_session()
        self.env = 'local'
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

    def get_access_token(self, business):
        if business == "contacts":
            corpsecret = self.eCommerce_contacts_token
            path = self.eCommerce_contacts_token_path
        else:
            corpsecret = self.eCommerce_customer_token
            path = self.eCommerce_customer_token_path

        with open(path, 'r', encoding='utf-8') as f:
            result = f.read()
            if result:
                access_token_info = result.split(',')
                old_time = pendulum.parser.parse(access_token_info[0])
                expiration_time = access_token_info[1]
                old_token = access_token_info[2]
                if self.date_diff(keywork='secrets', d1=pendulum.now(), d2=old_time) >= int(expiration_time):
                    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={corpsecret}"
                    resp = self.session.get(url).json()
                    if resp['errcode'] == 0:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
                        return resp['access_token']
                    else:
                        log.error('获取access_token失败')
                else:
                    return old_token
            else:
                url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={corpsecret}"
                resp = self.session.get(url).json()
                if resp['errcode'] == 0:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(str(pendulum.now()) + ',' + str(resp['expires_in']) + ',' + resp['access_token'])
                    return resp['access_token']
                else:
                    log.error('获取access_token失败')


    def get_users(self):
        '''获取成员ID列表'''
        token = self.get_access_token('contacts')
        url = f'https://qyapi.weixin.qq.com/cgi-bin/user/list_id?access_token={token}'
        resp = self.session.post(url).json()
        if resp['errcode'] == 0:
            log.success(f"获取成员ID列表成功,共计{len(resp['dept_user'])}条数据")
            try:
                sql = 'truncate table `douyin`.`ads_wework_eCommerce_userid_list`'
                self.cursor.execute(sql)
                self.connect.commit()
                log.success('清空表ads_wework_userid_list成功')
            except Exception as e:
                log.error(e)
                self.connect.rollback()
            r = [item['userid'] for item in resp['dept_user']]
            return [r[i:i + 100] for i in range(0, len(r), 100)]
        raise Exception('获取成员ID列表失败')

    async def insert_userid_list(self, result_list, mysqlobj):
        for item in result_list:
            try:
                sql = "INSERT INTO `douyin`.`ads_wework_eCommerce_userid_list`(unionid,userid,remark,description,createtime,tag_id,remark_mobiles,add_way,oper_userid,external_userid,name,type,avatar,gender,agent) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                if item['follow_info']['tag_id'] == []:
                    item['follow_info']['tag_id'] = None
                else:
                    item['follow_info']['tag_id'] = ','.join(item['follow_info']['tag_id'])
                if item['follow_info']['remark_mobiles'] == []:
                    item['follow_info']['remark_mobiles'] = None
                else:
                    item['follow_info']['remark_mobiles'] = ','.join(
                        item['follow_info']['remark_mobiles'])
                id = await mysqlobj.async_commit_oper(sql, (
                    item['external_contact'].get('unionid',None), item['follow_info']['userid'],
                    item['follow_info']['remark'],
                    item['follow_info']['description'], item['follow_info']['createtime'],
                    item['follow_info']['tag_id'],
                    item['follow_info']['remark_mobiles'], item['follow_info']['add_way'],
                    item['follow_info'].get('oper_userid',None),
                    item['external_contact']['external_userid'], item['external_contact']['name'],
                    item['external_contact']['type'], item['external_contact']['avatar'],
                    item['external_contact']['gender'], 3))
                log.success(f"插入ads_wework_userid_list表成功,【{item['follow_info']['userid']}】,【{item['follow_info']['remark']}】id:{id}")
            except Exception as e:
                log.error(e)

    async def get_by_user(self, client, user_item, mysqlobj):
        '''批量获取客户详情'''
        token = self.get_access_token('customer')
        url = f"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/batch/get_by_user?access_token={token}"
        next = True
        data = {
            "userid_list":
                [user_item],
            "limit": 100,
        }
        while next:
            await limiter.wait_until_allowed()
            async with client.post(url, json=data) as resp:
                result = await resp.json()
            if result['errcode'] == 0 and result['next_cursor']:
                await self.insert_userid_list(result['external_contact_list'], mysqlobj)
                data['cursor'] = result['next_cursor']
            elif result['errcode'] == 0 and result['next_cursor'] == '':
                await self.insert_userid_list(result['external_contact_list'], mysqlobj)
                log.info(f'{user_item}没有next_cursor了')
                next = False
            else:
                log.error(f"批量获取客户详情失败")
                log.error(result)

    async def main(self,total):
        timeout = aiohttp.ClientTimeout(total=None)
        connector = aiohttp.TCPConnector(verify_ssl=False)
        mysqlobj = await Connection.get_async_pool(loop,self.env)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as client:
            for i in total:
                users_tasks = [asyncio.ensure_future(self.get_by_user(client, item, mysqlobj)) for item in
                               i[0:1]]
                await asyncio.wait(users_tasks)

    def manual_get_userid(self):
        '''手动获取客户详情'''
        token = self.get_access_token('customer')
        url = f"https://qyapi.weixin.qq.com/cgi-bin/externalcontact/batch/get_by_user?access_token={token}"
        next = True
        data = {
            "userid_list":
                ["LianLianZhongQingCaoWenQian"],
            "limit": 100,
        }
        while next:
            resp = self.session.post(url, json=data).json()
            print(resp)
            if resp['errcode'] == 0 and resp['next_cursor']:
                data['cursor'] = resp['next_cursor']
            elif resp['errcode'] == 0 and resp['next_cursor'] == '':
                log.info(f'没有next_cursor了')
                next = False
            else:
                log.error(f"批量获取客户详情失败")
                log.error(resp)



if __name__ == '__main__':
    ec = eCommerce()
    total = ec.get_users()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(ec.main(total))
    # 手动用
    # wx.manual_get_userid()

