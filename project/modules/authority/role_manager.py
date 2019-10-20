#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  role_manager.py
@Desc :  角色管理
'''

# The Python Standard Modules(Library) and Third Modules(Library)
import uuid
# User-defined Modules
from project.common_tools.operate_mongodb import OperateMongodb
from project.common_tools.common_return import common_return
from project.common_tools.check_and_handle_request_param import CheckAndHandleRequestParam
from project.common_tools import http_response_code as H_R_C

class RoleManager:
    def __init__(self, request):
        self.request = request
        self.conn_mongo, self.db_mongo = OperateMongodb().conn_mongodb()
    
    def get_roles_info(self):
        start = self.request.args.get('start') or 0
        size = self.request.args.get('size') or 10
        req_dict = self.request.json or {}
        _, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            need_regexp_keys=['name', 'desc'])
        ret_dict = {'total': 0, 'data': []}
        rows = self.db_mongo.get_collection('roles_info').find(req_dict)
        ret_dict['total'] = rows.count()
        rows = rows.skip(int(start)).limit(int(size))
        for row in rows:
            row['obj_id'] = str(row['_id'])
            del row['_id']
            ret_dict['data'].append(row)
        return common_return(resp=ret_dict)
    
    def add_role(self):
        req_dict = self.request.json or {}
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['name', 'desc']
        )
        if check_status:
            req_dict['role_id'] = str(uuid.uuid1())
            self.db_mongo.get_collection('roles_info').insert_one(req_dict)
            return common_return(msg="角色新增成功")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')

    def delete_role(self):
        role_id = self.request.args.get('role_id')
        if role_id:
            self.db_mongo.get_collection('roles_info').delete_one({'role_id': role_id})
            return common_return(msg='角色删除成功')
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')

    def edit_role(self):
        req_dict = self.request.json or {}
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['role_id', 'name', 'desc']
        )
        if check_status:
            role_id = req_dict['role_id']
            del req_dict['role_id']
            self.db_mongo.get_collection('roles_info').update_one(
                {'role_id': role_id},
                {'$set': req_dict}
            )
            return common_return(msg='角色修改成功')
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')
    
    def get_menu_list_tree(self):
        depth_num_rows = list(self.db_mongo.get_collection('menus_info').aggregate([
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
                {'depth': (max_depth - depth_index)},
                {'_id': 0, 'menu_id': 1, 'parent_id': 1, 'name': 1}).sort('order', 1)
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
    
    def role_relate_menus(self):
        req_dict = self.request.json or {}
        check_status, req_dict = CheckAndHandleRequestParam(req_dict).main_contraller(
            must_need_keys=['role_id', 'menu_ids', 'menu_leaf_keys']
        )
        if check_status:
            self.db_mongo.get_collection('roles_info').update_one(
                {'role_id': req_dict['role_id']},
                {'$set': {'menu_ids': req_dict['menu_ids'], 'menu_leaf_keys': req_dict['menu_leaf_keys']}}
            )
            return common_return(msg="角色关联菜单成功")
        else:
            return common_return(code=H_R_C.PARAMETER_ERROR, isSuccess=False, msg='请求参数异常')
    
    def get_related_menu_ids(self):
        role_id = self.request.args.get('role_id')
        role_info = self.db_mongo.get_collection('roles_info').find_one({'role_id': role_id})
        menu_leaf_keys = []
        if role_info and 'menu_leaf_keys' in role_info:
            menu_leaf_keys = role_info['menu_leaf_keys']
        return common_return(resp=menu_leaf_keys)
