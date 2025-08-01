import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.tiktok.BillApi import BillApi
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.request.tiktok.OrderRequest import OrderRequest
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
billApi = BillApi()
shopRequest = ShopRequest()
tiktokService = TiktokService()
orderRequest = OrderRequest()
taskRequest = TaskRequest()

class BillService():
    def __init__(self):
        super().__init__()

    def getSettlementOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取结算订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取结算订单列表
        billApi.getSettlementOrderList(driver, options)

    def getSettlementOrderDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取订单结算明细
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取订单结算明细
        billApi.getSettlementOrderDetail(driver, options)