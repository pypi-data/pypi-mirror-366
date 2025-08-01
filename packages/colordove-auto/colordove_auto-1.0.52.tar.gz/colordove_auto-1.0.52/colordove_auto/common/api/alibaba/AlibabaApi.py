import json
import time
import re
import hashlib
import random
from urllib.parse import urlparse
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from env import config
from common.Common import Common
from common.library.Request import Request
from common.service.ExecuteService import ExecuteService
from common.request.common.TaskRequest import TaskRequest
from exceptions import TaskParamsException

request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()


class AlibabaApi():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getProductDetail(self, driver, options):
        '''
        @Desc    : 获取产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        url = options.get("url")

        # 访问订单页面
        driver.get(url)

        # 等待页面加载
        time.sleep(10)

        # 刷新页面
        driver.refresh()

        # 等待页面加载
        time.sleep(10)

        print("__INIT_DATA")
        init_data = driver.execute_script("""
            console.log("INIT_DATA:", window.__INIT_DATA);
            return window.__INIT_DATA;
        """)

        print("__GLOBAL_DATA")
        global_data = driver.execute_script("""
            console.log("GLOBAL_DATA:", window.__GLOBAL_DATA);
            return window.__GLOBAL_DATA;
        """)

        print("temp_data")
        temp_data = {
            "init_data": init_data['data'],
            "global_data": global_data,
        }

        # JSON 数据
        res = json.dumps(temp_data, ensure_ascii=False)

        # 保存数据
        options['response'] = res
        taskRequest.save(options)