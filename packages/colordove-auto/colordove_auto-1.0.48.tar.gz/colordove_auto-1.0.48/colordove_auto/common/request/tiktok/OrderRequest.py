import json
from env import config
from common.library.Request import Request

request = Request()

class OrderRequest():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def saveOrderList(self, data):
        '''
        @Desc    : 保存订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        url = self.host + '/api/v1/post?c=order&a=saveOrderList'
        res = request.post(url, data)
        return res