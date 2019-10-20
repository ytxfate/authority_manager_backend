#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  common_return.py
@Desc :  response 统一返回封装
'''

# The Python Standard Modules(Library) and Third Modules(Library)
from flask import jsonify

# User-defined Modules
from project.common_tools import http_response_code


def common_return(code=http_response_code.SUCCESS, isSuccess=True, msg="请求成功", resp={}):
    """
    接口统一返回模板
        @param:
            code:       http状态码     int      默认 200
            isSuccess:  请求成功状态    bool    默认 True
            msg:        描述            str     默认 请求成功
            resp:       返回的数据结果集  object 默认 {}
        @return:
            return jsonify
    """
    ret_json = {
        "code": code,
        "isSuccess": isSuccess,
        "msg": msg,
        "response": resp
    }
    return jsonify(ret_json)
