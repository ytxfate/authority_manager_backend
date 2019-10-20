#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  global_config.py
@Desc :  项目配置信息模块
'''

# The Python Standard Modules(Library) and Third Modules(Library)

# User-defined Modules


# ********** 运行配置 ********** #
# 基本运行配置
app_run_config = {
    "HOST": "127.0.0.1",
    "PORT": 5000,
    "DEBUG": True
}
# 密钥
SECRET_KEY = "123"

# ********** 生产 与 测试 系统切换 ********** #
# True : 生产系统
# False: 测试系统
isFormalSystem = False

# ********** 数据库配置 ********** #
# redis 数据库
Redis_config = {    # 生产系统使用
    "HOST": "127.0.0.1",
    "PORT": 6379,
    "AUTH": False,      # AUTH 为 True 时需要进行 用户认证
    "PASSWORD": "",
    "DECODE_RESPONSES": True    # 是否对查询结果进行编码处理
}
Redis_config_test = {   # 测试系统使用
    "HOST": "127.0.0.1",
    "PORT": 6379,
    "AUTH": False,      # AUTH 为 True 时需要进行 用户认证
    "PASSWORD": "",
    "DECODE_RESPONSES": True    # 是否对查询结果进行编码处理
}

# mongodb 数据库
MongoDB_config = {  # 生产系统使用
    "URL": "127.0.0.1:27017",   # 有此项则优先用此项进行数据库连接，否则用 HOST 和 PORT 连接
    "HOST": "127.0.0.1",
    "PORT": 27017,
    "AUTH": False,      # AUTH 为 True 时需要进行 用户认证
    "USERNAME": "",
    "PASSWORD": "",
    "DEFAULT_DB": "test"    # 默认数据库
}
MongoDB_config_test = { # 测试系统使用
    "URL": "127.0.0.1:27017",   # 有此项则优先用此项进行数据库连接，否则用 HOST 和 PORT 连接
    "HOST": "127.0.0.1",
    "PORT": 27017,
    "AUTH": True,      # AUTH 为 True 时需要进行 用户认证
    "USERNAME": "test",
    "PASSWORD": "test",
    "DEFAULT_DB": "test"    # 默认数据库
}
