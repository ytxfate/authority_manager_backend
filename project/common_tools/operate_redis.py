#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  operate_redis.py
@Desc :  操作 Redis 数据库
'''

# The Python Standard Modules(Library) and Third Modules(Library)
import redis

# User-defined Modules
from global_config import Redis_config, Redis_config_test, isFormalSystem


class OperateRedis:
    """
    操作 Redis 数据库
    """
    def __init__(self):
        # 根据 isFormalSystem 判断连接哪个 redis 数据库
        if isFormalSystem:
            self.Redis_config = Redis_config
        else:
            self.Redis_config = Redis_config_test
    
    def conn_redis(self):
        """
        连接 Redis 数据库
            @return:
                redis_connection
        """
        if self.Redis_config['AUTH'] is True:
            pool = redis.ConnectionPool(
                host=self.Redis_config['HOST'],
                port=self.Redis_config['PORT'],
                password=self.Redis_config['PASSWORD'],
                decode_responses=self.Redis_config['DECODE_RESPONSES']
            )
        else:
            pool = redis.ConnectionPool(
                host=self.Redis_config['HOST'],
                port=self.Redis_config['PORT'],
                decode_responses=self.Redis_config['DECODE_RESPONSES']
            )
        conn = redis.Redis(connection_pool=pool)
        return conn
