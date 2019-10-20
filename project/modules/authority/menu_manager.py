#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  menu_manager.py
@Desc :  菜单管理
'''

# The Python Standard Modules(Library) and Third Modules(Library)
import uuid
import re
# User-defined Modules
from project.common_tools.operate_mongodb import OperateMongodb
from project.common_tools.common_return import common_return
from project.common_tools.check_and_handle_request_param import CheckAndHandleRequestParam
from project.common_tools import http_response_code as H_R_C

class MenuManager:
    def __init__(self, request):
        self.request = request
        self.conn_mongo, self.db_mongo = OperateMongodb().conn_mongodb()

    def get_menus_info(self):
        start = self.request.args.get('start') or 0
        size = self.request.args.get('size') or 10
        req_dict = self.request.json or {}
        _, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            need_regexp_keys=['component', 'name'])
        # 对 meta.title 添加模糊查询
        if 'meta' in req_dict and 'title' in req_dict['meta']:
            req_dict['meta.title'] = re.compile(req_dict['meta']['title'])
            del req_dict['meta']
        ret_dict = {'total': 0, 'data': []}
        rows = self.db_mongo.get_collection('menus_info').find(req_dict)
        ret_dict['total'] = rows.count()
        rows = rows.skip(int(start)).limit(int(size))
        for row in rows:
            row['obj_id'] = str(row['_id'])
            del row['_id']
            ret_dict['data'].append(row)
        return common_return(resp=ret_dict)
    
    def add_menu(self):
        """
        新增菜单
        """
        req_dict = self.request.json
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['path', 'name', 'depth', 'component', 'hidden']
        )
        if check_status:
            req_dict['menu_id'] = str(uuid.uuid1())
            if 'parent_name' in req_dict:
                req_dict['parent_id'] = req_dict['parent_name']
                parent_row = self.db_mongo.get_collection('menus_info').find_one({'menu_id': req_dict['parent_id']}, {'name': 1})
                if parent_row:
                    req_dict['parent_name'] = parent_row['name']
                else:
                    return common_return(code=H_R_C.DATA_CHECK_ERROR, isSuccess=False, msg="父级菜单不存在")
            self.db_mongo.get_collection('menus_info').insert(req_dict)
            return common_return(msg="新增菜单成功")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数异常")

    def get_depth_menus(self):
        ret_list = []
        depth = self.request.args.get('depth')
        if depth:
            rows = self.db_mongo.get_collection('menus_info').find(
                {'depth': int(depth) - 1}, {'_id': 0, 'menu_id': 1, 'name': 1})
            ret_list = list(rows)
            return common_return(resp=ret_list)
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数异常")

    def delete_menu(self):
        menu_id = self.request.args.get('menu_id')
        if menu_id:
            self.db_mongo.get_collection('menus_info').delete_one({'menu_id': menu_id})
            return common_return(msg="菜单删除成功")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数异常")
    
    def edit_menu(self):
        """
        修改菜单
        """
        req_dict = self.request.json
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['path', 'name', 'depth', 'component', 'hidden', 'menu_id']
        )
        if check_status:
            if 'parent_name' in req_dict and req_dict['parent_name']:
                req_dict['parent_id'] = req_dict['parent_name']
                parent_row = self.db_mongo.get_collection('menus_info').find_one({'menu_id': req_dict['parent_id']}, {'name': 1})
                if parent_row:
                    req_dict['parent_name'] = parent_row['name']
                else:
                    return common_return(code=H_R_C.DATA_CHECK_ERROR, isSuccess=False, msg="父级菜单不存在")
            if req_dict['depth'] == 1:
                req_dict['parent_id'] = None
                req_dict['parent_name'] = None
            self.db_mongo.get_collection('menus_info').update_one(
                {'menu_id': req_dict['menu_id']},
                {'$set': req_dict}
            )
            return common_return(msg="修改菜单成功")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg="请求参数异常")
