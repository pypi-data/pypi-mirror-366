import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.api.tiktok.UnionApi import UnionApi
from common.request.common.ShopRequest import ShopRequest
from common.service.TiktokService import TiktokService
from common.request.tiktok.OrderRequest import OrderRequest
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
unionApi = UnionApi()
shopRequest = ShopRequest()
tiktokService = TiktokService()
orderRequest = OrderRequest()
taskRequest = TaskRequest()

class UnionService():
    def __init__(self):
        super().__init__()

    def getCreatorOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取联盟达人订单
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取联盟达人订单
        unionApi.getCreatorOrderList(driver, options)

    def getOpenCollaboration(self, driver, shop_data, options):
        '''
        @Desc    : 获取联盟公开合作
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 登录
        res = tiktokService.login(driver, shop_data, options)
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])

        # 获取联盟达人订单
        unionApi.getOpenCollaboration(driver, options)