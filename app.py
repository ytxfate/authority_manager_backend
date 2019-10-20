#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  app.py
@Desc :  项目基本配置模块
'''

# The Python Standard Modules(Library) and Third Modules(Library)
from flask import Flask, request
import flask_cors
from werkzeug.exceptions import HTTPException
from logging.config import dictConfig
from flask import g

# User-defined Modules
from project.common_tools import http_response_code
from project.common_tools.common_return import common_return
import global_config
from project.common_tools.jwt_auth import JWTAuth

# 日志配置
dictConfig({
    'version': 1,
    'formatters': {'default': {
        # 'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
# 密钥
app.secret_key = global_config.SECRET_KEY
# 跨域解决方案
flask_cors.CORS(app, supports_credentials=True)

# 注册蓝图
root_url = '/api'   # 当服务器使用 nginx 做反向代理的时候
                    # 可修改 root_url 已便 nginx 拦截请求
                    # 若不需要可以设置为空
from project.blueprint_manager.user_blueprint_manager import user
from project.blueprint_manager.authority_blueprint_manager import authority
BLUEPRINT_LIST = [
    {"blueprint": user, "url_prefix": root_url + "/user"},
    {"blueprint": authority, "url_prefix": root_url + "/authority"},
]
for bp in BLUEPRINT_LIST:
    app.register_blueprint(bp['blueprint'], url_prefix=bp['url_prefix'])


# 拦截器(用于用户身份认证等...)
@app.before_request
def app_before_request():
    # 按要求拦截请求
    req_path = request.path
    if ('user/refresh_login_status' in req_path):
        jwt_str = request.headers.get('Authorization')
        if not jwt_str:
            return common_return(code=http_response_code.USER_NO_LOGIN, isSuccess=False, msg="请求异常")
    elif any([
        ('user/logout' in req_path),
        ('user/get_user_info' in req_path),
        ('authority' in req_path),
    ]):
        # 拦截器进行用户认证，认证完成后将相关数据放到 flask 当前应用环境的通用变量 g 中，
        # 后续模块可以通过 g 对象来获取设置在其中的数据，
        # 当数据不存在时出现 '_AppCtxGlobals' object has no attribute 'xxx' 异常
        jwt_str = request.headers.get('Authorization')
        decode_status, user_info = JWTAuth().decode_jwt(jwt_str)
        g.user_info = None
        if decode_status:
            g.user_info = user_info
            # print(g.user_info)
        else:
            # 跳转到登录页面
            return common_return(code=http_response_code.JWT_PARSE_ERROR, isSuccess=False, msg="JWT 解析失败")
    

# 全局异常处理
@app.errorhandler(Exception)
def global_exception_handler(exp):
    # 获取请求中的参数，以判断哪个链接的哪个位置有 bug
    try:
        req_args = request.args.to_dict()
    except Exception as e:
        req_args = {"ERROR": str(e)}
    try:
        req_form = request.form.to_dict()
    except Exception as e:
        req_form = {"ERROR": str(e)}
    try:
        req_json = request.json
    except Exception as e:
        req_json = {"ERROR": str(e)}
    try:
        req_data = "having data" if bool(request.get_data()) else "not any data"
    except Exception as e:
        req_data = {"ERROR": str(e)}
    # 记录异常信息
    app.logger.error("Exception => " + str(exp) +
                     "\n****** REQUEST DETAIL ******" +
                     "\nurl:  " + request.base_url +
                     "\nargs: " + str(req_args) +
                     "\nform: " + str(req_form) +
                     "\njson: " + str(req_json) +
                     "\ndata: " + str(req_data) +
                     "\n****************************"
                     )
    if isinstance(exp, HTTPException):
        return common_return(code=http_response_code.EXCEPTION_ERROR, isSuccess=False, msg="HTTP Exception")
    else:
        # 若果不是 HTTPException 异常，则记录具体的异常信息
        app.logger.exception(exp)
        return common_return(code=http_response_code.EXCEPTION_ERROR, isSuccess=False, msg="Exception")
