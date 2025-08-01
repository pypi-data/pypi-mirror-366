import json
import os
import pandas as pd
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

class OrderService():
    def __init__(self):
        super().__init__()

    def getOrderList(self):
        '''
        @Desc    : 获取采购订单
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        options = {
            "type_id": 19,
            "task_id": 5477,
            "uuid": "tdkti4w25z31eyib2kkmt4jt137cfc5l",
        }

        dir_path = common.resourcePath("./upload/excel/alibaba/order/")

        # 如果目录不存在，则创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        for file_name in os.listdir(dir_path):

            if file_name.endswith(".xls") or file_name.endswith(".xlsx"):
                file_path = os.path.join(dir_path, file_name)

                try:
                    # 读取 Excel 文件中的所有 sheet
                    excel_data = pd.read_excel(file_path, sheet_name=None, dtype=str)

                    for sheet_name, df in excel_data.items():
                        df = df.dropna(how='all')  # 跳过整行为空

                        data = df.fillna("").to_dict(orient='records')
                        data = json.dumps(data, ensure_ascii=False)

                        options['response'] = data
                        taskRequest.save(options)

                    # 删除文件
                    os.remove(file_path)

                except Exception as e:
                    print(f"❌ 读取文件失败: {file_name}, 错误: {str(e)}")