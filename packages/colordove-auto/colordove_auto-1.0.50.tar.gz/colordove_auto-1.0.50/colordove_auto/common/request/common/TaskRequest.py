import json
from env import config
from common.library.Request import Request

request = Request()

class TaskRequest():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def getTask(self, data):
        '''
        @Desc    : 获取任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务 strat")
        url = self.host + '/api/v1/post?c=task&a=getTask'
        res = request.post(url, data)
        print("获取任务 end", res)
        return res

    def save(self, data):
        '''
        @Desc    : 保存数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存数据 strat")
        url = self.host + '/api/v1/post?c=task&a=save'
        res = request.post(url, data)
        print("保存数据 end")
        return res

    def end(self, data):
        '''
        @Desc    : 完成任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("完成任务 strat")
        url = self.host + '/api/v1/post?c=task&a=end'
        res = request.post(url, data)
        print("完成任务 end")
        return res
    
    def error(self, data):
        '''
        @Desc    : 任务异常
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("完成任务 strat")
        url = self.host + '/api/v1/post?c=task&a=error'
        res = request.post(url, data)
        print("完成任务 end")
        return res