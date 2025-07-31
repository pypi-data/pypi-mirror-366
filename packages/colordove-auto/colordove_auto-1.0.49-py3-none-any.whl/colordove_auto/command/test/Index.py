# -*- coding: utf-8 -*-
import time
import json
import gc
import threading
import traceback
import sys
import os
import tempfile
import subprocess
from pathlib import Path
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.request.common.TaskRequest import TaskRequest
from exceptions import TaskParamsException

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
taskRequest = TaskRequest()

class Index:
    def __init__(self):
        super().__init__()

    def index(self, options):
        '''
        @Desc    : 测试
        @command : python run.py test -m Index -a index debug=1
        @Author  : 钟水洲
        @Time    : 2024/06/04 15:55:13
        '''
        # 记录开始时间
        start_time = time.time()

        driver = None
        mitmdump = None
        tmpdir = None
        stop_event = None
        monitor_thread = None

        try:
            options = {"task_job":"command.tiktok.order.service.OrderService@getOrderList","params":"{\"type_id\":5,\"task_id\":53422,\"shop_global_id\":3,\"shop_id\":12}"}

            # 关闭超时进程
            chrome.closeTimeoutProcess()

            # 默认参数
            default_params = options["params"]
            if isinstance(default_params, str):
                default_params = json.loads(default_params)

            # 获取任务参数
            res = taskRequest.getTask(default_params)
            if res['status'] != 1:
                raise TaskParamsException(res['message'])
            task_data = res['data']

            # 任务参数
            task_params = task_data['params']

            # 获取店铺详情
            res = shopRequest.getDetail(default_params)
            if res['status'] != 1:
                print("获取店铺详情", res['message'])
                return common.back(0, res['message'])
            shop_data = res['data']

            # 合并参数
            params = {**default_params, **task_params}
            options['params'] = params

            # 启动mitmproxy
            listen_port = common.get_free_port()
            mitmdump = chrome.run_mitmproxy(shop_data, listen_port)
            print(f"✅ mitmproxy 已启动，本地监听 {listen_port}")

            # 临时用户目录
            tmpdir = tempfile.TemporaryDirectory()
            user_data_dir = tmpdir.name
            print("user_data_dir", user_data_dir)  # 临时目录路径

            # 启动驱动
            driver = chrome.start_driver(shop_data, listen_port, user_data_dir)

            # 监听新标签页
            known_handles = set(driver.window_handles)
            stop_event = threading.Event()
            monitor_thread= threading.Thread(
                target=chrome.monitorNewTabs,
                args=(driver, shop_data, known_handles, stop_event),
                daemon=True
            )
            monitor_thread.start()

            # 指纹检测
            # chrome.getFingerprint(driver)

            # 调用脚本
            common.runJob(driver, shop_data, options)

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            params['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 完成任务
            taskRequest.end(params)
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()

            # 获取完整 traceback 栈
            tb_list = traceback.extract_tb(tb)

            # 失败信息
            try:
                error_data = e.error_data()
            except Exception:
                if tb_list:
                    last_call = tb_list[-1]  # 最底层的异常点
                    file_path = last_call.filename
                    line_no = last_call.lineno
                else:
                    file_path = None
                    line_no = -1

                error_data = {
                    "error_code": "99999",
                    "error_msg": "未知异常",
                    "error_response": str(exc_obj),
                    "error_path": file_path,
                    "error_line": line_no
                }

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            error_data['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 任务ID
            error_data['task_id'] = default_params['task_id']
            print("任务失败", json.dumps(error_data, ensure_ascii=False))

            # 任务失败
            taskRequest.error(error_data)

        finally:
            # 停止监听新标签页线程
            if stop_event:
                stop_event.set()

            if monitor_thread:
                monitor_thread.join()

            # 关闭 driver
            if driver:
                driver.quit()
                time.sleep(1)

            # 关闭 mitmdump
            if mitmdump:
                mitmdump.kill()
                time.sleep(1)

            # 清理临时目录
            if tmpdir:
                tmpdir.cleanup()

            # 垃圾回收
            gc.collect()

        input("浏览器已打开，按 Enter 键退出")

    def start(self, options):
        '''
        @Desc    : 测试
        @command : python run.py test -m Index -a start debug=1
        @Author  : 钟水洲
        @Time    : 2024/06/04 15:55:13
        '''
        # 执行一个 CMD 命令
        root_dir = Path(__file__).resolve().parents[2]
        print("root_dir", root_dir)

        # 获取 main.py 的完整路径
        main_py_path = root_dir / 'main.py'
        print("main_py_path", main_py_path)

        # 执行 python main.py
        subprocess.run(['python', str(main_py_path)])