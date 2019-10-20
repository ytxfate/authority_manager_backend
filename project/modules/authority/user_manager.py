#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  user_manager.py
@Desc :  用户管理
'''

# The Python Standard Modules(Library) and Third Modules(Library)
import uuid
# User-defined Modules
from project.common_tools.operate_mongodb import OperateMongodb
from project.common_tools.common_return import common_return
from project.common_tools.check_and_handle_request_param import CheckAndHandleRequestParam
from project.common_tools import http_response_code as H_R_C

class UserManager:
    def __init__(self, request):
        self.request = request
        self.conn_mongo, self.db_mongo = OperateMongodb().conn_mongodb()
    
    def get_users_info(self):
        start = self.request.args.get('start') or 0
        size = self.request.args.get('size') or 10
        req_dict = self.request.json or {}
        _, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            need_regexp_keys=['username'])
        ret_dict = {'total': 0, 'data': []}
        rows = self.db_mongo.get_collection('users').find(req_dict)
        ret_dict['total'] = rows.count()
        rows = rows.skip(int(start)).limit(int(size))
        for row in rows:
            row['obj_id'] = str(row['_id'])
            del row['_id']
            ret_dict['data'].append(row)
        return common_return(resp=ret_dict)
    
    def delete_user(self):
        user_id = self.request.args.get('user_id')
        if user_id:
            self.db_mongo.get_collection('users').delete_one({'user_id': user_id})
            return common_return(msg='用户删除成功')
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')

    def get_all_roles(self):
        rows = self.db_mongo.get_collection('roles_info').find({}, {'_id': 0, 'role_id': 1, 'name': 1})
        return common_return(resp=list(rows))

    def get_user_roles(self):
        ret_list = set()
        user_id = self.request.args.get('user_id')
        rows = self.db_mongo.get_collection('user_roles').find({'user_id': user_id}, {'_id': 0, 'role_ids': 1})
        for row in rows:
            if row and 'role_ids' in row:
                ret_list.update(set(row['role_ids']))
        return common_return(resp=list(ret_list))
    
    def user_relate_roles(self):
        req_dict = self.request.json or {}
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['user_id', 'role_ids']
        )
        if check_status:
            if self.db_mongo.get_collection('user_roles').find_one({'user_id': req_dict['user_id']}):
                self.db_mongo.get_collection('user_roles').update_one(
                    {'user_id': req_dict['user_id']},
                    {'$set': {'role_ids': req_dict['role_ids']}}
                )
            else:
                self.db_mongo.get_collection('user_roles').insert_one({
                    'user_id': req_dict['user_id'],
                    'role_ids': req_dict['role_ids']
                })
            return common_return(msg='用户关联角色成功')
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')
