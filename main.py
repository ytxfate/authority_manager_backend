#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  main.py
@Desc :  项目启动模块
'''

# The Python Standard Modules(Library) and Third Modules(Library)

# User-defined Modules
from app import app
from global_config import app_run_config, isFormalSystem


if __name__ == '__main__':
    debug_value = app_run_config['DEBUG']
    # 判断是否为生产系统，若不是则开启 debug 功能
    if isFormalSystem:
        debug_value = False
    app.run(
        host=app_run_config['HOST'],
        port=app_run_config['PORT'],
        debug=debug_value
    )
