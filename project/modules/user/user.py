#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  user.py
@Desc :  用户管理模块
'''

# The Python Standard Modules(Library) and Third Modules(Library)
from flask import jsonify, Response, make_response, g
import json
import copy
import pprint
# User-defined Modules
from project.common_tools.jwt_auth import JWTAuth
from project.common_tools.common_return import common_return
from project.common_tools import http_response_code as H_R_C
from project.common_tools.check_and_handle_request_param import CheckAndHandleRequestParam
from project.common_tools.operate_mongodb import OperateMongodb

class UserModul:
    """
    用户模块
    """
    def __init__(self, request):
        self.request = request
        self.conn_mongo, self.db_mongo = OperateMongodb().conn_mongodb()

    def login(self):
        """
        登录
        """
        req_dict = copy.deepcopy(self.request.json)
        must_need_keys = ['username', 'password']
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            remove_spaces=True, must_need_keys=must_need_keys,
            can_change_keys=[], need_regexp_keys=[]
        )   # 默认值相同字段可省略
        if check_status:
            row = self.db_mongo.get_collection('users').find_one(req_dict)
            if row:
                user_info = {'username': req_dict['username'], 'user_id': row['user_id']}
                create_status, jwt_str, refresh_jwt_str = JWTAuth().create_jwt_and_refresh_jwt(user_info)
                if create_status:
                    return common_return(resp={'jwt': jwt_str, 'refresh_jwt': refresh_jwt_str})
                else:
                    return common_return(code=H_R_C.JWT_CREATE_ERROR, isSuccess=False, msg="JWT 信息生成异常")
            else:
                return common_return(code=H_R_C.DATA_CHECK_ERROR, isSuccess=False, msg="用户名或密码错误")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数错误")
    
    def refresh_login_status(self):
        """
        刷新登录状态
        """
        req_dict = copy.deepcopy(self.request.json)
        must_need_keys = ['refresh_jwt']
        jwt_str = self.request.headers.get('Authorization')
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=must_need_keys
        )
        if check_status and jwt_str:
            decode_status, _ = JWTAuth().decode_jwt(req_dict['refresh_jwt'])
            user_info = JWTAuth().decode_jwt_without_check(jwt_str)
            if decode_status:
                create_status, jwt_str, refresh_jwt_str = JWTAuth().create_jwt_and_refresh_jwt(user_info)
                if create_status:
                    return common_return(resp={'jwt': jwt_str, 'refresh_jwt': refresh_jwt_str})
                else:
                    return common_return(code=H_R_C.JWT_CREATE_ERROR, isSuccess=False, msg="JWT 信息生成异常")
            else:
                # 跳转到登录界面 ???
                return common_return(code=H_R_C.USER_NO_LOGIN, isSuccess=False, msg="刷新 jwt 失败，重新登录")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数错误")
    
    def logout(self):
        """
        登出
        """
        # jwt 做 用户认证 时，不存在可以注销的说法
        return common_return(msg="用户登出")

    def get_user_info(self):
        """
        获取用户信息
        """
        ret_dict = {'user_info': {}, 'role_ids': []}
        role_ids = set()
        ret_dict['user_info'] = self.db_mongo.get_collection('users').find_one(g.user_info, {'_id': 0})
        rows = self.db_mongo.get_collection('user_roles').find({'user_id': g.user_info['user_id']}, {'_id': 0, 'role_ids': 1})
        for row in rows:
            if 'role_ids' in row:
                role_ids.update(row['role_ids'])
        ret_dict['role_ids'] = list(role_ids)
        return common_return(resp=ret_dict)

    def get_user_routers(self):
        req_dict = self.request.json
        must_need_keys = ['role_ids']
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=must_need_keys
        )
        if check_status:
            # 获取全部的 role 角色对应的 menu_id
            role_rows = self.db_mongo.get_collection('roles_info').find({'role_id': {'$in': req_dict['role_ids']}})
            menu_ids = set()
            for role in role_rows:
                if 'menu_ids' in role and role['menu_ids']:
                    menu_ids.update(set(role['menu_ids']))
            # 获取符合条件的菜单的级别的数组
            depth_num_rows = list(self.db_mongo.get_collection('menus_info').aggregate([
                {'$match': {'menu_id':{'$in': list(menu_ids)}}},
                {'$group': {'_id': '$depth'}}
            ]))
            depth_nums = set()
            for depth_num_row in depth_num_rows:
                if depth_num_row['_id']:
                    depth_nums.add(depth_num_row['_id'])
            if len(depth_nums) <= 0:
                return common_return(resp=[])
            # 获取最大的菜单级别，以此确认需要循环几次来组装菜单路由
            max_depth = max(depth_nums)
            temp_dict_menu_up = {}
            temp_dict_menu_down = {}
            routers = []
            # 循环按菜单级别，反向查询，组装菜单
            for depth_index in range(max_depth):
                menu_rows = self.db_mongo.get_collection('menus_info').find(
                    {'menu_id': {'$in': list(menu_ids)},'depth': (max_depth - depth_index)}, {'_id': 0}).sort('order', 1)
                for menu_row in menu_rows:
                    # 当菜单级别不是最底层的子菜单时，将其对应的子菜单存到当前菜单的 children 中
                    if menu_row['menu_id'] in temp_dict_menu_down:
                        menu_row['children'] = temp_dict_menu_down[menu_row['menu_id']]
                    # 当菜单的 parent_id 为 None 时，此菜单为一级菜单，可直接将此菜单 append 到最终的菜单路由中
                    if menu_row['parent_id'] is None:
                        routers.append(menu_row)
                    else:
                        # 按菜单的 parent_id 进行分组
                        if menu_row['parent_id'] in temp_dict_menu_up:
                            temp_dict_menu_up[menu_row['parent_id']].append(menu_row)
                        else:
                            temp_dict_menu_up[menu_row['parent_id']] = [menu_row]
                temp_dict_menu_down, temp_dict_menu_up = temp_dict_menu_up, {}
            return common_return(resp=routers)
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数错误")
