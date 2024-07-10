# coding = utf-8
import pymysql
import requests
from requests import adapters
from pymysql.cursors import SSDictCursor
from config.read_config import ReadConfig
from dbutils.pooled_db import PooledDB


class Connection:
    session = None
    conf = None
    business_db = None

    def __init__(self):
        pass

    @classmethod
    def get_session(cls):
        if cls.session is None:
            requests.adapters.DEFAULT_RETRIES = 100  # 增加重连次数
            cls.session = requests.session()
            cls.session.keep_alive = False  # 关闭多余连接
        return cls.session


    @classmethod
    def get_db_connect(cls):
        if cls.conf is None:
            cls.conf = ReadConfig()
            cls.version = cls.conf.get_config_value('version', 'version')
            cls.pool = PooledDB(
                creator=pymysql,
                maxconnections=10,   # 连接池允许的最大连接数,0和None表示没有限制
                mincached=3,    # 初始化时,连接池至少创建的空闲连接,0表示不创建
                blocking=True,  # False表示不等待然后报错
                host=cls.conf.get_config_value('database', 'ip'),
                user=cls.conf.get_config_value('database', 'user'),
                password=cls.conf.get_config_value('database', 'pwd'),
                db=cls.conf.get_config_value('database', 'dbname'),
                charset=cls.conf.get_config_value('database', 'charset'),
            )
            cls.conn = cls.pool.connection()
            cls.cursor = cls.conn.cursor(SSDictCursor)
        return cls.conn,cls.cursor,cls.version


    @classmethod
    def get_more_db_connect(cls):
        if cls.business_db is None:
            cls.conf = ReadConfig()
            cls.bus_pool = PooledDB(
                creator=pymysql,
                maxconnections=10,  # 连接池允许的最大连接数,0和None表示没有限制
                mincached=3,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                blocking=True,  # False表示不等待然后报错
                host=cls.conf.get_config_value('business_database', 'ip'),
                port=int(cls.conf.get_config_value('business_database', 'port')),
                user=cls.conf.get_config_value('business_database', 'user'),
                password=cls.conf.get_config_value('business_database', 'pwd'),
                database=cls.conf.get_config_value('business_database', 'dbname'),
                charset=cls.conf.get_config_value('business_database', 'charset')
                )
            cls.bus_conn = cls.bus_pool.connection()
            cls.bus_cursor = cls.bus_conn.cursor(SSDictCursor)
        return cls.bus_conn,cls.bus_cursor


    @classmethod
    def close_session(cls):
        cls.session.close()

    @classmethod
    def close_more_db(cls):
        con,cur = cls.get_more_db_connect()
        cur.close()
        con.close()











