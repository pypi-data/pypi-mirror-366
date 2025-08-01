import os
import sys
import subprocess

class Init():
    def __init__(self):
        super().__init__()

        print(sys.executable)

    def setEnv(self):
        '''
        @Desc    : 设置环境
        @Author  : 钟水洲
        @Time    : 2025/07/29 18:06:50
        '''
        # 获取根目录
        root_dir = self.get_root_dir()

        if root_dir:
            print(f"colordove_auto 的项目路径: {root_dir}")

            # 设置 PYTHONPATH 环境变量为该路径
            os.environ["PYTHONPATH"] = root_dir

            # 确保模块路径更新
            sys.path.insert(0, os.environ["PYTHONPATH"])

            # 打印当前模块搜索路径
            print("当前模块搜索路径:")
            for path in sys.path:
                print(path)
        else:
            print("未找到 colordove-auto 包的安装路径")

    def get_root_dir(self):
        '''
        @Desc    : 初始化加载模块
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        package_path = ""
        # 使用 pip show 获取 colordove-auto 的安装路径
        result = subprocess.run([sys.executable, "-m", "pip", "show", "colordove-auto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Location:"):
                    # 提取安装路径
                    package_path = line.split(":", 1)[1].strip()
                    break

        if not package_path:
            print("未找到 colordove-auto 包的安装路径")
            return ''

        root_dir = os.path.join(package_path, "colordove_auto")

        return root_dir

# 设置环境
Init().setEnv()

import threading
import pytz
import chardet
import imaplib
import logging
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from email.header import decode_header
from bs4 import BeautifulSoup

from common.library.Queue import Queue
from common.library.Logger import Logger
from common.library.Env import Env

class Main():
    def __init__(self):
        super().__init__()

        # 初始化加载模块
        self.init_module()

        # 运行
        self.run()

    def run(self):
        '''
        @Desc    : 运行
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 日志
        Logger()

        # 环境
        Env()

        # 消费队列
        Queue()

    def init_module(self):
        '''
        @Desc    : 初始化加载模块
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 调用这些模块以防打包丢失
        _ = threading.Thread
        _ = uc.Chrome
        _ = webdriver.Chrome
        _ = WebDriverWait
        _ = By
        _ = EC.title_is
        _ = decode_header
        _ = BeautifulSoup
        _ = pytz.timezone
        _ = chardet.detect
        _ = imaplib.IMAP4

def main():
    try:
        # 启动程序
        Main()
    except Exception as e:
        print(f"error {e}")
        logging.error(f"程序发生错误: {e}", exc_info=True)

if __name__ == '__main__':
    main()