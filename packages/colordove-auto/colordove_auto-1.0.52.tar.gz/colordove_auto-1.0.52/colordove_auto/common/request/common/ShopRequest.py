import json
from env import config
from common.library.Request import Request

request = Request()

class ShopRequest():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getDetail(self, data):
        '''
        @Desc    : 获取店铺详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        url = self.host + '/api/v1/post?c=shop&a=getDetail'
        res = request.post(url, data)
        return res
    
    def saveStorage(self, data):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        url = self.host + '/api/v1/post?c=shop&a=saveStorage'
        res = request.post(url, data)
        return res