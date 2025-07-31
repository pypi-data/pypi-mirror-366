# -*- coding: utf-8 -*-

import sys
import subprocess
import sys
from pathlib import Path
from common.Common import Common

common = Common()

def main():
    '''
    @Desc    : 入口
    @Author  : 钟水洲
    @Time    : 2024/05/31 10:01:57
    '''
    args = common.handleArgs(sys.argv)

    # 解析命令行参数
    module_name = f"command.{args.f}.{args.m}"

    class_name = args.m.capitalize()
    method_name = args.a

    # 导入模块
    __import__(module_name)

    # 获取类和方法
    module = sys.modules[module_name]
    Bot = getattr(module, class_name)()
    method = getattr(Bot, method_name)

    # 调用方法
    method(args.options)

if __name__ == "__main__":
    main()