#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  authority_blueprint_manager.py
@Desc :  权限管理蓝图管理模块
'''

# The Python Standard Modules(Library) and Third Modules(Library)
from flask import request, Blueprint
# User-defined Modules
from project.modules.authority.menu_manager import MenuManager
from project.modules.authority.role_manager import RoleManager
from project.modules.authority.user_manager import UserManager

authority = Blueprint(__name__, 'authority')


# ===================== MENU ===================== #
@authority.route('/get_menus_info', methods=['POST'])
def authority_get_menus_info():
    return MenuManager(request).get_menus_info()

@authority.route('/add_menu', methods=['POST'])
def authority_add_menu():
    return MenuManager(request).add_menu()

@authority.route('/get_depth_menus', methods=['GET'])
def authority_get_depth_menus():
    return MenuManager(request).get_depth_menus()

@authority.route('/delete_menu', methods=['GET'])
def authority_delete_menu():
    return MenuManager(request).delete_menu()

@authority.route('/edit_menu', methods=['POST'])
def authority_edit_menu():
    return MenuManager(request).edit_menu()

# ===================== ROLE ===================== #
@authority.route('/get_roles_info', methods=['POST'])
def authority_get_roles_info():
    return RoleManager(request).get_roles_info()

@authority.route('/add_role', methods=['POST'])
def authority_add_role():
    return RoleManager(request).add_role()

@authority.route('/delete_role', methods=['GET'])
def authority_delete_role():
    return RoleManager(request).delete_role()

@authority.route('/edit_role', methods=['POST'])
def authority_edit_role():
    return RoleManager(request).edit_role()

@authority.route('/get_menu_list_tree', methods=['GET'])
def authority_get_menu_list_tree():
    return RoleManager(request).get_menu_list_tree()

@authority.route('/role_relate_menus', methods=['POST'])
def authority_role_relate_menus():
    return RoleManager(request).role_relate_menus()

@authority.route('/get_related_menu_ids', methods=['GET'])
def authority_get_related_menu_ids():
    return RoleManager(request).get_related_menu_ids()

# ===================== USER ===================== #
@authority.route('/get_users_info', methods=['POST'])
def authority_get_users_info():
    return UserManager(request).get_users_info()

@authority.route('/delete_user', methods=['GET'])
def authority_delete_user():
    return UserManager(request).delete_user()

@authority.route('/get_all_roles', methods=['GET'])
def authority_get_all_roles():
    return UserManager(request).get_all_roles()

@authority.route('/get_user_roles', methods=['GET'])
def authority_get_user_roles():
    return UserManager(request).get_user_roles()

@authority.route('/user_relate_roles', methods=['POST'])
def authority_user_relate_roles():
    return UserManager(request).user_relate_roles()
