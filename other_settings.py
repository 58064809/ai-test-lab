# coding=utf-8
# 2024/8/30 11:04

from dbutils.pooled_db import PooledDB
from pymysql.cursors import SSDictCursor
from requests import adapters
from enum import Enum
import requests, pymysql
import aiomysql


class Environment(Enum):
    LOCAL = "local"
    SERVER = "server"
    SHENJI = "shenji"

class Connection:
    _db = None
    _conn = None
    _cursor = None
    _async_db = None
    session = None


    @classmethod
    def get_session(cls):
        if cls.session is None:
            requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
            cls.session = requests.session()
            cls.session.keep_alive = False  # 关闭多余连接
        return cls.session

    @classmethod
    def get_db_connect(cls, env):
        if cls._db is None:
            try:
                if env == Environment.LOCAL.value:
                    __pool = PooledDB(
                        creator=pymysql,
                        mincached=10,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                        blocking=True,  # False表示不等待然后报错
                        host="10.10.100.195",
                        port=3306,
                        user="root",
                        password="123456",
                        database="douyin",
                    )
                elif env == Environment.SERVER.value:
                    __pool = PooledDB(
                        creator=pymysql,
                        mincached=10,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                        blocking=True,  # False表示不等待然后报错
                        host="pc-2zefs39o1el89k1jn.rwlb.rds.aliyuncs.com",
                        port=3306,
                        user="ll_db_tag",
                        password="GE4FGaZWDKY2kL",
                        database="posttag",
                    )
                elif env == Environment.SHENJI.value:
                    __pool = PooledDB(
                        creator=pymysql,
                        mincached=10,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                        blocking=True,  # False表示不等待然后报错
                        host="39.105.171.113",
                        port=3306,
                        user="cdao",
                        password="d4RMQ67yLV*Y",
                        database="zentao",
                    )
                else:
                    raise Exception("环境变量错误")
                cls._conn = __pool.connection()
                cls._cursor = cls._conn.cursor(SSDictCursor)
                cls._db = True
            except Exception as e:
                raise Exception(f"Error connecting to the database: {e}")
        return cls._conn, cls._cursor

    @classmethod
    def db_close(cls):
        if cls._cursor and cls._conn:
            try:
                cls._cursor.close()
                cls._conn.close()
            except Exception as e:
                raise Exception(f"Error closing to the database: {e}")
            finally:
                cls._cursor = None
                cls._conn = None
                cls._db = None

    @classmethod
    async def init_pool(cls, loop, env):
        if cls._async_db is None:
            try:
                if env == Environment.LOCAL.value:
                    __pool = await aiomysql.create_pool(
                        maxsize=10,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                        host="10.10.100.195",
                        port=3306,
                        user="root",
                        password="123456",
                        db="douyin",
                        autocommit=True,
                        loop=loop
                    )
                elif env == env == Environment.SERVER.value:
                    __pool = await aiomysql.create_pool(
                        maxsize=10,  # 初始化时,连接池至少创建的空闲连接,0表示不创建
                        host="pc-2zefs39o1el89k1jn.rwlb.rds.aliyuncs.com",
                        port=3306,
                        user="ll_db_tag",
                        password="GE4FGaZWDKY2kL",
                        db="posttag",
                        autocommit=True,
                        loop=loop
                    )
                else:
                    raise ValueError("环境变量错误，请指定'local'或'server'")
                cls._async_db = True
                cls._pool = __pool
            except Exception as e:
                raise Exception(f"Error connecting to the database: {e}")
        return cls._pool

    @classmethod
    async def get_async_pool(cls, loop,env):
        cls.async_pool = await cls.init_pool(loop,env)
        return cls

    @classmethod
    async def async_query(cls, sql, args=None):
        try:
            async with cls.async_pool.acquire() as conn:
                async with conn.cursor(aiomysql.SSDictCursor) as cur:
                    await cur.execute(sql, args=args)
                    return await cur.fetchall()
        except Exception as e:
            raise e

    @classmethod
    async def async_commit_oper(cls, sql, args=None):
        try:
            async with cls.async_pool.acquire() as conn:
                async with conn.cursor(aiomysql.SSDictCursor) as cur:
                    await cur.execute(sql, args=args)
                    await conn.commit()
                    last_id = cur.lastrowid
                    return last_id
        except Exception as e:
            raise e
    @classmethod
    async def close_async_pool(cls):
        if cls._async_db and cls.async_pool:
            cls.async_pool.close()
            await cls.async_pool.wait_closed()
            cls._async_db = None
            cls.async_pool = None