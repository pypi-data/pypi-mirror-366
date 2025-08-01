# -*- coding: utf-8 -*-
import time
from env import config
from common.Common import Common
from command.alibaba.supplier.service.OrderService import OrderService

common = Common()
orderService = OrderService()

class Order:
    def __init__(self):
        super().__init__()

    def getOrderList(self, options):
        '''
        @Desc    : 获取采购订单
        @command : python run.py supplier -m Order -a getOrderList debug=1
        @Author  : 钟水洲
        @Time    : 2024/06/04 15:55:13
        '''
        orderService.getOrderList()

        input("浏览器已打开，按 Enter 键退出...")