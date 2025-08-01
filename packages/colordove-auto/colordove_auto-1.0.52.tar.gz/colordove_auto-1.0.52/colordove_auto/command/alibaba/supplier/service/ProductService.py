import json
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.AlibabaService import AlibabaService
from common.api.alibaba.AlibabaApi import AlibabaApi
from common.request.common.TaskRequest import TaskRequest

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
alibabaService = AlibabaService()
alibabaApi = AlibabaApi()
taskRequest = TaskRequest()

class ProductService():
    def __init__(self):
        super().__init__()

    def getProductDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取产品
        alibabaApi.getProductDetail(driver, options)