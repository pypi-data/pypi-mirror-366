import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.api.tiktok.ShopApi import ShopApi
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
tiktokService = TiktokService()
shopApi = ShopApi()
taskRequest = TaskRequest()

class ShopService():
    def __init__(self):
        super().__init__()

    def getSellerInfo(self, driver, shop_data, options):
        '''
        @Desc    : 获取商家信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取商家信息
        shopApi.getSellerInfo(driver, options)

    def getWarehouseList(self, driver, shop_data, options):
        '''
        @Desc    : 获取仓库信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取商家信息
        shopApi.getWarehouseList(driver, options)

    def getShopList(self, driver, shop_data, options):
        '''
        @Desc    : 获取店铺
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取商家信息
        shopApi.getShopList(driver, options)
