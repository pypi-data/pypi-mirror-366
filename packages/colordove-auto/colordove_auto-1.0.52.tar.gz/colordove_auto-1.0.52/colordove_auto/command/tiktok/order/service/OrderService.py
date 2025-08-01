import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.tiktok.OrderApi import OrderApi
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.request.tiktok.OrderRequest import OrderRequest
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
orderApi = OrderApi()
shopRequest = ShopRequest()
tiktokService = TiktokService()
orderRequest = OrderRequest()
taskRequest = TaskRequest()

class OrderService():
    def __init__(self):
        super().__init__()

    def getOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        orderApi.getOrderList(driver, options)

    def getOrderDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取店铺订单详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        orderApi.getOrderDetail(driver, options)

    def getOrderReturnList(self, driver, shop_data, options):
        '''
        @Desc    : 获取退货退款
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 优化标题
        orderApi.getOrderReturnList(driver, options)