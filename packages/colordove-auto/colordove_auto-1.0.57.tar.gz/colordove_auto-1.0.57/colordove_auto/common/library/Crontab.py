import json
import requests
import logging
import time
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

class Crontab():
    def __init__(self):
        super().__init__()

        # 判断系统
        if sys.platform.startswith('linux'):
            colordove_auto_path = self.get_colordove_auto_path()  # 获取 colordove_auto 命令的路径
            cron_command = self.get_cron_command(colordove_auto_path)  # 创建 cron 命令
            self.add_cron_task(cron_command)  # 添加定时任务

    # 获取 colordove_auto 的完整路径
    def get_colordove_auto_path(self):
        try:
            colordove_auto_path = subprocess.check_output("which colordove_auto", shell=True).decode().strip()
            if not colordove_auto_path:
                raise ValueError("colordove_auto not found.")
            return colordove_auto_path
        except subprocess.CalledProcessError:
            print("Error: Unable to find colordove_auto. Please ensure it is installed and available in the PATH.")
            exit(1)

    # 定义 cron 任务的命令
    def get_cron_command(self, colordove_auto_path):
        return f'* * * * * {colordove_auto_path} start > /dev/null 2>&1'

    # 获取当前 crontab 内容
    def get_current_crontab(self):
        try:
            # 使用 `crontab -l` 命令获取当前 crontab 列表
            crontab_content = subprocess.check_output("crontab -l", shell=True, stderr=subprocess.PIPE).decode()
        except subprocess.CalledProcessError:
            # 如果 crontab 没有任何任务，返回空字符串
            crontab_content = ""
        return crontab_content

    # 添加定时任务到 crontab
    def add_cron_task(self, cron_command):
        # 获取当前 crontab 内容
        current_crontab = self.get_current_crontab()

        # 检查任务是否已存在
        if cron_command not in current_crontab:
            # 如果没有找到任务，则将新的 cron 任务添加到 crontab
            updated_crontab = current_crontab + '\n' + cron_command

            # 将更新后的 crontab 内容写回系统
            try:
                # 使用 `echo` 将新任务写入 crontab
                subprocess.run(f'echo "{updated_crontab}" | crontab -', shell=True, check=True)
                print("定时任务已成功添加！")
            except subprocess.CalledProcessError as e:
                print(f"添加定时任务失败: {e}")
        else:
            print("定时任务已存在，跳过添加！")