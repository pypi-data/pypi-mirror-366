import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.api.tiktok.OptimizerApi import OptimizerApi
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
tiktokService = TiktokService()
optimizerApi = OptimizerApi()
taskRequest = TaskRequest()

class OptimizerService():
    def __init__(self):
        super().__init__()

    def getOptimizerTitle(self, driver, shop_data, options):
        '''
        @Desc    : 获取优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        optimizerApi.getOptimizerTitle(driver, options)

    def optimizerTitle(self, driver, shop_data, options):
        '''
        @Desc    : 优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        optimizerApi.optimizerTitle(driver, options)