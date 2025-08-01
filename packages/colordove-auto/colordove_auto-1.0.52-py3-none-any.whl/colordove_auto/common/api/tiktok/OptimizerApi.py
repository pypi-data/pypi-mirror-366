import json
import time
import uuid
from urllib.parse import urlparse
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

class OptimizerApi():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getOptimizerTitle(self, driver, options):
        '''
        @Desc    : 获取优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 获取待优化产品
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/optimize/product/multi_get"

        params = {
            "oec_seller_id": oec_seller_id,
            "issue_types": "2",
            "page_limit": "20",
            "get_total_product_count": "true",
        }

        request_id = str(uuid.uuid4())
        list_count = 0
        page_number = 1
        page_size = 20
        page_cursor = ""

        while True:
            if page_cursor:
                params["page_cursor"] = page_cursor
            params["page_limit"] = str(page_size)

            res = executeService.request(driver=driver, url=url, params=params, method="GET")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_product_count", 0)
            temp_list = temp_data.get("products", [])
            page_cursor = temp_data.get("next_page_cursor", '')

            if page_number > 1 and not temp_list:
                break

            temp_count = len(temp_list)

            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = page_number
            options['page_size'] = page_size
            options['list_count'] = temp_count
            options['total_count'] = total_count
            options['response'] = res
            taskRequest.save(options)

            list_count += temp_count
            if list_count >= total_count:
                break

            # 下一页
            page_number += 1

            # 休息一会
            time.sleep(0.3)

    def optimizerTitle(self, driver, options):
        '''
        @Desc    : 优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        products_optimized = options.get("response").get("products_optimized")
        session_id = options.get("response").get("session_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 提交优化
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/optimize/multi_edit"

        params = {
            "oec_seller_id": oec_seller_id,
        }

        data = {
            "products_optimized": products_optimized,
            "source_page": 5,
            "session_id": session_id
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="PUT")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)
