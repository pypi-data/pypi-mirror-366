import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.tiktok.LogisticsApi import LogisticsApi
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.request.tiktok.OrderRequest import OrderRequest
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
logisticsApi = LogisticsApi()
shopRequest = ShopRequest()
tiktokService = TiktokService()
orderRequest = OrderRequest()
taskRequest = TaskRequest()

class LogisticsService():
    def __init__(self):
        super().__init__()

    def getPackagesList(self, driver, shop_data, options):
        '''
        @Desc    : 获取包裹列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        logisticsApi.getPackagesList(driver, options)